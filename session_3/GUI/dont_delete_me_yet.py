#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2025 SensorStim Neurotechnology GmbH <support@capture2go.com>
#
# SPDX-License-Identifier: MIT
#
# Real-time GUI for the Capture2Go sensor - STUDENT VERSION
# Cross-platform (Windows / macOS / Linux).
# Packaged as a standalone executable (.exe / .app).
# A connection dialog is shown at startup so no terminal arguments are needed.
# On close, all recorded data is exported as CSV to:
#     <Documents>/Capture2Go_Data/<Name>_<ID>_<timestamp>/data.csv
#
# Permission error on Linux?  Run once in a terminal:
#   sudo usermod -aG dialout $USER
# then log out and back in (or reboot).  After that the sensor will be found.

import asyncio
import csv
import datetime
import os
import queue
import subprocess
import sys
import threading

import numpy as np
import tkinter as tk
from tkinter import ttk, messagebox

import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.animation import FuncAnimation

import capture2go as c2g


# ──────────────────────────────────────────────────────────────────────────────
# Platform helpers
# ──────────────────────────────────────────────────────────────────────────────

IS_WINDOWS = sys.platform.startswith("win")
IS_MAC     = sys.platform == "darwin"
IS_LINUX   = sys.platform.startswith("linux")

# Monospace font that really exists on each system
if IS_MAC:
    MONO = "Menlo"
elif IS_WINDOWS:
    MONO = "Consolas"
else:
    MONO = "DejaVu Sans Mono"


# ──────────────────────────────────────────────────────────────────────────────
# Color palette  (imes logo: blue / orange / white / dark-gray)
# ──────────────────────────────────────────────────────────────────────────────

COLOR_BG          = "#EEF1F5"   # window background (light gray)
COLOR_PANEL       = "#FFFFFF"   # panels and plot backgrounds
COLOR_TEXT        = "#3C3C3B"   # main text (dark gray)
COLOR_MUTED       = "#6B6B6A"   # secondary text
COLOR_BLUE        = "#00569E"   # logo blue
COLOR_ORANGE      = "#E8822A"   # logo orange
COLOR_ORANGE_DARK = "#C96A15"   # button hover / active
COLOR_GRID        = "#D9DDE3"
COLOR_SPINE       = "#B8BEC8"
COLOR_GREEN       = "#2E7D32"   # success green

CHANNEL_COLORS = [COLOR_BLUE, COLOR_ORANGE, COLOR_TEXT]
CHANNEL_NAMES  = ["Channel 1", "Channel 2", "Channel 3"]

FONT_SIZE      = 10
TK_FONT        = (MONO, FONT_SIZE)
TK_FONT_BOLD   = (MONO, FONT_SIZE, "bold")
TICK_SIZE      = 9
LEGEND_SIZE    = 9

POLL_INTERVAL_MS = 20
PLOT_INTERVAL_MS = 40

# Anonymous signal names shown to students (no axis labels / units on purpose)
SIGNAL_NAMES = ["Signal A", "Signal B", "Signal C", "Signal D"]

# CSV export column names (matching reference_data.csv template)
CSV_COLUMNS = ["time_s", "signal_1", "signal_2", "signal_3",
               "signal_4", "signal_5", "signal_6"]


# ──────────────────────────────────────────────────────────────────────────────
# Flat colored button
# macOS ignores bg/fg of tk.Button (white text on white background), so we
# build buttons from a Label, which looks the same on every platform.
# ──────────────────────────────────────────────────────────────────────────────

class FlatButton(tk.Label):
    def __init__(self, parent, text, command, bg, fg,
                 hover_bg=None, font=TK_FONT, padx=12, pady=4):
        super().__init__(parent, text=text, bg=bg, fg=fg, font=font,
                         padx=padx, pady=pady, cursor="hand2")
        self._command  = command
        self._bg       = bg
        self._hover_bg = hover_bg or bg
        self.bind("<Button-1>", self._on_click)
        self.bind("<Enter>", lambda _e: self.configure(bg=self._hover_bg))
        self.bind("<Leave>", lambda _e: self.configure(bg=self._bg))

    def _on_click(self, _event):
        if self._command:
            self._command()


# ──────────────────────────────────────────────────────────────────────────────
# BLE/USB streaming thread
# ──────────────────────────────────────────────────────────────────────────────

async def stream_sensor(device_name: str, data_queue: queue.Queue,
                        stop_event: threading.Event):
    """Connect to the sensor and push packets into the queue."""
    try:
        sensor, = await c2g.connect([device_name])
        await sensor.init(setTime=True, abortStreaming=True)
        await sensor.send(c2g.pkg.CmdSetMeasurementMode(
            fullPackedMode=c2g.pkg.SamplingMode.MODE_200HZ,
            statusMode=1,
        ))
        await sensor.send(c2g.pkg.CmdStartStreaming())
        try:
            async for package in sensor:
                if stop_event.is_set():
                    break
                data_queue.put(package)
        except asyncio.CancelledError:
            pass
        finally:
            await sensor.send(c2g.pkg.CmdStopStreaming())
            await sensor.disconnect()
    except Exception as exc:
        data_queue.put(exc)


def run_stream_thread(device_name: str, data_queue: queue.Queue,
                      stop_event: threading.Event):
    loop = asyncio.new_event_loop()
    loop.run_until_complete(stream_sensor(device_name, data_queue, stop_event))
    loop.close()


# ──────────────────────────────────────────────────────────────────────────────
# Student info dialog  (shown before the connection dialog)
# ──────────────────────────────────────────────────────────────────────────────

class StudentInfoDialog(tk.Toplevel):
    """
    Modal dialog that collects the student's name and ID before connecting.
    Sets self.student_name and self.student_id, or both None if cancelled.
    """

    def __init__(self, parent: tk.Tk):
        super().__init__(parent)
        self.title("Student Information")
        self.resizable(False, False)
        self.configure(bg=COLOR_BG)
        self.student_name: str | None = None
        self.student_id:   str | None = None

        self._build()
        self.protocol("WM_DELETE_WINDOW", self._cancel)

        # Center on screen, then make modal (after the window is visible)
        self.update_idletasks()
        x = (self.winfo_screenwidth()  - self.winfo_reqwidth())  // 2
        y = (self.winfo_screenheight() - self.winfo_reqheight()) // 2
        self.geometry(f"+{x}+{y}")
        self.lift()
        self.focus_force()
        self.after(100, self._safe_grab)

    def _safe_grab(self):
        try:
            self.grab_set()
        except tk.TclError:
            pass

    def _build(self):
        # ── Header ────────────────────────────────────────────────────────────
        tk.Label(
            self, text="Capture2Go  ·  Student Info",
            bg=COLOR_BLUE, fg="#FFFFFF",
            font=(MONO, 13, "bold"), pady=8
        ).pack(fill=tk.X)

        body = tk.Frame(self, bg=COLOR_BG, padx=24, pady=16)
        body.pack(fill=tk.BOTH, expand=True)

        # ── Name ──────────────────────────────────────────────────────────────
        tk.Label(body, text="Full name:", bg=COLOR_BG,
                 fg=COLOR_TEXT, font=TK_FONT_BOLD).grid(
            row=0, column=0, sticky="w", pady=(0, 2))

        self._name_entry = tk.Entry(
            body, font=TK_FONT, width=32,
            bg=COLOR_PANEL, fg=COLOR_TEXT,
            insertbackground=COLOR_BLUE,
            relief=tk.FLAT, bd=4
        )
        self._name_entry.grid(row=1, column=0, sticky="ew", pady=(0, 12))
        self._name_entry.focus_set()

        # ── Matrikel / Student ID ─────────────────────────────────────────────
        tk.Label(body, text="Matrikel-Nr. / Student ID:", bg=COLOR_BG,
                 fg=COLOR_TEXT, font=TK_FONT_BOLD).grid(
            row=2, column=0, sticky="w", pady=(0, 2))

        self._id_entry = tk.Entry(
            body, font=TK_FONT, width=32,
            bg=COLOR_PANEL, fg=COLOR_TEXT,
            insertbackground=COLOR_BLUE,
            relief=tk.FLAT, bd=4
        )
        self._id_entry.grid(row=3, column=0, sticky="ew", pady=(0, 16))

        # ── Buttons ───────────────────────────────────────────────────────────
        btn_frame = tk.Frame(body, bg=COLOR_BG)
        btn_frame.grid(row=4, column=0, sticky="e")

        FlatButton(
            btn_frame, text="Cancel", command=self._cancel,
            bg=COLOR_PANEL, fg=COLOR_MUTED, hover_bg="#E3E7ED",
            font=TK_FONT
        ).pack(side=tk.LEFT, padx=(0, 8))

        FlatButton(
            btn_frame, text="  Continue  ", command=self._confirm,
            bg=COLOR_ORANGE, fg="#FFFFFF", hover_bg=COLOR_ORANGE_DARK,
            font=TK_FONT_BOLD
        ).pack(side=tk.LEFT)

        # Allow Enter key to confirm
        self.bind("<Return>", lambda _: self._confirm())

    def _confirm(self):
        name = self._name_entry.get().strip()
        sid  = self._id_entry.get().strip()
        if not name:
            messagebox.showwarning(
                "Missing name",
                "Please enter your full name.",
                parent=self
            )
            return
        if not sid:
            messagebox.showwarning(
                "Missing student ID",
                "Please enter your Matrikel-Nr. / student ID.",
                parent=self
            )
            return
        self.student_name = name
        self.student_id   = sid
        self.destroy()

    def _cancel(self):
        self.student_name = None
        self.student_id   = None
        self.destroy()


# ──────────────────────────────────────────────────────────────────────────────
# Connection dialog  (shown before the dashboard)
# ──────────────────────────────────────────────────────────────────────────────

class ConnectionDialog(tk.Toplevel):
    """
    Modal dialog that lets the user choose USB or BLE and type the device name.
    Sets self.result to the chosen device name, or None if cancelled.
    """

    def __init__(self, parent: tk.Misc):
        super().__init__(parent)
        self.title("Connect to sensor")
        self.resizable(False, False)
        self.configure(bg=COLOR_BG)
        self.result: str | None = None

        self._build()
        self.protocol("WM_DELETE_WINDOW", self._cancel)

        # Center on screen, then make modal (after the window is visible)
        self.update_idletasks()
        x = (self.winfo_screenwidth()  - self.winfo_reqwidth())  // 2
        y = (self.winfo_screenheight() - self.winfo_reqheight()) // 2
        self.geometry(f"+{x}+{y}")
        self.lift()
        self.focus_force()
        self.after(100, self._safe_grab)

    def _safe_grab(self):
        try:
            self.grab_set()
        except tk.TclError:
            pass

    def _build(self):
        # ── Header ────────────────────────────────────────────────────────────
        tk.Label(
            self, text="Capture2Go  ·  Connect",
            bg=COLOR_BLUE, fg="#FFFFFF",
            font=(MONO, 13, "bold"), pady=8
        ).pack(fill=tk.X)

        body = tk.Frame(self, bg=COLOR_BG, padx=24, pady=16)
        body.pack(fill=tk.BOTH, expand=True)

        # ── Connection type ───────────────────────────────────────────────────
        tk.Label(body, text="Connection type:", bg=COLOR_BG,
                 fg=COLOR_TEXT, font=TK_FONT_BOLD).grid(
            row=0, column=0, sticky="w", pady=(0, 4))

        self._conn_var = tk.StringVar(value="usb")
        frame_radio = tk.Frame(body, bg=COLOR_BG)
        frame_radio.grid(row=1, column=0, columnspan=2, sticky="w", pady=(0, 12))

        tk.Radiobutton(
            frame_radio, text="USB  (plug-in cable)",
            variable=self._conn_var, value="usb",
            bg=COLOR_BG, fg=COLOR_TEXT, selectcolor=COLOR_PANEL,
            activebackground=COLOR_BG, font=TK_FONT,
            command=self._on_conn_type
        ).pack(side=tk.LEFT, padx=(0, 16))

        tk.Radiobutton(
            frame_radio, text="Bluetooth (BLE)",
            variable=self._conn_var, value="ble",
            bg=COLOR_BG, fg=COLOR_TEXT, selectcolor=COLOR_PANEL,
            activebackground=COLOR_BG, font=TK_FONT,
            command=self._on_conn_type
        ).pack(side=tk.LEFT)

        # ── Device name (BLE only) ────────────────────────────────────────────
        self._ble_frame = tk.Frame(body, bg=COLOR_BG)
        self._ble_frame.grid(row=2, column=0, columnspan=2, sticky="ew", pady=(0, 12))

        tk.Label(self._ble_frame, text="Device name (e.g. IMU_ab1234):",
                 bg=COLOR_BG, fg=COLOR_TEXT, font=TK_FONT).pack(anchor="w")
        self._ble_entry = tk.Entry(
            self._ble_frame, font=TK_FONT, width=28,
            bg=COLOR_PANEL, fg=COLOR_TEXT,
            insertbackground=COLOR_BLUE,
            relief=tk.FLAT, bd=4
        )
        self._ble_entry.pack(fill=tk.X, pady=(4, 0))
        self._ble_frame.grid_remove()   # hidden by default (USB selected)

        # ── Linux note (dialout group) – only shown on Linux ──────────────────
        row_btn = 4
        if IS_LINUX:
            note_frame = tk.Frame(body, bg="#FFF8E7", relief=tk.FLAT, bd=0)
            note_frame.grid(row=3, column=0, columnspan=2, sticky="ew", pady=(0, 12))

            tk.Label(
                note_frame,
                text="⚠  Linux users – sensor not found?",
                bg="#FFF8E7", fg=COLOR_ORANGE_DARK,
                font=TK_FONT_BOLD, anchor="w", padx=8, pady=4
            ).pack(fill=tk.X)

            tk.Label(
                note_frame,
                text=(
                    "Run this once in a terminal, then reboot:\n"
                    "   sudo usermod -aG dialout $USER"
                ),
                bg="#FFF8E7", fg=COLOR_TEXT,
                font=(MONO, FONT_SIZE - 1),
                justify=tk.LEFT, anchor="w", padx=8, pady=6
            ).pack(fill=tk.X)

        # ── Buttons ───────────────────────────────────────────────────────────
        btn_frame = tk.Frame(body, bg=COLOR_BG)
        btn_frame.grid(row=row_btn, column=0, columnspan=2, sticky="e")

        FlatButton(
            btn_frame, text="Cancel", command=self._cancel,
            bg=COLOR_PANEL, fg=COLOR_MUTED, hover_bg="#E3E7ED",
            font=TK_FONT
        ).pack(side=tk.LEFT, padx=(0, 8))

        FlatButton(
            btn_frame, text="  Connect  ", command=self._connect,
            bg=COLOR_ORANGE, fg="#FFFFFF", hover_bg=COLOR_ORANGE_DARK,
            font=TK_FONT_BOLD
        ).pack(side=tk.LEFT)

        self.bind("<Return>", lambda _: self._connect())

    def _on_conn_type(self):
        if self._conn_var.get() == "ble":
            self._ble_frame.grid()
        else:
            self._ble_frame.grid_remove()

    def _connect(self):
        if self._conn_var.get() == "usb":
            self.result = "usb"
        else:
            name = self._ble_entry.get().strip()
            if not name:
                messagebox.showwarning(
                    "Missing device name",
                    "Please enter the BLE device name (e.g. IMU_ab1234).",
                    parent=self
                )
                return
            self.result = name
        self.destroy()

    def _cancel(self):
        self.result = None
        self.destroy()


# ──────────────────────────────────────────────────────────────────────────────
# Data export helpers
# ──────────────────────────────────────────────────────────────────────────────

def get_export_root() -> str:
    """
    Folder where all sessions are saved:  <Documents>/Capture2Go_Data
    Falls back to the home folder if there is no Documents folder.
    This works for .exe / .app / plain python alike (a .app bundle is not a
    good place to write files, and some folders are read-only).
    """
    home = os.path.expanduser("~")
    docs = os.path.join(home, "Documents")
    base = docs if os.path.isdir(docs) else home
    return os.path.join(base, "Capture2Go_Data")


def open_folder(path: str):
    """Open a folder in the file explorer (Windows / macOS / Linux)."""
    try:
        if IS_WINDOWS:
            os.startfile(path)                      # type: ignore[attr-defined]
        elif IS_MAC:
            subprocess.Popen(["open", path])
        else:
            subprocess.Popen(["xdg-open", path])
    except Exception:
        pass


def export_data(student_name: str, student_id: str,
                records: list[tuple]) -> str:
    """
    Write collected sensor data to a CSV file inside a named export folder.

    Folder structure:
        <Documents>/Capture2Go_Data/<StudentName>_<MatrikelNr>_<YYYYMMDD_HHMMSS>/
            data.csv

    The CSV follows the reference_data.csv template:
        time_s, signal_1, signal_2, signal_3, signal_4, signal_5, signal_6

    Signals exported:
        signal_1 .. signal_3  →  accelerometer  x, y, z  (m/s²)
        signal_4 .. signal_6  →  gyroscope       x, y, z  (deg/s)

    Returns the path of the created folder.
    """
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    # Sanitize name/id for use as folder name
    safe_name = "".join(c if c.isalnum() or c in "-_" else "_"
                        for c in student_name.replace(" ", "_"))
    safe_id   = "".join(c if c.isalnum() or c in "-_" else "_"
                        for c in student_id)
    folder_name = f"{safe_name}_{safe_id}_{timestamp}"

    export_dir = os.path.join(get_export_root(), folder_name)
    os.makedirs(export_dir, exist_ok=True)

    csv_path = os.path.join(export_dir, "data.csv")
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(CSV_COLUMNS)
        for row in records:
            writer.writerow([f"{v:.4f}" for v in row])

    return export_dir


# ──────────────────────────────────────────────────────────────────────────────
# Main dashboard window
# ──────────────────────────────────────────────────────────────────────────────

class SensorDashboard(tk.Tk):
    N_SAMPLES   = 800
    SAMPLE_RATE = 200.0

    def __init__(self, device_name: str,
                 student_name: str, student_id: str):
        super().__init__()
        self.device_name  = device_name
        self.student_name = student_name
        self.student_id   = student_id

        self.title(f"Capture2Go  ·  {device_name}  ·  {student_name}")
        self.configure(bg=COLOR_BG)
        self.protocol("WM_DELETE_WINDOW", self._on_close)

        self._fig_dpi = max(72.0, 72.0 * float(self.tk.call("tk", "scaling")))

        self._queue: queue.Queue = queue.Queue()
        self._stop_event = threading.Event()

        self._t       = np.arange(-self.N_SAMPLES, 0, dtype=float) / self.SAMPLE_RATE
        self._buffers = [np.full((self.N_SAMPLES, 3), np.nan) for _ in SIGNAL_NAMES]
        self._lines:  list = []
        self._pkt_count = 0

        # ── Full recording storage ─────────────────────────────────────────────
        # Each entry: (time_s, acc_x, acc_y, acc_z, gyr_x, gyr_y, gyr_z)
        self._records: list[tuple] = []
        self._t_elapsed = 0.0   # running timestamp counter (seconds)

        self._build_ui()
        self._start_stream()
        self._anim = FuncAnimation(
            self._fig, self._update_plot,
            interval=PLOT_INTERVAL_MS, blit=True, cache_frame_data=False
        )
        self._poll_queue()

    # ── UI ────────────────────────────────────────────────────────────────────

    def _build_ui(self):
        # Header
        tk.Label(
            self, text="Capture2Go  ·  Sensor Dashboard",
            bg=COLOR_BLUE, fg="#FFFFFF",
            font=(MONO, 14, "bold"), pady=8
        ).pack(side=tk.TOP, fill=tk.X)

        # Student info banner
        info_banner = tk.Frame(self, bg=COLOR_PANEL, pady=4)
        info_banner.pack(side=tk.TOP, fill=tk.X, padx=8, pady=(4, 0))
        tk.Label(
            info_banner,
            text=f"🎓  {self.student_name}  ·  ID: {self.student_id}",
            bg=COLOR_PANEL, fg=COLOR_BLUE,
            font=TK_FONT_BOLD
        ).pack(side=tk.LEFT, padx=8)

        self._rec_var = tk.StringVar(value="⏺  Recording: 0 samples")
        tk.Label(
            info_banner, textvariable=self._rec_var,
            bg=COLOR_PANEL, fg=COLOR_MUTED,
            font=TK_FONT
        ).pack(side=tk.RIGHT, padx=8)

        main = tk.Frame(self, bg=COLOR_BG)
        main.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)

        # ── Left: data table ──────────────────────────────────────────────────
        left = tk.Frame(main, bg=COLOR_PANEL, relief=tk.FLAT, bd=0)
        left.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 6))

        tk.Label(
            left, text="📡  Real-time data",
            bg=COLOR_PANEL, fg=COLOR_BLUE,
            font=(MONO, FONT_SIZE + 1, "bold"), pady=6
        ).pack(fill=tk.X, padx=8)

        ttk.Separator(left, orient="horizontal").pack(fill=tk.X, padx=4)

        self._value_vars: list[list[tk.StringVar]] = []
        for signal_name in SIGNAL_NAMES:
            tk.Label(
                left, text=f"── {signal_name} ──",
                bg=COLOR_PANEL, fg=COLOR_ORANGE,
                font=TK_FONT_BOLD, anchor="w"
            ).pack(fill=tk.X, padx=8, pady=(6, 1))

            signal_vars = []
            for ch_name, ch_color in zip(CHANNEL_NAMES, CHANNEL_COLORS):
                row = tk.Frame(left, bg=COLOR_PANEL)
                row.pack(fill=tk.X, padx=8, pady=1)
                tk.Label(row, text="■", bg=COLOR_PANEL, fg=ch_color,
                         font=TK_FONT).pack(side=tk.LEFT)
                tk.Label(row, text=f" {ch_name}",
                         bg=COLOR_PANEL, fg=COLOR_MUTED,
                         font=TK_FONT, anchor="w", width=18).pack(side=tk.LEFT)
                var = tk.StringVar(value="—")
                signal_vars.append(var)
                tk.Label(row, textvariable=var,
                         bg=COLOR_PANEL, fg=COLOR_BLUE,
                         font=TK_FONT, anchor="e", width=10).pack(side=tk.RIGHT)
            self._value_vars.append(signal_vars)

        # Packet counter
        tk.Label(
            left, text="── Status ──",
            bg=COLOR_PANEL, fg=COLOR_ORANGE,
            font=TK_FONT_BOLD, anchor="w"
        ).pack(fill=tk.X, padx=8, pady=(6, 1))
        row = tk.Frame(left, bg=COLOR_PANEL)
        row.pack(fill=tk.X, padx=8, pady=1)
        tk.Label(row, text="  Packets received",
                 bg=COLOR_PANEL, fg=COLOR_MUTED,
                 font=TK_FONT, anchor="w", width=20).pack(side=tk.LEFT)
        self._pkt_var = tk.StringVar(value="—")
        tk.Label(row, textvariable=self._pkt_var,
                 bg=COLOR_PANEL, fg=COLOR_BLUE,
                 font=TK_FONT, anchor="e", width=10).pack(side=tk.RIGHT)

        ttk.Separator(left, orient="horizontal").pack(fill=tk.X, padx=4, pady=4)
        self._status_var = tk.StringVar(value="🔄  Connecting…")
        tk.Label(
            left, textvariable=self._status_var,
            bg=COLOR_PANEL, fg=COLOR_TEXT,
            font=TK_FONT, pady=4
        ).pack(fill=tk.X, padx=8)

        # Reconnect button (re-opens connection dialog)
        FlatButton(
            left, text="🔌  Reconnect", command=self._reconnect,
            bg=COLOR_PANEL, fg=COLOR_BLUE, hover_bg="#E3E7ED",
            font=TK_FONT
        ).pack(fill=tk.X, padx=8, pady=(0, 4))

        # Stop / export button
        FlatButton(
            left, text="⏹  Stop & Export data", command=self._on_close,
            bg=COLOR_ORANGE, fg="#FFFFFF", hover_bg=COLOR_ORANGE_DARK,
            font=TK_FONT_BOLD
        ).pack(fill=tk.X, padx=8, pady=(0, 8))

        # ── Right: matplotlib ─────────────────────────────────────────────────
        right = tk.Frame(main, bg=COLOR_BG)
        right.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self._fig = self._build_figure()
        canvas = FigureCanvasTkAgg(self._fig, master=right)
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        self._canvas = canvas

    def _build_figure(self) -> plt.Figure:
        fig = plt.Figure(
            figsize=(1000 / self._fig_dpi, 700 / self._fig_dpi),
            dpi=self._fig_dpi,
            tight_layout=True,
        )
        fig.patch.set_facecolor(COLOR_BG)

        axes = fig.subplots(2, 2).flatten()
        self._axes = axes

        y_limits = [(-800, 800), (-20, 20), (-100, 100), (-180, 180)]

        for ax, name, ylim in zip(axes, SIGNAL_NAMES, y_limits):
            ax.set_facecolor(COLOR_PANEL)
            for spine in ax.spines.values():
                spine.set_edgecolor(COLOR_SPINE)
            ax.tick_params(colors=COLOR_TEXT, labelsize=TICK_SIZE)
            ax.set_title(name, color=COLOR_BLUE, fontsize=FONT_SIZE,
                         fontweight="bold", fontfamily="monospace", pad=6)
            ax.set_xlim(self._t[0], self._t[-1])
            ax.set_ylim(*ylim)
            ax.grid(color=COLOR_GRID, linestyle="--", linewidth=0.6)
            ax.set_prop_cycle("color", CHANNEL_COLORS)

        for ax, buf in zip(axes, self._buffers):
            self._lines.append(ax.plot(self._t, buf, linewidth=1.4))

        axes[0].legend(
            CHANNEL_NAMES, loc="upper left", fontsize=LEGEND_SIZE,
            facecolor=COLOR_PANEL, edgecolor=COLOR_SPINE, labelcolor=COLOR_TEXT
        )
        return fig

    # ── Streaming ─────────────────────────────────────────────────────────────

    def _start_stream(self):
        self._stream_thread = threading.Thread(
            target=run_stream_thread,
            args=(self.device_name, self._queue, self._stop_event),
            daemon=True,
        )
        self._stream_thread.start()

    def _reconnect(self):
        """Stop current stream, re-open connection dialog, start new stream."""
        self._stop_event.set()
        self._stop_event = threading.Event()
        self._queue = queue.Queue()
        self._pkt_count = 0
        self._buffers = [np.full((self.N_SAMPLES, 3), np.nan) for _ in SIGNAL_NAMES]
        self._status_var.set("🔄  Connecting…")

        dialog = ConnectionDialog(self)
        self.wait_window(dialog)
        if dialog.result:
            self.device_name = dialog.result
            self.title(f"Capture2Go  ·  {self.device_name}  ·  {self.student_name}")
            self._start_stream()
        else:
            self._status_var.set("⏸  Not connected")

    # ── Queue polling ─────────────────────────────────────────────────────────

    def _poll_queue(self):
        try:
            while True:
                item = self._queue.get_nowait()
                if isinstance(item, Exception):
                    self._status_var.set(f"❌  {item}")
                    self._show_error(item)
                    break          # keep polling alive so Reconnect works
                if isinstance(item, c2g.pkg.DataFullPacked):
                    self._handle_packet(item)
        except queue.Empty:
            pass
        self.after(POLL_INTERVAL_MS, self._poll_queue)

    def _handle_packet(self, packet):
        parsed = packet.parse()
        n = len(parsed["gyr"])
        batches = [
            np.rad2deg(parsed["gyr"]),       # Signal A: gyroscope  (deg/s)
            parsed["acc"],                   # Signal B: accelerometer (m/s²)
            parsed["mag"],                   # Signal C: magnetometer
            np.rad2deg(np.array([
                c2g.utils.eulerAngles(parsed["quat9D"][i], "zxy", True)
                for i in range(n)
            ])),                             # Signal D: Euler angles (deg)
        ]

        # ── Update rolling display buffers ─────────────────────────────────
        for idx, batch in enumerate(batches):
            self._buffers[idx] = np.vstack([self._buffers[idx][n:], batch])
            for ch in range(3):
                self._value_vars[idx][ch].set(f"{batch[-1][ch]:+8.2f}")

        # ── Accumulate full recording (acc + gyr → 6-column CSV) ───────────
        # Signal B = acc (m/s²),  Signal A = gyr (deg/s)
        acc_batch = batches[1]   # shape (n, 3)
        gyr_batch = batches[0]   # shape (n, 3)
        dt = 1.0 / self.SAMPLE_RATE
        for i in range(n):
            t = self._t_elapsed
            self._records.append((
                round(t, 5),
                round(acc_batch[i, 0], 4),
                round(acc_batch[i, 1], 4),
                round(acc_batch[i, 2], 4),
                round(gyr_batch[i, 0], 4),
                round(gyr_batch[i, 1], 4),
                round(gyr_batch[i, 2], 4),
            ))
            self._t_elapsed += dt

        self._pkt_count += 1
        self._pkt_var.set(str(self._pkt_count))
        self._rec_var.set(f"⏺  Recording: {len(self._records)} samples")
        self._status_var.set("🟢  Streaming active")

    def _show_error(self, exc: Exception):
        hint = ""
        exc_str = str(exc).lower()
        if IS_LINUX and ("dialout" in exc_str or "permission" in exc_str
                         or "access" in exc_str or "serial" in exc_str):
            hint = (
                "\n\nLinux fix – run this in a terminal and reboot:\n"
                "   sudo usermod -aG dialout $USER"
            )
        elif "not found" in exc_str or "no device" in exc_str or "usb" in exc_str:
            hint = (
                "\n\nCheck that the sensor is plugged in with a data cable "
                "and switched on, then press Reconnect."
            )
        messagebox.showerror(
            "Connection error",
            f"Could not connect to '{self.device_name}':\n{exc}{hint}",
            parent=self
        )

    # ── Animation ─────────────────────────────────────────────────────────────

    def _update_plot(self, _frame):
        artists = []
        for lines, buf in zip(self._lines, self._buffers):
            for ch, line in enumerate(lines):
                line.set_ydata(buf[:, ch])
            artists += lines
        return artists

    # ── Shutdown & Export ─────────────────────────────────────────────────────

    def _on_close(self):
        """Stop streaming, export data, then close the window."""
        self._stop_event.set()

        if self._records:
            try:
                export_dir = export_data(
                    self.student_name,
                    self.student_id,
                    self._records,
                )
                open_it = messagebox.askyesno(
                    "Data exported",
                    f"✅  Session data saved successfully!\n\n"
                    f"📁  Folder:\n{export_dir}\n\n"
                    f"📄  File:  data.csv\n"
                    f"📊  Samples: {len(self._records)}\n\n"
                    f"Open the folder now?",
                    parent=self,
                )
                if open_it:
                    open_folder(export_dir)
            except Exception as exc:
                messagebox.showerror(
                    "Export error",
                    f"Could not save data:\n{exc}",
                    parent=self,
                )
        else:
            messagebox.showinfo(
                "No data recorded",
                "No sensor data was received during this session.\n"
                "Nothing was exported.",
                parent=self,
            )

        self.destroy()


# ──────────────────────────────────────────────────────────────────────────────
# Entry point
# ──────────────────────────────────────────────────────────────────────────────

def main():
    # Hidden root so dialogs appear without a main window first
    root = tk.Tk()
    root.withdraw()

    # ── Step 1: Collect student info ──────────────────────────────────────────
    student_dialog = StudentInfoDialog(root)
    root.wait_window(student_dialog)

    if not student_dialog.student_name:
        root.destroy()
        sys.exit(0)

    student_name = student_dialog.student_name
    student_id   = student_dialog.student_id

    # ── Step 2: Connect to sensor ─────────────────────────────────────────────
    conn_dialog = ConnectionDialog(root)
    root.wait_window(conn_dialog)

    if not conn_dialog.result:
        root.destroy()
        sys.exit(0)

    root.destroy()

    # ── Step 3: Run the dashboard ─────────────────────────────────────────────
    app = SensorDashboard(
        device_name=conn_dialog.result,
        student_name=student_name,
        student_id=student_id,
    )
    app.mainloop()


if __name__ == "__main__":
    main()

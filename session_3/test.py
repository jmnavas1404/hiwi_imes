"Here you can run any different test that you would like to try"

#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2025 SensorStim Neurotechnology GmbH <support@capture2go.com>
#
# SPDX-License-Identifier: MIT
#
# Real-time GUI for the Capture2Go sensor - STUDENT + TEACHER VERSION
# Cross-platform (Windows / macOS / Linux).
# Packaged as a standalone executable (.exe / .app).
#
# Two interfaces (chosen in the first dialog):
#   * Student  - anonymous signals (Signal A..D, Channel 1..3), no units.
#   * Teacher  - password protected, fully labelled signals (Gyr / Acc / Mag / Euler).
#
# Data are shown live as soon as the sensor is connected, but they are only
# RECORDED after pressing the "Iniciar toma de datos" button.
# On close, all recorded data is exported as CSV to:
#     <Documents>/Capture2Go_Data/<Name>_<ID>_<timestamp>/data.csv
#
# Permission error on Linux?  Run once in a terminal:
#   sudo usermod -aG dialout $USER
# then log out and back in (or reboot).  After that the sensor will be found.

import asyncio
import csv
import datetime
import hashlib
import hmac
import os
import queue
import subprocess
import sys
import threading
import time

import numpy as np
import tkinter as tk
from tkinter import ttk, messagebox

import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.animation import FuncAnimation
from mpl_toolkits.mplot3d.art3d import Poly3DCollection  # registers the 3D projection

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
# Teacher password  (stored only as SHA-256 hash, not as plain text)
# ──────────────────────────────────────────────────────────────────────────────

TEACHER_PASSWORD_SHA256 = (
    "ee819c21be42106408ca5de6bfac2ed224ac0dfa2039594b267686afdfcb3edb"
)


def check_teacher_password(password: str) -> bool:
    digest = hashlib.sha256(password.encode("utf-8")).hexdigest()
    return hmac.compare_digest(digest, TEACHER_PASSWORD_SHA256)


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
COLOR_GREEN_DARK  = "#256628"

CHANNEL_COLORS = [COLOR_BLUE, COLOR_ORANGE, COLOR_TEXT]
CHANNEL_NAMES  = ["Channel 1", "Channel 2", "Channel 3"]

FONT_SIZE      = 10
TK_FONT        = (MONO, FONT_SIZE)
TK_FONT_BOLD   = (MONO, FONT_SIZE, "bold")

# Plot text sizes (bigger than before)
PLOT_TITLE_SIZE  = 14
PLOT_TICK_SIZE   = 12
PLOT_LEGEND_SIZE = 11
PLOT_LABEL_SIZE  = 11

POLL_INTERVAL_MS = 20
PLOT_INTERVAL_MS = 40

# Text of the button that starts recording
BTN_START_TEXT     = "▶  Iniciar toma de datos"
BTN_RECORDING_TEXT = "⏺  Tomando datos…"

# ── Bluetooth / connection robustness ─────────────────────────────────────────
CONNECT_RETRIES   = 3      # connection attempts before giving up
CONNECT_TIMEOUT_S = 20.0   # max. seconds for ONE connection attempt
RETRY_DELAY_S     = 2.0    # pause between attempts
DATA_TIMEOUT_S    = 6.0    # no packets for this long -> connection lost

# Anonymous signal names shown to students (no axis labels / units on purpose)
SIGNAL_NAMES = ["Signal A", "Signal B", "Signal C", "Signal D"]

# CSV export column names (matching reference_data.csv template)
CSV_COLUMNS = ["time_s", "signal_1", "signal_2", "signal_3",
               "signal_4", "signal_5", "signal_6"]


# ──────────────────────────────────────────────────────────────────────────────
# Label definitions for both interfaces
# ──────────────────────────────────────────────────────────────────────────────
# Signal index: 0 = gyroscope, 1 = accelerometer, 2 = magnetometer, 3 = Euler

# Teacher version: plot titles / legends
TEACHER_PLOT_TITLES = [
    "Gyroscope [°/s]",
    "Accelerometer [m/s²]",
    "Magnetometer [µT]",
    "Euler orientation [°]",
]
TEACHER_CHANNEL_NAMES = [
    ["X", "Y", "Z"],
    ["X", "Y", "Z"],
    ["X", "Y", "Z"],
    ["Roll (z)", "Pitch (x')", "Yaw (y'')"],
]

# Teacher version: table on the left  (label, key)  -  key None = header
TEACHER_FIELDS = [
    ("── Gyroscope [°/s] ──", None),
    ("  Gyr X", "gyr_x"),
    ("  Gyr Y", "gyr_y"),
    ("  Gyr Z", "gyr_z"),
    ("── Accelerometer [m/s²] ──", None),
    ("  Acc X", "acc_x"),
    ("  Acc Y", "acc_y"),
    ("  Acc Z", "acc_z"),
    ("── Magnetometer [µT] ──", None),
    ("  Mag X", "mag_x"),
    ("  Mag Y", "mag_y"),
    ("  Mag Z", "mag_z"),
    ("── Euler orientation [°] ──", None),
    ("  Roll  (z)", "euler_z"),
    ("  Pitch (x')", "euler_x"),
    ("  Yaw  (y'')", "euler_y"),
    ("── Status ──", None),
    ("  Packets received", "pkt_count"),
]

# key -> (signal index, channel index)
TEACHER_KEY_MAP = {
    "gyr_x": (0, 0), "gyr_y": (0, 1), "gyr_z": (0, 2),
    "acc_x": (1, 0), "acc_y": (1, 1), "acc_z": (1, 2),
    "mag_x": (2, 0), "mag_y": (2, 1), "mag_z": (2, 2),
    "euler_z": (3, 0), "euler_x": (3, 1), "euler_y": (3, 2),
}


def build_student_fields():
    """Same table as the original student interface (Signal A..D, Channel 1..3)."""
    fields, key_map = [], {}
    for i, sig in enumerate(SIGNAL_NAMES):
        fields.append((f"── {sig} ──", None))
        for c, ch in enumerate(CHANNEL_NAMES):
            key = f"sig{i}_ch{c}"
            fields.append((f" {ch}", key))
            key_map[key] = (i, c)
    fields.append(("── Status ──", None))
    fields.append(("  Packets received", "pkt_count"))
    return fields, key_map


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
        self._enabled  = True
        self.bind("<Button-1>", self._on_click)
        self.bind("<Enter>", lambda _e: self.configure(bg=self._hover_bg))
        self.bind("<Leave>", lambda _e: self.configure(bg=self._bg))

    def _on_click(self, _event):
        if self._enabled and self._command:
            self._command()

    def update_style(self, text=None, bg=None, hover_bg=None, enabled=None):
        """Change text / colors / enabled state after creation."""
        if text is not None:
            self.configure(text=text)
        if bg is not None:
            self._bg = bg
            self.configure(bg=bg)
        if hover_bg is not None:
            self._hover_bg = hover_bg
        if enabled is not None:
            self._enabled = enabled
            self.configure(cursor="hand2" if enabled else "arrow")


# ──────────────────────────────────────────────────────────────────────────────
# Device name helper
# ──────────────────────────────────────────────────────────────────────────────

def normalize_device_name(raw: str) -> str:
    """
    Clean up what the user typed so BLE name matching does not fail on trivial
    differences:  ' IMU_3DBE7 ', 'imu_3dbe7', '3dbe7'  ->  'IMU_3dbe7'
    (Capture2Go device names are 'IMU_' + lowercase hex id.)
    """
    name = raw.strip().replace(" ", "")
    if name.lower() == "usb":
        return "usb"
    low = name.lower()
    if low.startswith("imu_"):
        return "IMU_" + low[4:]
    if low.startswith("imu"):
        return "IMU_" + low[3:]
    if 3 <= len(low) <= 8 and all(ch in "0123456789abcdef" for ch in low):
        return "IMU_" + low          # bare id typed without prefix
    return name                      # unknown format: leave untouched


# ──────────────────────────────────────────────────────────────────────────────
# BLE/USB streaming thread
# ──────────────────────────────────────────────────────────────────────────────

class StatusMessage(str):
    """Progress text sent from the streaming thread to the GUI."""


async def _connect_with_retries(device_name: str, data_queue: queue.Queue,
                                stop_event: threading.Event):
    """Try to connect several times (BLE scans often miss a device once)."""
    last_exc: Exception | None = None
    for attempt in range(1, CONNECT_RETRIES + 1):
        if stop_event.is_set():
            return None
        data_queue.put(StatusMessage(
            f"🔄  Connecting… (attempt {attempt}/{CONNECT_RETRIES})"))
        try:
            sensor, = await asyncio.wait_for(
                c2g.connect([device_name]), timeout=CONNECT_TIMEOUT_S)
            return sensor
        except Exception as exc:        # includes asyncio.TimeoutError
            last_exc = exc
            if isinstance(exc, (asyncio.TimeoutError, TimeoutError)):
                last_exc = TimeoutError(
                    f"Sensor '{device_name}' not found within "
                    f"{CONNECT_TIMEOUT_S:.0f} s")
        # pause before next attempt (but react quickly to a stop request)
        for _ in range(int(RETRY_DELAY_S / 0.25)):
            if stop_event.is_set():
                return None
            await asyncio.sleep(0.25)
    raise last_exc if last_exc else RuntimeError("Connection failed")


async def stream_sensor(device_name: str, data_queue: queue.Queue,
                        stop_event: threading.Event):
    """Connect to the sensor and push packets into the queue."""
    sensor = None
    pending = None
    try:
        sensor = await _connect_with_retries(device_name, data_queue, stop_event)
        if sensor is None:                       # stopped by the user
            return

        data_queue.put(StatusMessage("🔄  Initialising sensor…"))
        await sensor.init(setTime=True, abortStreaming=True)
        await sensor.send(c2g.pkg.CmdSetMeasurementMode(
            fullPackedMode=c2g.pkg.SamplingMode.MODE_200HZ,
            statusMode=1,
        ))
        await sensor.send(c2g.pkg.CmdStartStreaming())

        # Read packets WITHOUT blocking forever, so that a stop request
        # (Reconnect / close window) is noticed even if no data arrive.
        aiter = sensor.__aiter__()
        last_rx = time.monotonic()
        while not stop_event.is_set():
            if pending is None:
                pending = asyncio.ensure_future(aiter.__anext__())
            done, _ = await asyncio.wait({pending}, timeout=0.3)
            if not done:
                if time.monotonic() - last_rx > DATA_TIMEOUT_S:
                    raise TimeoutError(
                        f"No data received from '{device_name}' for "
                        f"{DATA_TIMEOUT_S:.0f} s (connection lost?)")
                continue
            task, pending = pending, None
            try:
                package = task.result()
            except StopAsyncIteration:
                break
            last_rx = time.monotonic()
            data_queue.put(package)

    except Exception as exc:
        data_queue.put(exc)

    finally:
        # ALWAYS release the sensor.  A BLE sensor that is still "connected"
        # from a previous run refuses every new connection.
        if pending is not None and not pending.done():
            pending.cancel()
        if sensor is not None:
            try:
                await sensor.send(c2g.pkg.CmdStopStreaming())
            except Exception:
                pass
            try:
                await sensor.disconnect()
            except Exception:
                pass
            await asyncio.sleep(0.5)             # let the BLE stack settle


def run_stream_thread(device_name: str, data_queue: queue.Queue,
                      stop_event: threading.Event):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(stream_sensor(device_name, data_queue, stop_event))
    except Exception as exc:
        data_queue.put(exc)
    finally:
        try:
            loop.run_until_complete(loop.shutdown_asyncgens())
        except Exception:
            pass
        loop.close()


# ──────────────────────────────────────────────────────────────────────────────
# Mode dialog  (Student / Teacher + password)  -  first dialog
# ──────────────────────────────────────────────────────────────────────────────

class ModeDialog(tk.Toplevel):
    """
    Lets the user choose the interface. Teacher mode needs the password.
    Sets self.mode to "student", "teacher" or None (cancelled).
    """

    def __init__(self, parent: tk.Tk):
        super().__init__(parent)
        self.title("Select interface")
        self.resizable(False, False)
        self.configure(bg=COLOR_BG)
        self.mode: str | None = None

        self._build()
        self.protocol("WM_DELETE_WINDOW", self._cancel)

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
        tk.Label(
            self, text="Capture2Go  ·  Interface",
            bg=COLOR_BLUE, fg="#FFFFFF",
            font=(MONO, 13, "bold"), pady=8
        ).pack(fill=tk.X)

        body = tk.Frame(self, bg=COLOR_BG, padx=24, pady=16)
        body.pack(fill=tk.BOTH, expand=True)

        tk.Label(body, text="Version:", bg=COLOR_BG,
                 fg=COLOR_TEXT, font=TK_FONT_BOLD).grid(
            row=0, column=0, sticky="w", pady=(0, 4))

        self._mode_var = tk.StringVar(value="student")
        radio_frame = tk.Frame(body, bg=COLOR_BG)
        radio_frame.grid(row=1, column=0, sticky="w", pady=(0, 12))

        for text, value in (("Student", "student"), ("Teacher", "teacher")):
            tk.Radiobutton(
                radio_frame, text=text, variable=self._mode_var, value=value,
                bg=COLOR_BG, fg=COLOR_TEXT, selectcolor=COLOR_PANEL,
                activebackground=COLOR_BG, font=TK_FONT,
                command=self._on_mode_change
            ).pack(side=tk.LEFT, padx=(0, 16))

        # Password (teacher only)
        self._pw_frame = tk.Frame(body, bg=COLOR_BG)
        self._pw_frame.grid(row=2, column=0, sticky="ew", pady=(0, 12))
        tk.Label(self._pw_frame, text="Password:", bg=COLOR_BG,
                 fg=COLOR_TEXT, font=TK_FONT).pack(anchor="w")
        self._pw_entry = tk.Entry(
            self._pw_frame, font=TK_FONT, width=28, show="•",
            bg=COLOR_PANEL, fg=COLOR_TEXT,
            insertbackground=COLOR_BLUE, relief=tk.FLAT, bd=4
        )
        self._pw_entry.pack(fill=tk.X, pady=(4, 0))
        self._pw_frame.grid_remove()

        btn_frame = tk.Frame(body, bg=COLOR_BG)
        btn_frame.grid(row=3, column=0, sticky="e")

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

        self.bind("<Return>", lambda _: self._confirm())

    def _on_mode_change(self):
        if self._mode_var.get() == "teacher":
            self._pw_frame.grid()
            self._pw_entry.focus_set()
        else:
            self._pw_frame.grid_remove()

    def _confirm(self):
        if self._mode_var.get() == "teacher":
            if not check_teacher_password(self._pw_entry.get()):
                messagebox.showwarning(
                    "Wrong password",
                    "The password is not correct.",
                    parent=self
                )
                self._pw_entry.delete(0, tk.END)
                return
            self.mode = "teacher"
        else:
            self.mode = "student"
        self.destroy()

    def _cancel(self):
        self.mode = None
        self.destroy()


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
            raw = self._ble_entry.get().strip()
            if not raw:
                messagebox.showwarning(
                    "Missing device name",
                    "Please enter the BLE device name (e.g. IMU_ab1234).",
                    parent=self
                )
                return
            # strips spaces, fixes upper/lower case, adds the 'IMU_' prefix
            self.result = normalize_device_name(raw)
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
                 student_name: str, student_id: str,
                 teacher_mode: bool = False):
        super().__init__()
        self.device_name  = device_name
        self.student_name = student_name
        self.student_id   = student_id
        self.teacher_mode = teacher_mode

        self.title(f"Capture2Go  ·  {device_name}  ·  {student_name}")
        self.configure(bg=COLOR_BG)
        self.protocol("WM_DELETE_WINDOW", self._on_close)

        self._fig_dpi = max(72.0, 72.0 * float(self.tk.call("tk", "scaling")))

        self._queue: queue.Queue = queue.Queue()
        self._stop_event = threading.Event()
        self._stream_thread: threading.Thread | None = None

        self._t       = np.arange(-self.N_SAMPLES, 0, dtype=float) / self.SAMPLE_RATE
        self._buffers = [np.full((self.N_SAMPLES, 3), np.nan) for _ in SIGNAL_NAMES]
        self._lines:  list = []
        self._pkt_count = 0

        # ── Full recording storage ─────────────────────────────────────────────
        # Each entry: (time_s, acc_x, acc_y, acc_z, gyr_x, gyr_y, gyr_z)
        # Recording only starts when the user presses the start button.
        self._records: list[tuple] = []
        self._t_elapsed = 0.0   # running timestamp counter (seconds)
        self._recording = False

        self._last_quat = None   # latest orientation quaternion [w, x, y, z]

        self._build_ui()
        self._start_stream()
        self._anim = FuncAnimation(
            self._fig, self._update_plot,
            interval=PLOT_INTERVAL_MS, blit=True, cache_frame_data=False
        )
        self._poll_queue()
        self._update_3d()

    # ── UI ────────────────────────────────────────────────────────────────────

    def _build_ui(self):
        # Header
        header = "Capture2Go  ·  Sensor Dashboard"
        if self.teacher_mode:
            header += "  ·  Teacher"
        tk.Label(
            self, text=header,
            bg=COLOR_BLUE, fg="#FFFFFF",
            font=(MONO, 14, "bold"), pady=8
        ).pack(side=tk.TOP, fill=tk.X)

        # Student / teacher info banner
        info_banner = tk.Frame(self, bg=COLOR_PANEL, pady=4)
        info_banner.pack(side=tk.TOP, fill=tk.X, padx=8, pady=(4, 0))
        banner_text = ("🎓  Teacher mode" if self.teacher_mode else
                       f"🎓  {self.student_name}  ·  ID: {self.student_id}")
        tk.Label(
            info_banner, text=banner_text,
            bg=COLOR_PANEL, fg=COLOR_BLUE,
            font=TK_FONT_BOLD
        ).pack(side=tk.LEFT, padx=8)

        self._rec_var = tk.StringVar(
            value="⏸  Not recording – press the start button")
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

        # Fields: teacher = real labels, student = Signal A..D / Channel 1..3
        if self.teacher_mode:
            fields, key_map = TEACHER_FIELDS, TEACHER_KEY_MAP
        else:
            fields, key_map = build_student_fields()

        self._data_labels: dict[str, tk.StringVar] = {}
        # _value_vars[signal][channel] -> StringVar  (used by _handle_packet)
        self._value_vars: list[list[tk.StringVar | None]] = [
            [None, None, None] for _ in SIGNAL_NAMES
        ]

        for label, key in fields:
            if key is None:                       # section header
                tk.Label(
                    left, text=label,
                    bg=COLOR_PANEL, fg=COLOR_ORANGE,
                    font=TK_FONT_BOLD, anchor="w"
                ).pack(fill=tk.X, padx=8, pady=(6, 1))
                continue

            row = tk.Frame(left, bg=COLOR_PANEL)
            row.pack(fill=tk.X, padx=8, pady=1)
            var = tk.StringVar(value="—")
            self._data_labels[key] = var

            if key == "pkt_count":
                self._pkt_var = var
                tk.Label(row, text=label,
                         bg=COLOR_PANEL, fg=COLOR_MUTED,
                         font=TK_FONT, anchor="w", width=20).pack(side=tk.LEFT)
            else:
                sig, ch = key_map[key]
                self._value_vars[sig][ch] = var
                tk.Label(row, text="■", bg=COLOR_PANEL,
                         fg=CHANNEL_COLORS[ch], font=TK_FONT).pack(side=tk.LEFT)
                tk.Label(row, text=label,
                         bg=COLOR_PANEL, fg=COLOR_MUTED,
                         font=TK_FONT, anchor="w", width=18).pack(side=tk.LEFT)
            tk.Label(row, textvariable=var,
                     bg=COLOR_PANEL, fg=COLOR_BLUE,
                     font=TK_FONT, anchor="e", width=10).pack(side=tk.RIGHT)

        ttk.Separator(left, orient="horizontal").pack(fill=tk.X, padx=4, pady=4)
        self._status_var = tk.StringVar(value="🔄  Connecting…")
        tk.Label(
            left, textvariable=self._status_var,
            bg=COLOR_PANEL, fg=COLOR_TEXT,
            font=TK_FONT, pady=4, wraplength=280, justify=tk.LEFT
        ).pack(fill=tk.X, padx=8)

        # Start recording button
        self._start_btn = FlatButton(
            left, text=BTN_START_TEXT, command=self._start_recording,
            bg=COLOR_GREEN, fg="#FFFFFF", hover_bg=COLOR_GREEN_DARK,
            font=TK_FONT_BOLD
        )
        self._start_btn.pack(fill=tk.X, padx=8, pady=(0, 4))

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

        # 3D sensor view: below the buttons in the left panel
        view3d = tk.Frame(left, bg=COLOR_PANEL)
        view3d.pack(fill=tk.BOTH, expand=True, padx=4, pady=(0, 8))
        self._build_3d(view3d)

        # ── Right: matplotlib ─────────────────────────────────────────────────
        right = tk.Frame(main, bg=COLOR_BG)
        right.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self._fig = self._build_figure()
        canvas = FigureCanvasTkAgg(self._fig, master=right)
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        self._canvas = canvas

    # ── 3D sensor view ────────────────────────────────────────────────────────

    # Box proportions (x, y, z) roughly like the sensor housing
    _BOX = np.array([0.5, 0.3, 0.1])

    @staticmethod
    def _quat_to_matrix(q):
        w, x, y, z = q / np.linalg.norm(q)
        return np.array([
            [1 - 2*(y*y + z*z), 2*(x*y - z*w),     2*(x*z + y*w)],
            [2*(x*y + z*w),     1 - 2*(x*x + z*z), 2*(y*z - x*w)],
            [2*(x*z - y*w),     2*(y*z + x*w),     1 - 2*(x*x + y*y)],
        ])

    def _box_faces(self, R):
        sx, sy, sz = self._BOX
        v = np.array([[sx*a, sy*b, sz*c]
                      for a in (-1, 1) for b in (-1, 1) for c in (-1, 1)])
        v = v @ R.T
        idx = [(0, 1, 3, 2), (4, 5, 7, 6),   # x- , x+
               (0, 1, 5, 4), (2, 3, 7, 6),   # y- , y+
               (0, 2, 6, 4), (1, 3, 7, 5)]   # z- , z+
        return [v[list(f)] for f in idx]

    def _build_3d(self, parent):
        self._fig3d = plt.Figure(figsize=(3.0, 3.0), dpi=self._fig_dpi, tight_layout=True)
        self._fig3d.patch.set_facecolor(COLOR_PANEL)
        ax = self._fig3d.add_subplot(111, projection="3d")
        ax.set_facecolor(COLOR_PANEL)
        ax.set_xlim(-0.8, 0.8); ax.set_ylim(-0.8, 0.8); ax.set_zlim(-0.8, 0.8)
        ax.set_box_aspect((1, 1, 1))
        ax.set_xticklabels([]); ax.set_yticklabels([]); ax.set_zticklabels([])
        ax.set_title("Sensor orientation", color=COLOR_BLUE,
                     fontsize=PLOT_LABEL_SIZE, fontweight="bold",
                     fontfamily="monospace")
        ax.view_init(elev=20, azim=-60)
        self._ax3d = ax

        # Face colors: z+ (top, sensor label side) in orange, rest in blue/gray
        face_colors = [COLOR_BLUE, COLOR_BLUE, "#7FA8CC", "#7FA8CC",
                       COLOR_GRID, COLOR_ORANGE]
        self._box = Poly3DCollection(self._box_faces(np.eye(3)),
                                     facecolors=face_colors,
                                     edgecolors=COLOR_TEXT, linewidths=1.0,
                                     alpha=0.9)
        ax.add_collection3d(self._box)

        # Sensor axes: X red, Y green, Z blue
        self._axis_lines = []
        for col in ("#D32F2F", "#2E7D32", "#1565C0"):
            (ln,) = ax.plot([0, 0], [0, 0], [0, 0], color=col, linewidth=2.5)
            self._axis_lines.append(ln)
        self._set_3d_orientation(np.eye(3))

        self._canvas3d = FigureCanvasTkAgg(self._fig3d, master=parent)
        self._canvas3d.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def _set_3d_orientation(self, R):
        self._box.set_verts(self._box_faces(R))
        for i, ln in enumerate(self._axis_lines):
            tip = R[:, i] * 0.75
            ln.set_data_3d([0, tip[0]], [0, tip[1]], [0, tip[2]])

    def _update_3d(self):
        q = self._last_quat
        if q is not None and np.all(np.isfinite(q)):
            self._set_3d_orientation(self._quat_to_matrix(np.asarray(q, float)))
            self._canvas3d.draw_idle()
        self.after(40, self._update_3d)   # ~25 fps

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
        titles = TEACHER_PLOT_TITLES if self.teacher_mode else SIGNAL_NAMES

        for ax, name, ylim in zip(axes, titles, y_limits):
            ax.set_facecolor(COLOR_PANEL)
            for spine in ax.spines.values():
                spine.set_edgecolor(COLOR_SPINE)
            ax.tick_params(colors=COLOR_TEXT, labelsize=PLOT_TICK_SIZE)
            ax.set_title(name, color=COLOR_BLUE, fontsize=PLOT_TITLE_SIZE,
                         fontweight="bold", fontfamily="monospace", pad=8)
            ax.set_xlim(self._t[0], self._t[-1])
            ax.set_ylim(*ylim)
            ax.grid(color=COLOR_GRID, linestyle="--", linewidth=0.6)
            ax.set_prop_cycle("color", CHANNEL_COLORS)
            if self.teacher_mode:
                ax.set_xlabel("Time [s]", color=COLOR_TEXT,
                              fontsize=PLOT_LABEL_SIZE)

        for ax, buf in zip(axes, self._buffers):
            self._lines.append(ax.plot(self._t, buf, linewidth=1.4))

        legend_kw = dict(
            loc="upper left", fontsize=PLOT_LEGEND_SIZE,
            facecolor=COLOR_PANEL, edgecolor=COLOR_SPINE, labelcolor=COLOR_TEXT
        )
        if self.teacher_mode:
            for ax, names in zip(axes, TEACHER_CHANNEL_NAMES):
                ax.legend(names, **legend_kw)
        else:
            axes[0].legend(CHANNEL_NAMES, **legend_kw)
        return fig

    # ── Recording control ─────────────────────────────────────────────────────

    def _start_recording(self):
        """Begin storing samples (live display is already running)."""
        if self._recording:
            return
        self._records.clear()
        self._t_elapsed = 0.0          # recorded time starts at 0 s
        self._recording = True
        self._start_btn.update_style(
            text=BTN_RECORDING_TEXT,
            bg=COLOR_MUTED, hover_bg=COLOR_MUTED, enabled=False
        )
        self._rec_var.set("⏺  Recording: 0 samples")

    # ── Streaming ─────────────────────────────────────────────────────────────

    def _start_stream(self):
        self._stream_thread = threading.Thread(
            target=run_stream_thread,
            args=(self.device_name, self._queue, self._stop_event),
            daemon=True,
        )
        self._stream_thread.start()

    def _stop_stream(self, timeout: float = 6.0):
        """Ask the stream thread to stop and WAIT until the sensor is released."""
        self._stop_event.set()
        t = self._stream_thread
        if t is not None and t.is_alive():
            t.join(timeout)

    def _reconnect(self):
        """Stop current stream, re-open connection dialog, start new stream."""
        self._status_var.set("⏳  Closing previous connection…")
        self.update_idletasks()
        # Important: wait until the old connection is really closed.  A BLE
        # sensor accepts only ONE connection, so starting the new one while the
        # old one is still open makes the new connection fail.
        self._stop_stream()

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
                if isinstance(item, StatusMessage):
                    self._status_var.set(str(item))
                elif isinstance(item, Exception):
                    self._status_var.set(f"❌  {item}")
                    self._show_error(item)
                    break          # keep polling alive so Reconnect works
                elif isinstance(item, c2g.pkg.DataFullPacked):
                    self._handle_packet(item)
        except queue.Empty:
            pass
        self.after(POLL_INTERVAL_MS, self._poll_queue)

    def _handle_packet(self, packet):
        parsed = packet.parse()
        n = len(parsed["gyr"])
        batches = [
            np.rad2deg(parsed["gyr"]),       # Signal 0: gyroscope  (deg/s)
            parsed["acc"],                   # Signal 1: accelerometer (m/s²)
            parsed["mag"],                   # Signal 2: magnetometer
            np.rad2deg(np.array([
                c2g.utils.eulerAngles(parsed["quat9D"][i], "zxy", True)
                for i in range(n)
            ])),                             # Signal 3: Euler angles (deg)
        ]

        self._last_quat = parsed["quat9D"][-1]   # for the 3D view

        # ── Update rolling display buffers (always, live view) ─────────────
        for idx, batch in enumerate(batches):
            self._buffers[idx] = np.vstack([self._buffers[idx][n:], batch])
            for ch in range(3):
                self._value_vars[idx][ch].set(f"{batch[-1][ch]:+8.2f}")

        # ── Accumulate recording ONLY after pressing the start button ──────
        # acc + gyr → 6-column CSV
        if self._recording:
            acc_batch = batches[1]   # shape (n, 3)
            gyr_batch = batches[0]   # shape (n, 3)
            dt = 1.0 / self.SAMPLE_RATE
            for i in range(n):
                self._records.append((
                    round(self._t_elapsed, 5),
                    round(acc_batch[i, 0], 4),
                    round(acc_batch[i, 1], 4),
                    round(acc_batch[i, 2], 4),
                    round(gyr_batch[i, 0], 4),
                    round(gyr_batch[i, 1], 4),
                    round(gyr_batch[i, 2], 4),
                ))
                self._t_elapsed += dt
            self._rec_var.set(f"⏺  Recording: {len(self._records)} samples")

        self._pkt_count += 1
        self._pkt_var.set(str(self._pkt_count))
        self._status_var.set("🟢  Streaming active")

    def _show_error(self, exc: Exception):
        hint = ""
        exc_str = str(exc).lower()
        is_usb = self.device_name == "usb"
        if IS_LINUX and ("dialout" in exc_str or "permission" in exc_str
                         or "access" in exc_str or "serial" in exc_str):
            hint = (
                "\n\nLinux fix – run this in a terminal and reboot:\n"
                "   sudo usermod -aG dialout $USER"
            )
        elif is_usb:
            hint = (
                "\n\nCheck that the sensor is plugged in with a data cable "
                "and switched on, then press Reconnect."
            )
        else:
            hint = (
                "\n\nBluetooth checklist:\n"
                " • Sensor is switched on and close to the computer\n"
                " • Name is correct (e.g. IMU_3dbe7)\n"
                " • Sensor is NOT connected to another program, phone or "
                "computer\n"
                " • Bluetooth is enabled on this computer\n"
                " • If it still fails: switch the sensor off and on, then "
                "press Reconnect"
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
        # Wait until the sensor is disconnected properly; otherwise a BLE
        # sensor stays "connected" and refuses the next connection.
        self._status_var.set("⏳  Closing connection…")
        self.update_idletasks()
        self._stop_stream(timeout=6.0)

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
            if self._recording:
                msg = ("Recording was started but no sensor data were "
                       "received.\nNothing was exported.")
            else:
                msg = ("Data recording was never started (button "
                       f"'{BTN_START_TEXT.strip()}').\nNothing was exported.")
            messagebox.showinfo("No data recorded", msg, parent=self)

        self.destroy()


# ──────────────────────────────────────────────────────────────────────────────
# Entry point
# ──────────────────────────────────────────────────────────────────────────────

def main():
    # Hidden root so dialogs appear without a main window first
    root = tk.Tk()
    root.withdraw()

    # ── Step 0: Choose interface (student / teacher + password) ───────────────
    mode_dialog = ModeDialog(root)
    root.wait_window(mode_dialog)

    if mode_dialog.mode is None:
        root.destroy()
        sys.exit(0)

    teacher_mode = mode_dialog.mode == "teacher"

    # ── Step 1: Collect student info (students only) ──────────────────────────
    if teacher_mode:
        student_name = "Teacher"
        student_id   = "teacher"
    else:
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
        teacher_mode=teacher_mode,
    )
    app.mainloop()


if __name__ == "__main__":
    main()
    
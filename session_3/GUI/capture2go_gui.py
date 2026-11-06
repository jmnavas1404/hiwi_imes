#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2025 SensorStim Neurotechnology GmbH <support@capture2go.com>
#
# SPDX-License-Identifier: MIT
#
# Real-time GUI for the Capture2Go sensor - STUDENT VERSION
# Packaged as a standalone executable (.exe / .app).
# A connection dialog is shown at startup so no terminal arguments are needed.
#
# Permission error on Linux?  Run once in a terminal:
#   sudo usermod -aG dialout $USER
# then log out and back in (or reboot).  After that the sensor will be found.

import asyncio
import queue
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

CHANNEL_COLORS = [COLOR_BLUE, COLOR_ORANGE, COLOR_TEXT]
CHANNEL_NAMES  = ["Channel 1", "Channel 2", "Channel 3"]

FONT_SIZE      = 10
TK_FONT        = ("Monospace", FONT_SIZE)
TK_FONT_BOLD   = ("Monospace", FONT_SIZE, "bold")
TICK_SIZE      = 9
LEGEND_SIZE    = 9

POLL_INTERVAL_MS = 20
PLOT_INTERVAL_MS = 40

# Anonymous signal names shown to students (no axis labels / units on purpose)
SIGNAL_NAMES = ["Signal A", "Signal B", "Signal C", "Signal D"]


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
# Connection dialog  (shown before the dashboard)
# ──────────────────────────────────────────────────────────────────────────────

class ConnectionDialog(tk.Toplevel):
    """
    Modal dialog that lets the user choose USB or BLE and type the device name.
    Sets self.result to the chosen device name, or None if cancelled.
    """

    def __init__(self, parent: tk.Tk):
        super().__init__(parent)
        self.title("Connect to sensor")
        self.resizable(False, False)
        self.configure(bg=COLOR_BG)
        self.grab_set()          # modal
        self.result: str | None = None

        self._build()
        self.protocol("WM_DELETE_WINDOW", self._cancel)

        # Center on screen
        self.update_idletasks()
        x = (self.winfo_screenwidth()  - self.winfo_reqwidth())  // 2
        y = (self.winfo_screenheight() - self.winfo_reqheight()) // 2
        self.geometry(f"+{x}+{y}")

    def _build(self):
        # ── Header ────────────────────────────────────────────────────────────
        tk.Label(
            self, text="Capture2Go  ·  Connect",
            bg=COLOR_BLUE, fg="#FFFFFF",
            font=("Monospace", 13, "bold"), pady=8
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
            bg=COLOR_BG, fg=COLOR_TEXT, selectcolor=COLOR_BG,
            activebackground=COLOR_BG, font=TK_FONT,
            command=self._on_conn_type
        ).pack(side=tk.LEFT, padx=(0, 16))

        tk.Radiobutton(
            frame_radio, text="Bluetooth (BLE)",
            variable=self._conn_var, value="ble",
            bg=COLOR_BG, fg=COLOR_TEXT, selectcolor=COLOR_BG,
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
        self._ble_frame.pack_forget()   # hidden by default (USB selected)

        # ── Linux note (dialout group) ────────────────────────────────────────
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
            font=("Monospace", FONT_SIZE - 1),
            justify=tk.LEFT, anchor="w", padx=8, pady=6
        ).pack(fill=tk.X)

        # ── Buttons ───────────────────────────────────────────────────────────
        btn_frame = tk.Frame(body, bg=COLOR_BG)
        btn_frame.grid(row=4, column=0, columnspan=2, sticky="e")

        tk.Button(
            btn_frame, text="Cancel",
            bg=COLOR_PANEL, fg=COLOR_MUTED,
            font=TK_FONT, relief=tk.FLAT, cursor="hand2",
            command=self._cancel, padx=12, pady=4
        ).pack(side=tk.LEFT, padx=(0, 8))

        tk.Button(
            btn_frame, text="  Connect  ",
            bg=COLOR_ORANGE, fg="#FFFFFF",
            activebackground=COLOR_ORANGE_DARK, activeforeground="#FFFFFF",
            font=TK_FONT_BOLD, relief=tk.FLAT, cursor="hand2",
            command=self._connect, padx=12, pady=4
        ).pack(side=tk.LEFT)

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
# Main dashboard window
# ──────────────────────────────────────────────────────────────────────────────

class SensorDashboard(tk.Tk):
    N_SAMPLES   = 800
    SAMPLE_RATE = 200.0

    def __init__(self, device_name: str):
        super().__init__()
        self.device_name = device_name
        self.title(f"Capture2Go  ·  {device_name}")
        self.configure(bg=COLOR_BG)
        self.protocol("WM_DELETE_WINDOW", self._on_close)

        self._fig_dpi = 72.0 * float(self.tk.call("tk", "scaling"))

        self._queue: queue.Queue = queue.Queue()
        self._stop_event = threading.Event()

        self._t       = np.arange(-self.N_SAMPLES, 0, dtype=float) / self.SAMPLE_RATE
        self._buffers = [np.full((self.N_SAMPLES, 3), np.nan) for _ in SIGNAL_NAMES]
        self._lines:  list = []
        self._pkt_count = 0

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
            font=("Monospace", 14, "bold"), pady=8
        ).pack(side=tk.TOP, fill=tk.X)

        main = tk.Frame(self, bg=COLOR_BG)
        main.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)

        # ── Left: data table ──────────────────────────────────────────────────
        left = tk.Frame(main, bg=COLOR_PANEL, relief=tk.FLAT, bd=0)
        left.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 6))

        tk.Label(
            left, text="📡  Real-time data",
            bg=COLOR_PANEL, fg=COLOR_BLUE,
            font=("Monospace", FONT_SIZE + 1, "bold"), pady=6
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
        tk.Button(
            left, text="🔌  Reconnect",
            bg=COLOR_PANEL, fg=COLOR_BLUE,
            font=TK_FONT, relief=tk.FLAT, cursor="hand2",
            command=self._reconnect
        ).pack(fill=tk.X, padx=8, pady=(0, 4))

        # Stop button
        tk.Button(
            left, text="⏹  Stop streaming",
            bg=COLOR_ORANGE, fg="#FFFFFF",
            activebackground=COLOR_ORANGE_DARK, activeforeground="#FFFFFF",
            font=TK_FONT_BOLD, relief=tk.FLAT, cursor="hand2",
            command=self._on_close
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
            self.title(f"Capture2Go  ·  {self.device_name}")
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
                    return
                if isinstance(item, c2g.pkg.DataFullPacked):
                    self._handle_packet(item)
        except queue.Empty:
            pass
        self.after(POLL_INTERVAL_MS, self._poll_queue)

    def _handle_packet(self, packet):
        parsed = packet.parse()
        n = len(parsed["gyr"])
        batches = [
            np.rad2deg(parsed["gyr"]),
            parsed["acc"],
            parsed["mag"],
            np.rad2deg(np.array([
                c2g.utils.eulerAngles(parsed["quat9D"][i], "zxy", True)
                for i in range(n)
            ])),
        ]
        for idx, batch in enumerate(batches):
            self._buffers[idx] = np.vstack([self._buffers[idx][n:], batch])
            for ch in range(3):
                self._value_vars[idx][ch].set(f"{batch[-1][ch]:+8.2f}")

        self._pkt_count += 1
        self._pkt_var.set(str(self._pkt_count))
        self._status_var.set("🟢  Streaming active")

    def _show_error(self, exc: Exception):
        hint = ""
        exc_str = str(exc).lower()
        if "dialout" in exc_str or "permission" in exc_str or "access" in exc_str or "serial" in exc_str:
            hint = (
                "\n\nLinux fix – run this in a terminal and reboot:\n"
                "   sudo usermod -aG dialout $USER"
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

    # ── Shutdown ──────────────────────────────────────────────────────────────

    def _on_close(self):
        self._stop_event.set()
        self.destroy()


# ──────────────────────────────────────────────────────────────────────────────
# Entry point
# ──────────────────────────────────────────────────────────────────────────────

def main():
    # Hidden root so the connection dialog appears without a main window first
    root = tk.Tk()
    root.withdraw()

    dialog = ConnectionDialog(root)
    root.wait_window(dialog)

    if not dialog.result:
        root.destroy()
        sys.exit(0)

    root.destroy()

    app = SensorDashboard(device_name=dialog.result)
    app.mainloop()


if __name__ == "__main__":
    main()


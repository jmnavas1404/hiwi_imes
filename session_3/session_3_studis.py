#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2025 SensorStim Neurotechnology GmbH <support@capture2go.com>
#
# SPDX-License-Identifier: MIT
#
# Real-time GUI for the Capture2Go sensor - STUDENT VERSION
# Signals are shown anonymously (no names, no units) so that students can
# work out what each signal represents.
# Usage: python imu_dashboard_v2_student.py [device_name]
#   e.g. python imu_dashboard_v2_student.py usb
#        python imu_dashboard_v2_student.py IMU_ab1234

import argparse
import asyncio
import queue
import threading

import numpy as np
import tkinter as tk
from tkinter import ttk

import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.animation import FuncAnimation

import capture2go as c2g


# ──────────────────────────────────────────────────────────────────────────────
# Color palette (taken from the imes logo: blue, orange, white, dark gray)
# ──────────────────────────────────────────────────────────────────────────────

COLOR_BG = "#EEF1F5"          # window background (light gray)
COLOR_PANEL = "#FFFFFF"       # panels and plot backgrounds (white)
COLOR_TEXT = "#3C3C3B"        # main text (dark gray, as in the logo lettering)
COLOR_MUTED = "#6B6B6A"       # secondary text
COLOR_BLUE = "#00569E"        # logo blue
COLOR_ORANGE = "#E8822A"      # logo orange
COLOR_ORANGE_DARK = "#C96A15" # button hover
COLOR_GRID = "#D9DDE3"
COLOR_SPINE = "#B8BEC8"

# One color per channel, identical in every plot and in the data table
CHANNEL_COLORS = [COLOR_BLUE, COLOR_ORANGE, COLOR_TEXT]
CHANNEL_NAMES = ["Channel 1", "Channel 2", "Channel 3"]


# ──────────────────────────────────────────────────────────────────────────────
# Appearance
# ──────────────────────────────────────────────────────────────────────────────

# One single font size is used for the left panel text AND the plot titles,
# so both always look the same size.
FONT_SIZE = 10
TK_FONT = ("Monospace", FONT_SIZE)
TK_FONT_BOLD = ("Monospace", FONT_SIZE, "bold")

TICK_SIZE = 9
LEGEND_SIZE = 9

# Update intervals (milliseconds)
POLL_INTERVAL_MS = 20
PLOT_INTERVAL_MS = 40

# Anonymous signal names shown to the students
SIGNAL_NAMES = ["Signal A", "Signal B", "Signal C", "Signal D"]


# ──────────────────────────────────────────────────────────────────────────────
# BLE/USB streaming - runs in a separate thread
# ──────────────────────────────────────────────────────────────────────────────

async def stream_sensor(device_name: str, data_queue: queue.Queue, stop_event: threading.Event):
    """Connect to the sensor and put packets in the queue until stop_event is set."""
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
        # Put the exception in the queue so the GUI can display it
        data_queue.put(exc)


def run_stream_thread(device_name: str, data_queue: queue.Queue, stop_event: threading.Event):
    """Entry point of the streaming thread: runs its own asyncio event loop."""
    loop = asyncio.new_event_loop()
    loop.run_until_complete(stream_sensor(device_name, data_queue, stop_event))
    loop.close()


# ──────────────────────────────────────────────────────────────────────────────
# Main window
# ──────────────────────────────────────────────────────────────────────────────

class SensorDashboard(tk.Tk):
    # Number of samples shown in the plots (4 s at 200 Hz)
    N_SAMPLES = 800
    SAMPLE_RATE = 200.0

    def __init__(self, device_name: str):
        super().__init__()
        self.device_name = device_name
        self.title(f"Capture2Go – {device_name}")
        self.configure(bg=COLOR_BG)
        self.protocol("WM_DELETE_WINDOW", self._on_close)

        # Match matplotlib's DPI to Tk's screen scaling. Without this, text
        # drawn by matplotlib looks much smaller than Tk text on HiDPI screens,
        # even when both use the same point size.
        self._fig_dpi = 72.0 * float(self.tk.call("tk", "scaling"))

        # Queue and stop event shared with the streaming thread
        self._queue: queue.Queue = queue.Queue()
        self._stop_event = threading.Event()

        # Data buffers: one (N_SAMPLES x 3) array per anonymous signal
        self._t = np.arange(-self.N_SAMPLES, 0, dtype=float) / self.SAMPLE_RATE
        self._buffers = [np.full((self.N_SAMPLES, 3), np.nan) for _ in SIGNAL_NAMES]
        self._lines: list = []
        self._pkt_count = 0

        self._build_ui()
        self._start_stream()
        self._anim = FuncAnimation(
            self._fig, self._update_plot,
            interval=PLOT_INTERVAL_MS, blit=True, cache_frame_data=False
        )
        # Start polling the queue (the ONLY place that reads from it)
        self._poll_queue()

    # ── UI construction ───────────────────────────────────────────────────────

    def _build_ui(self):
        """Build the main layout: left panel (data table) + right panel (plots)."""
        # Top header (blue band, white text)
        header = tk.Label(
            self, text="Capture2Go  ·  Sensor Dashboard",
            bg=COLOR_BLUE, fg="#FFFFFF",
            font=("Monospace", 14, "bold"), pady=8
        )
        header.pack(side=tk.TOP, fill=tk.X)

        # Main horizontal container
        main = tk.Frame(self, bg=COLOR_BG)
        main.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)

        # ── Left panel: data table ────────────────────────────────────────────
        left = tk.Frame(main, bg=COLOR_PANEL, relief=tk.FLAT, bd=0)
        left.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 6))

        tk.Label(
            left, text="📡  Real-time data",
            bg=COLOR_PANEL, fg=COLOR_BLUE,
            font=("Monospace", FONT_SIZE + 1, "bold"), pady=6
        ).pack(fill=tk.X, padx=8)

        ttk.Separator(left, orient="horizontal").pack(fill=tk.X, padx=4)

        # Rows: for each signal, a section header + one row per channel.
        # Each channel name has a small colored square matching its plot line.
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
                tk.Label(
                    row, text="■", bg=COLOR_PANEL, fg=ch_color, font=TK_FONT
                ).pack(side=tk.LEFT)
                tk.Label(
                    row, text=f" {ch_name}",
                    bg=COLOR_PANEL, fg=COLOR_MUTED,
                    font=TK_FONT, anchor="w", width=18
                ).pack(side=tk.LEFT)
                var = tk.StringVar(value="—")
                signal_vars.append(var)
                tk.Label(
                    row, textvariable=var,
                    bg=COLOR_PANEL, fg=COLOR_BLUE,
                    font=TK_FONT, anchor="e", width=10
                ).pack(side=tk.RIGHT)
            self._value_vars.append(signal_vars)

        # Packet counter
        tk.Label(
            left, text="── Status ──",
            bg=COLOR_PANEL, fg=COLOR_ORANGE,
            font=TK_FONT_BOLD, anchor="w"
        ).pack(fill=tk.X, padx=8, pady=(6, 1))
        row = tk.Frame(left, bg=COLOR_PANEL)
        row.pack(fill=tk.X, padx=8, pady=1)
        tk.Label(
            row, text="  Packets received",
            bg=COLOR_PANEL, fg=COLOR_MUTED,
            font=TK_FONT, anchor="w", width=20
        ).pack(side=tk.LEFT)
        self._pkt_var = tk.StringVar(value="—")
        tk.Label(
            row, textvariable=self._pkt_var,
            bg=COLOR_PANEL, fg=COLOR_BLUE,
            font=TK_FONT, anchor="e", width=10
        ).pack(side=tk.RIGHT)

        # Connection status
        ttk.Separator(left, orient="horizontal").pack(fill=tk.X, padx=4, pady=4)
        self._status_var = tk.StringVar(value="🔄  Connecting…")
        tk.Label(
            left, textvariable=self._status_var,
            bg=COLOR_PANEL, fg=COLOR_TEXT,
            font=TK_FONT, pady=4
        ).pack(fill=tk.X, padx=8)

        # Stop button
        stop_btn = tk.Button(
            left, text="⏹  Stop streaming",
            bg=COLOR_ORANGE, fg="#FFFFFF",
            activebackground=COLOR_ORANGE_DARK, activeforeground="#FFFFFF",
            font=TK_FONT_BOLD, relief=tk.FLAT, cursor="hand2",
            command=self._on_close
        )
        stop_btn.pack(fill=tk.X, padx=8, pady=8)

        # ── Right panel: matplotlib plots ─────────────────────────────────────
        right = tk.Frame(main, bg=COLOR_BG)
        right.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self._fig = self._build_figure()
        canvas = FigureCanvasTkAgg(self._fig, master=right)
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        self._canvas = canvas

    def _build_figure(self) -> plt.Figure:
        """Create the matplotlib figure with 4 anonymous subplots."""
        # Initial size of about 1000 x 700 pixels, independent of the DPI
        fig = plt.Figure(
            figsize=(1000 / self._fig_dpi, 700 / self._fig_dpi),
            dpi=self._fig_dpi,
            tight_layout=True,
        )
        fig.patch.set_facecolor(COLOR_BG)

        axes = fig.subplots(2, 2).flatten()
        self._axes = axes

        # Fixed vertical ranges per plot (one per signal)
        y_limits = [(-800, 800), (-20, 20), (-100, 100), (-180, 180)]

        for ax, name, ylim in zip(axes, SIGNAL_NAMES, y_limits):
            ax.set_facecolor(COLOR_PANEL)
            for spine in ax.spines.values():
                spine.set_edgecolor(COLOR_SPINE)
            ax.tick_params(colors=COLOR_TEXT, labelsize=TICK_SIZE)
            # Title uses the same size as the left panel text.
            # No axis labels and no units are shown on purpose.
            ax.set_title(
                name, color=COLOR_BLUE, fontsize=FONT_SIZE,
                fontweight="bold", fontfamily="monospace", pad=6
            )
            ax.set_xlim(self._t[0], self._t[-1])
            ax.set_ylim(*ylim)
            ax.grid(color=COLOR_GRID, linestyle="--", linewidth=0.6)
            ax.set_prop_cycle("color", CHANNEL_COLORS)

        # Create one set of 3 lines per plot
        for ax, buf in zip(axes, self._buffers):
            self._lines.append(ax.plot(self._t, buf, linewidth=1.4))

        # Legend only on the first plot to keep the figure clean
        axes[0].legend(
            CHANNEL_NAMES, loc="upper left", fontsize=LEGEND_SIZE,
            facecolor=COLOR_PANEL, edgecolor=COLOR_SPINE, labelcolor=COLOR_TEXT
        )

        return fig

    # ── Streaming thread ──────────────────────────────────────────────────────

    def _start_stream(self):
        self._stream_thread = threading.Thread(
            target=run_stream_thread,
            args=(self.device_name, self._queue, self._stop_event),
            daemon=True,
        )
        self._stream_thread.start()

    # ── Queue polling (updates data table AND plot buffers) ───────────────────

    def _poll_queue(self):
        """Read everything available in the queue. This is the only queue consumer."""
        try:
            while True:
                item = self._queue.get_nowait()
                if isinstance(item, Exception):
                    self._status_var.set(f"❌  Error: {item}")
                    return
                if isinstance(item, c2g.pkg.DataFullPacked):
                    self._handle_packet(item)
        except queue.Empty:
            pass
        self.after(POLL_INTERVAL_MS, self._poll_queue)

    def _handle_packet(self, packet):
        """Update plot buffers and data table with one packet (a batch of samples)."""
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
            # Shift the buffer and append the new batch
            self._buffers[idx] = np.vstack([self._buffers[idx][n:], batch])
            # Data table shows the last sample of the batch
            for ch in range(3):
                self._value_vars[idx][ch].set(f"{batch[-1][ch]:+8.2f}")

        self._pkt_count += 1
        self._pkt_var.set(str(self._pkt_count))
        self._status_var.set("🟢  Streaming active")

    # ── Matplotlib animation (drawing only) ───────────────────────────────────

    def _update_plot(self, _frame):
        """Redraw the lines from the buffers. Does not touch the queue."""
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
    parser = argparse.ArgumentParser(
        description="Real-time GUI for the Capture2Go sensor (student version)."
    )
    parser.add_argument(
        "device", nargs="?", default="usb",
        help='Device name: "usb" (default) or e.g. "IMU_ab1234" for BLE'
    )
    args = parser.parse_args()

    app = SensorDashboard(device_name=args.device)
    app.mainloop()


if __name__ == "__main__":
    main()
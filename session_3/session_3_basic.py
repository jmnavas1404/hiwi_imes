#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2025 SensorStim Neurotechnology GmbH <support@capture2go.com>
#
# SPDX-License-Identifier: MIT
#
# Real-time GUI for the Capture2Go IMU
# Shows: live data table (left) + live plots (right)
# Usage: python imu_dashboard_v1.py [device_name]
#   e.g. python imu_dashboard_v1.py usb
#        python imu_dashboard_v1.py IMU_ab1234

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
# Appearance
# ──────────────────────────────────────────────────────────────────────────────

# One single font size is used for the left panel text AND the plot titles,
# so both always look the same size.
FONT_SIZE = 10

# Plot titles: same size as the left panel text. Raise TITLE_SIZE (e.g. 12 or 14)
# if you want them even bigger.
TITLE_SIZE = FONT_SIZE
TK_FONT = ("Monospace", FONT_SIZE)
TK_FONT_BOLD = ("Monospace", FONT_SIZE, "bold")

# Smaller secondary text inside the plots
AXIS_LABEL_SIZE = 9
TICK_SIZE = 9
LEGEND_SIZE = 9

# Update intervals (milliseconds)
POLL_INTERVAL_MS = 20
PLOT_INTERVAL_MS = 40


# ──────────────────────────────────────────────────────────────────────────────
# BLE/USB streaming - runs in a separate thread
# ──────────────────────────────────────────────────────────────────────────────

async def stream_imu(device_name: str, data_queue: queue.Queue, stop_event: threading.Event):
    """Connect to the IMU and put packets in the queue until stop_event is set."""
    try:
        imu, = await c2g.connect([device_name])
        await imu.init(setTime=True, abortStreaming=True)
        await imu.send(c2g.pkg.CmdSetMeasurementMode(
            fullPackedMode=c2g.pkg.SamplingMode.MODE_200HZ,
            statusMode=1,
        ))
        await imu.send(c2g.pkg.CmdStartStreaming())
        try:
            async for package in imu:
                if stop_event.is_set():
                    break
                data_queue.put(package)
        except asyncio.CancelledError:
            pass
        finally:
            await imu.send(c2g.pkg.CmdStopStreaming())
            await imu.disconnect()
    except Exception as exc:
        # Put the exception in the queue so the GUI can display it
        data_queue.put(exc)


def run_ble_thread(device_name: str, data_queue: queue.Queue, stop_event: threading.Event):
    """Entry point of the streaming thread: runs its own asyncio event loop."""
    loop = asyncio.new_event_loop()
    loop.run_until_complete(stream_imu(device_name, data_queue, stop_event))
    loop.close()


# ──────────────────────────────────────────────────────────────────────────────
# Main window
# ──────────────────────────────────────────────────────────────────────────────

class IMUDashboard(tk.Tk):
    # Number of samples shown in the plots (4 s at 200 Hz)
    N_SAMPLES = 800
    SAMPLE_RATE = 200.0

    def __init__(self, device_name: str):
        super().__init__()
        self.device_name = device_name
        self.title(f"Capture2Go – {device_name}")
        self.configure(bg="#1e1e2e")
        self.protocol("WM_DELETE_WINDOW", self._on_close)

        # Last text scale ratio applied to the plots (see _sync_font_sizes)
        self._text_ratio = None

        # Queue and stop event shared with the streaming thread
        self._queue: queue.Queue = queue.Queue()
        self._stop_event = threading.Event()

        # Data buffers
        self._t = np.arange(-self.N_SAMPLES, 0, dtype=float) / self.SAMPLE_RATE
        self._gyr = np.full((self.N_SAMPLES, 3), np.nan)
        self._acc = np.full((self.N_SAMPLES, 3), np.nan)
        self._mag = np.full((self.N_SAMPLES, 3), np.nan)
        self._euler = np.full((self.N_SAMPLES, 3), np.nan)
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
        # Top header
        header = tk.Label(
            self, text="Capture2Go  ·  IMU Dashboard",
            bg="#1e1e2e", fg="#cdd6f4",
            font=("Monospace", 14, "bold"), pady=6
        )
        header.pack(side=tk.TOP, fill=tk.X)

        # Main horizontal container
        main = tk.Frame(self, bg="#1e1e2e")
        main.pack(fill=tk.BOTH, expand=True, padx=8, pady=(0, 8))

        # ── Left panel: data table ────────────────────────────────────────────
        left = tk.Frame(main, bg="#181825", relief=tk.FLAT, bd=0)
        left.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 6))

        tk.Label(
            left, text="📡  Real-time data",
            bg="#181825", fg="#89b4fa",
            font=("Monospace", FONT_SIZE + 1, "bold"), pady=6
        ).pack(fill=tk.X, padx=8)

        ttk.Separator(left, orient="horizontal").pack(fill=tk.X, padx=4)

        self._data_labels: dict[str, tk.StringVar] = {}
        fields = [
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

        for label_text, key in fields:
            row = tk.Frame(left, bg="#181825")
            row.pack(fill=tk.X, padx=8, pady=1)
            if key is None:
                # Section header
                tk.Label(
                    row, text=label_text,
                    bg="#181825", fg="#f38ba8",
                    font=TK_FONT_BOLD, anchor="w"
                ).pack(fill=tk.X, pady=(6, 1))
            else:
                tk.Label(
                    row, text=label_text,
                    bg="#181825", fg="#a6adc8",
                    font=TK_FONT, anchor="w", width=10
                ).pack(side=tk.LEFT)
                var = tk.StringVar(value="—")
                self._data_labels[key] = var
                tk.Label(
                    row, textvariable=var,
                    bg="#181825", fg="#a6e3a1",
                    font=TK_FONT, anchor="e", width=10
                ).pack(side=tk.RIGHT)

        # Connection status
        ttk.Separator(left, orient="horizontal").pack(fill=tk.X, padx=4, pady=4)
        self._status_var = tk.StringVar(value="🔄  Connecting…")
        tk.Label(
            left, textvariable=self._status_var,
            bg="#181825", fg="#f9e2af",
            font=TK_FONT, pady=4
        ).pack(fill=tk.X, padx=8)

        # Stop button
        stop_btn = tk.Button(
            left, text="⏹  Stop streaming",
            bg="#313244", fg="#f38ba8",
            font=TK_FONT, relief=tk.FLAT, cursor="hand2",
            command=self._on_close
        )
        stop_btn.pack(fill=tk.X, padx=8, pady=8)

        # ── Right panel: matplotlib plots ─────────────────────────────────────
        right = tk.Frame(main, bg="#1e1e2e")
        right.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self._fig = self._build_figure()
        canvas = FigureCanvasTkAgg(self._fig, master=right)
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        self._canvas = canvas
        # Keep plot text the same on-screen size as the Tk text, whatever the DPI
        canvas.mpl_connect("resize_event", self._sync_font_sizes)
        self.after(300, self._sync_font_sizes)

    def _build_figure(self) -> plt.Figure:
        """Create the matplotlib figure with 4 subplots."""
        # Initial size of about 1000 x 700 pixels, independent of the DPI
        self._legends = []
        fig = plt.Figure(figsize=(10, 7), tight_layout=True)
        fig.patch.set_facecolor("#1e1e2e")

        axes = fig.subplots(2, 2)
        self._axes = axes
        ax_colors = {
            "rgb": ["#d62728", "#2ca02c", "#1f77b4"],  # red, green, blue -> x, y, z
            "bry": ["#1f77b4", "#d62728", "#2ca02c"],  # for Euler angles
        }

        def style_ax(ax, title, ylabel, ylim, colors):
            ax.set_facecolor("#181825")
            for spine in ax.spines.values():
                spine.set_edgecolor("#45475a")
            ax.tick_params(colors="#cdd6f4", labelsize=TICK_SIZE)
            # Title uses the same size as the left panel text
            ax.set_title(
                title, color="#cdd6f4", fontsize=TITLE_SIZE,
                fontweight="bold", fontfamily="monospace", pad=6
            )
            ax.set_xlabel("Time [s]", color="#9399b2", fontsize=AXIS_LABEL_SIZE)
            ax.set_ylabel(ylabel, color="#9399b2", fontsize=AXIS_LABEL_SIZE)
            ax.set_xlim(self._t[0], self._t[-1])
            ax.set_ylim(*ylim)
            ax.grid(color="#313244", linestyle="--", linewidth=0.5)
            ax.set_prop_cycle("color", colors)

        def style_legend(ax, labels):
            self._legends.append(ax.legend(
                labels, loc="upper left", fontsize=LEGEND_SIZE,
                facecolor="#313244", labelcolor="#cdd6f4"
            ))

        style_ax(axes[0, 0], "Gyroscope [°/s]", "°/s", (-800, 800), ax_colors["rgb"])
        self._gyr_lines = axes[0, 0].plot(self._t, self._gyr)
        style_legend(axes[0, 0], ["x", "y", "z"])

        style_ax(axes[0, 1], "Accelerometer [m/s²]", "m/s²", (-20, 20), ax_colors["rgb"])
        self._acc_lines = axes[0, 1].plot(self._t, self._acc)
        style_legend(axes[0, 1], ["x", "y", "z"])

        style_ax(axes[1, 0], "Magnetometer [µT]", "µT", (-100, 100), ax_colors["rgb"])
        self._mag_lines = axes[1, 0].plot(self._t, self._mag)
        style_legend(axes[1, 0], ["x", "y", "z"])

        style_ax(axes[1, 1], "Euler orientation [°]", "°", (-180, 180), ax_colors["bry"])
        self._euler_lines = axes[1, 1].plot(self._t, self._euler)
        style_legend(axes[1, 1], ["z (roll)", "x' (pitch)", "y'' (yaw)"])

        return fig

    # ── Font size sync ────────────────────────────────────────────────────────

    def _sync_font_sizes(self, _event=None):
        """Make the plot text the same on-screen size as the Tk text.

        Matplotlib sizes are points at the figure's own DPI, which differs from
        Tk's screen scaling (especially on HiDPI displays). This converts the
        Tk point sizes into the equivalent matplotlib sizes, using real pixels.
        """
        tk_px_per_pt = float(self.tk.call("tk", "scaling"))
        mpl_px_per_pt = self._fig.dpi / 72.0
        ratio = tk_px_per_pt / mpl_px_per_pt
        if self._text_ratio is not None and abs(ratio - self._text_ratio) < 1e-3:
            return
        self._text_ratio = ratio

        for ax in self._axes.flatten():
            ax.title.set_fontsize(TITLE_SIZE * ratio)
            ax.xaxis.label.set_fontsize(AXIS_LABEL_SIZE * ratio)
            ax.yaxis.label.set_fontsize(AXIS_LABEL_SIZE * ratio)
            ax.tick_params(labelsize=TICK_SIZE * ratio)
        for legend in self._legends:
            for text in legend.get_texts():
                text.set_fontsize(LEGEND_SIZE * ratio)
        self._canvas.draw_idle()

    # ── Streaming thread ──────────────────────────────────────────────────────

    def _start_stream(self):
        self._stream_thread = threading.Thread(
            target=run_ble_thread,
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
        gyr = np.rad2deg(parsed["gyr"])
        acc = parsed["acc"]
        mag = parsed["mag"]
        n = len(gyr)
        euler = np.rad2deg(np.array([
            c2g.utils.eulerAngles(parsed["quat9D"][i], "zxy", True)
            for i in range(n)
        ]))

        # Shift the buffers and append the new batch
        self._gyr = np.vstack([self._gyr[n:], gyr])
        self._acc = np.vstack([self._acc[n:], acc])
        self._mag = np.vstack([self._mag[n:], mag])
        self._euler = np.vstack([self._euler[n:], euler])

        # Data table shows the last sample of the batch
        g, a, m, e = gyr[-1], acc[-1], mag[-1], euler[-1]
        labels = self._data_labels
        labels["gyr_x"].set(f"{g[0]:+8.2f}")
        labels["gyr_y"].set(f"{g[1]:+8.2f}")
        labels["gyr_z"].set(f"{g[2]:+8.2f}")
        labels["acc_x"].set(f"{a[0]:+8.3f}")
        labels["acc_y"].set(f"{a[1]:+8.3f}")
        labels["acc_z"].set(f"{a[2]:+8.3f}")
        labels["mag_x"].set(f"{m[0]:+8.2f}")
        labels["mag_y"].set(f"{m[1]:+8.2f}")
        labels["mag_z"].set(f"{m[2]:+8.2f}")
        labels["euler_z"].set(f"{e[0]:+8.2f}")
        labels["euler_x"].set(f"{e[1]:+8.2f}")
        labels["euler_y"].set(f"{e[2]:+8.2f}")
        self._pkt_count += 1
        labels["pkt_count"].set(str(self._pkt_count))
        self._status_var.set("🟢  Streaming active")

    # ── Matplotlib animation (drawing only) ───────────────────────────────────

    def _update_plot(self, _frame):
        """Redraw the lines from the buffers. Does not touch the queue."""
        for i, line in enumerate(self._gyr_lines):
            line.set_ydata(self._gyr[:, i])
        for i, line in enumerate(self._acc_lines):
            line.set_ydata(self._acc[:, i])
        for i, line in enumerate(self._mag_lines):
            line.set_ydata(self._mag[:, i])
        for i, line in enumerate(self._euler_lines):
            line.set_ydata(self._euler[:, i])

        return self._gyr_lines + self._acc_lines + self._mag_lines + self._euler_lines

    # ── Shutdown ──────────────────────────────────────────────────────────────

    def _on_close(self):
        self._stop_event.set()
        self.destroy()


# ──────────────────────────────────────────────────────────────────────────────
# Entry point
# ──────────────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Real-time GUI for the Capture2Go IMU (streaming + plots)."
    )
    parser.add_argument(
        "device", nargs="?", default="usb",
        help='IMU device name: "usb" (default) or e.g. "IMU_ab1234" for BLE'
    )
    args = parser.parse_args()

    app = IMUDashboard(device_name=args.device)
    app.mainloop()


if __name__ == "__main__":
    main()
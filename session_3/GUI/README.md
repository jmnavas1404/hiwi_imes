# Capture2Go GUI – Sensor Dashboard (Student Version)

A standalone GUI application for real-time IMU sensor visualization and recording.
No Python installation required — just run the executable.

---

## Files in this folder

| File | Description |
|------|-------------|
| `Capture2Go` | **Linux** executable *(build on Linux — see below)* |
| `Capture2Go.exe` | **Windows** executable *(build on Windows — see below)* |
| `Capture2Go.app` / `Capture2Go-mac.zip` | **macOS** app bundle *(build on macOS — see below)* |
| `capture2go_gui.py` | Source code (only needed to rebuild the executables) |

---

## Running the application

### Windows
Double-click `Capture2Go.exe`.

If Windows shows *"Windows protected your PC"* (the file is not code-signed):
click **More info → Run anyway**.

Do not run it from inside a `.zip` file — extract it first.

### macOS
Unzip `Capture2Go-mac.zip` and open `Capture2Go.app`.

If macOS blocks it: **right-click the app → Open → Open**, or go to
**System Settings → Privacy & Security → Open Anyway**.
If it says the app is "damaged", run this once in a terminal (from the folder containing the app):

```bash
xattr -cr Capture2Go.app
```

Use the **USB** connection on macOS (Bluetooth is not configured in this build).

### Linux
```bash
chmod +x Capture2Go     # only needed once
./Capture2Go
```

---

## First-time setup: Linux serial port permission

> **Sensor not detected on Linux?**

Your user account may not have permission to access the USB serial port.
Run this command **once** in a terminal:

```bash
sudo usermod -aG dialout $USER
```

Then **log out and back in** (or reboot). Verify with:

```bash
groups   # "dialout" should appear in the list
```

---

## How to use the app

1. Connect the Capture2Go sensor with a **USB data cable** (charge-only cables do not work) and make sure it is switched on.
2. Launch the application.
3. Enter your **full name** and your **Matrikel-Nr. / student ID**, then click **Continue**.
4. In the connection dialog, select **USB** (default) or **Bluetooth (BLE)**.
   - For BLE: type the device name (e.g. `IMU_ab1234`).
5. Click **Connect**.
6. The dashboard opens with:
   - **Left panel** — live numeric values for Signals A–D (3 channels each) and a packet counter.
   - **Right panel** — 4 real-time plots (4-second sliding window at 200 Hz).
   - **Top banner** — your name/ID and the number of samples recorded so far.
7. Use **Reconnect** if the connection drops or you want to switch the sensor.
8. When you are done, click **Stop & Export data** (or close the window).
   The recording is saved automatically and you are asked whether to open the folder.

---

## Exported data

Every session is saved when you stop or close the app, in:

| System | Location |
|--------|----------|
| Windows | `C:\Users\<you>\Documents\Capture2Go_Data\` |
| macOS | `/Users/<you>/Documents/Capture2Go_Data/` |
| Linux | `~/Documents/Capture2Go_Data/` |

Each session creates its own folder:

```
Capture2Go_Data/
└── <Name>_<StudentID>_<YYYYMMDD_HHMMSS>/
    └── data.csv
```

`data.csv` columns (200 samples per second):

| Column | Content |
|--------|---------|
| `time_s` | Time since the start of the recording (s) |
| `signal_1` – `signal_3` | Accelerometer x, y, z (m/s²) |
| `signal_4` – `signal_6` | Gyroscope x, y, z (deg/s) |

> Note: on screen, the gyroscope is shown as **Signal A** and the accelerometer
> as **Signal B**, so the column order in the CSV differs from the order of the plots.

Please keep the session folder and hand in `data.csv` as instructed by your lecturer.

---

## Troubleshooting

| Problem | What to try |
|---------|-------------|
| "Could not connect" / sensor not found | Check that the sensor is on, use a data cable, try another USB port, then press **Reconnect**. |
| Linux: permission denied | See *First-time setup* above. |
| Running in a virtual machine | The USB device must be passed to the VM (VirtualBox: **Devices → USB**). |
| "No data recorded" at the end | No packets arrived during the session; check the connection and repeat the measurement. |
| Antivirus flags the file | The executable is not code-signed. Add an exception or ask your lecturer for the source code. |

---

## Building the executables (for the lecturer)

PyInstaller builds executables **only for the system it runs on**. Build the
Windows version on Windows, the macOS version on a Mac, and the Linux version
on Linux. Use Python 3.12 or 3.13 (very new Python versions may lack library support).

Run all commands from the folder that contains `capture2go_gui.py`.

### Requirements (all systems)

```bash
pip install pyinstaller matplotlib numpy capture2go
```

On Linux, tkinter must also be installed: `sudo apt install python3-tk`.
On macOS, use the official installer from python.org (it includes tkinter).

### Windows → `dist\Capture2Go.exe`

```powershell
python -m PyInstaller --onefile --windowed --name Capture2Go --collect-all capture2go --noconfirm capture2go_gui.py
```

### Linux → `dist/Capture2Go`

```bash
python -m PyInstaller --onefile --name Capture2Go --collect-all capture2go --noconfirm capture2go_gui.py
```

### macOS → `dist/Capture2Go.app`

```bash
python -m PyInstaller --windowed --name Capture2Go --collect-all capture2go --noconfirm capture2go_gui.py
cd dist
ditto -c -k --keepParent Capture2Go.app Capture2Go-mac.zip
```

An app built on an Apple-silicon Mac runs only on Apple-silicon Macs; build on an
Intel Mac for Intel students.

### Cleaning old builds

Delete the `build/`, `dist/` and `*.spec` files before rebuilding if something looks stale.

### Running without building

```bash
python capture2go_gui.py
```

---

*Capture2Go SDK © 2025 SensorStim Neurotechnology GmbH — MIT License*

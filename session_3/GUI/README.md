# Capture2Go GUI – Sensor Dashboard (Student Version)

A standalone GUI application for real-time IMU sensor visualization.  
No Python installation required — just run the executable.

---

## Files in this folder

| File | Description |
|------|-------------|
| `capture2go_gui` | **Linux** executable (run directly) |
| `capture2go_gui.exe` | **Windows** executable *(build on Windows — see below)* |
| `capture2go_gui.app` | **macOS** app bundle *(build on macOS — see below)* |

---

## Running the application

### Linux
```bash
./capture2go_gui
```
Double-click also works in most file managers.

### Windows
Double-click `capture2go_gui.exe`.

### macOS
Double-click `capture2go_gui.app`.  
If macOS blocks it: **System Settings → Privacy & Security → Open Anyway**.

---

## First-time setup: Linux serial port permission

> **Sensor not detected on Linux?**

Your user account may not have permission to access the USB serial port.  
Fix it by running this command **once** in a terminal:

```bash
sudo usermod -aG dialout $USER
```

Then **log out and back in** (or reboot).  
You can verify it worked with:

```bash
groups   # "dialout" should appear in the list
```

---

## How to use the app

1. Connect the Capture2Go sensor via USB (or make sure BLE is on).
2. Launch the executable — a **connection dialog** will appear.
3. Select **USB** (default) or **Bluetooth (BLE)**.
   - For BLE: type the device name (e.g. `IMU_ab1234`).
4. Click **Connect**.
5. The dashboard opens with:
   - **Left panel** — live numeric values updated at 20 ms.
   - **Right panel** — 4 real-time plots (4-second sliding window at 200 Hz).
6. Click **Stop streaming** or close the window to disconnect.

---

## Building the executable on other platforms

The `.spec` file in the project root works on Windows, macOS, and Linux.

### Requirements
```bash
pip install pyinstaller matplotlib numpy capture2go
```

### Build command
```bash
# From the project root (imes_lehrenticklung/)
pyinstaller capture2go_gui.spec --distpath session_3/dist --noconfirm
```

This generates:
- **Linux** → `dist/capture2go_gui`
- **Windows** → `dist/capture2go_gui.exe`
- **macOS** → `dist/capture2go_gui` + `dist/capture2go_gui.app`

---

*Capture2Go SDK © 2025 SensorStim Neurotechnology GmbH — MIT License*


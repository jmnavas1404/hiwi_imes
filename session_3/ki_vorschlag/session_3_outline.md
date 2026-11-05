🗂️ [STRUCTURE]
**Session 3 — Motion Sensors: The Unlabelled Signals**
**Responsible:** Timo
**Target Audience:** Beginner Biomedical Engineering Bachelor students.
**Language:** English.
**Platform:** JupyterLite (no accounts required, runs in browser).
**Internal Notes:** 
- The live connection is simulated ("replay mode") until the hardware integration (Capture2Go / Movella DOT) is finalized. "REVIEW" markers are left for hardware integration.
- The 5th foot movement is still unspecified in the brief (only 4 listed).
- Need to align the exact CSV format (decimal separator, column names) with Session 4.

---

📝 [TEXT]
## Welcome to Session 3: The Unlabelled Signals
Today, you will see what a motion sensor sees. We have an IMU (Inertial Measurement Unit) that contains an accelerometer and a gyroscope. Together, they output 6 unlabelled signals. Your mission is to perform specific movements and guess which signal corresponds to which sensor and axis.

---

🗂️ [STRUCTURE]
**Block 1: IMU in the Hand (Labeling Game)**
Students run this block to see real-time (simulated) data while moving the sensor in their hands.

📝 [TEXT]
### Cell 1: Connection & Live Graph (Hand)
Run this cell to start seeing data from the IMU. Move the sensor in your hand in different directions. Watch how the 6 signals react!

💻 [CODE]
```python
# ==========================================
# 1. CONNECT TO IMU AND PLOT LIVE DATA
# ==========================================
# What it does: Starts a simulated live feed of 6 unlabelled signals from the IMU.
# Typical error: If you see "ModuleNotFoundError", make sure you ran the cell properly or re-load the page.

# ------------------------------------------
# YOU MAY CHANGE THIS
# ------------------------------------------
TIME_WINDOW_SECONDS = 10  # How many seconds of data to show on the screen at once
# ------------------------------------------

# REVIEW: Hardware connection to be implemented here (Capture2Go / Movella DOT)
# Currently running in REPLAY MODE using placeholder data logic.

import matplotlib.pyplot as plt
import numpy as np
import time
from IPython.display import display, clear_output

# Mock function to simulate live incoming data
def get_imu_data(t):
    return [
        np.sin(t), np.cos(t), np.sin(t/2), # Accelerometer mock
        np.cos(t/2), np.sin(t*2), np.cos(t*2) # Gyroscope mock
    ]

fig, ax = plt.subplots(figsize=(10, 5))
start_time = time.time()

# Simple loop to simulate live plotting (runs for 10 updates for demonstration)
# REVIEW: Real implementation will need asynchronous plotting or ipywidgets for JupyterLite
for _ in range(15):
    current_time = time.time() - start_time
    data = get_imu_data(current_time)
    
    # Plotting logic omitted for brevity in beginner view, wrapped in backend function ideally
    print(f"Time: {current_time:.1f}s | Signal 1: {data[0]:.2f} | Signal 2: {data[1]:.2f} | ...")
    time.sleep(0.5)
    clear_output(wait=True)
    
print("Live feed paused.")
```

---

🗂️ [STRUCTURE]
**Block 2: IMU on the Foot**
Students strap the IMU to their foot and perform 4 (or 5) specific movements.

📝 [TEXT]
### Cell 2: Foot Movements
Now, strap the IMU to your foot. Run this cell to record your foot movements.

💻 [CODE]
```python
# ==========================================
# 2. RECORD FOOT MOVEMENTS
# ==========================================
# What it does: Records a fixed window of data while you perform your foot movements.

# ------------------------------------------
# YOU MAY CHANGE THIS
# ------------------------------------------
RECORDING_TIME_SECONDS = 30  # Adjust this if you need more time to do all movements
# ------------------------------------------

print(f"Starting recording for {RECORDING_TIME_SECONDS} seconds...")
print("Please perform your movements now!")
# REVIEW: Trigger recording logic from real sensor here.
time.sleep(2) # Mock wait
print("Recording complete! Data stored in memory.")
```

---

🗂️ [STRUCTURE]
**Block 3: The Mystery Recording**
Students record an unknown movement for another group to guess.

📝 [TEXT]
### Cell 3: The Mystery Recording
Run this cell to make a secret 15-second recording. Don't let the other groups see what movement you are doing!

💻 [CODE]
```python
# ==========================================
# 3. MYSTERY RECORDING
# ==========================================
# What it does: Records a short burst of data to challenge other groups.

# ------------------------------------------
# YOU MAY CHANGE THIS
# ------------------------------------------
MYSTERY_DURATION = 15  # Keep it between 10 and 20 seconds
# ------------------------------------------

print(f"Shhh... Secret recording started for {MYSTERY_DURATION} seconds.")
# REVIEW: Trigger recording logic.
time.sleep(2) # Mock wait
print("Mystery recording saved!")
```

---

🗂️ [STRUCTURE]
**Block 4: Exporting Data and Labels**
Critical step to bridge Session 3 and Session 4. 

📝 [TEXT]
### Cell 4: Export Your Data and Labels
Run this final cell to save your data into a CSV file, and to save your guessed labels so you can use them in Session 4.

💻 [CODE]
```python
# ==========================================
# 4. EXPORT DATA AND LABELS
# ==========================================
# What it does: Generates two CSV files that you will download and save for Session 4.

# ------------------------------------------
# YOU MAY CHANGE THIS
# ------------------------------------------
GROUP_NAME = "Group_1"  # Put your group number or name here, no spaces!

# Fill in your guessed labels below based on your experiments!
# Options typically involve: Accel X, Accel Y, Accel Z, Gyro X, Gyro Y, Gyro Z
LABEL_SIGNAL_1 = "Unknown"
LABEL_SIGNAL_2 = "Unknown"
LABEL_SIGNAL_3 = "Unknown"
LABEL_SIGNAL_4 = "Unknown"
LABEL_SIGNAL_5 = "Unknown"
LABEL_SIGNAL_6 = "Unknown"
# ------------------------------------------

# REVIEW: CSV formatting. Need to ensure time column is 'time_s', decimal separator matches regional settings.
import csv

data_filename = f"{GROUP_NAME}_data.csv"
labels_filename = f"{GROUP_NAME}_labels.csv"

# Mock saving data
print(f"Saving data to {data_filename}...")
# Mock saving labels
with open(labels_filename, 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['Signal', 'Label'])
    writer.writerow(['signal_1', LABEL_SIGNAL_1])
    writer.writerow(['signal_2', LABEL_SIGNAL_2])
    writer.writerow(['signal_3', LABEL_SIGNAL_3])
    writer.writerow(['signal_4', LABEL_SIGNAL_4])
    writer.writerow(['signal_5', LABEL_SIGNAL_5])
    writer.writerow(['signal_6', LABEL_SIGNAL_6])

print(f"Labels saved to {labels_filename}.")
print("DONE! Please download these files from your JupyterLite file browser on the left.")
# REVIEW: Add instructions on where students must upload this (e.g., shared drive folder) for Session 4.
```
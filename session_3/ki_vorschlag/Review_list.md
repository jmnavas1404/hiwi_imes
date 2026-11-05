**Open points / REVIEW list (KI-Generated):**
- REVIEW: Hardware connection (Bluetooth / Capture2Go / Movella DOT) is not implemented. Everything runs in REPLAY MODE (simulated data) until it is finalized.
- REVIEW: Sampling frequency is provisional (`SAMPLING_RATE_HZ = 30`). Confirm the real value of the device.
- REVIEW: Only 4 foot movements are specified in the brief. The 5th is still open (placeholder in Cell 2).
- REVIEW: Signal order is FIXED (Signal 1 to Signal 6) and must be identical in Session 4. Internal mapping (hidden from students) must be confirmed with the real device channel order.
- REVIEW: Align the CSV format with Session 4 (column names, `time_s`, decimal separator, units).
- REVIEW: Where students upload their files (group folder) is undefined.
- REVIEW: Check that `await asyncio.sleep` and live plot refresh work in the target JupyterLite kernel (Pyodide). `time.sleep` would freeze the page.
- REVIEW: Prepare the predefined LLM prompts for the in-browser assistant (e.g. "Explain what this cell does", "Help me change the time window").
# Capture2Go - macOS Installation and Troubleshooting Guide

This document provides instructions for running the Capture2Go application on macOS, along with development notes for troubleshooting common errors when executing the source code or compiling the app.

## How to run the application (For Users)

After downloading and extracting the `Capture2Go.zip` file, you will have the executable application. Because the app is not signed with an official Apple Developer certificate, macOS Gatekeeper will block it if you try to open it with a standard double-click.

To open it for the first time, follow these steps:

1. Do not double-click the application.
2. Right-click (or Control + click) the `Capture2Go` icon.
3. Select "Open" from the context menu.
4. A warning message will appear stating that the developer cannot be verified, but this time it will include an "Open" button.
5. Click "Open". The application will launch normally.

*Note: This process is only required the first time. Afterwards, you can launch the app with a normal double-click like any other application.*

## Development and Build Notes (For Developers)

If you are running the original Python script (`.py`) or packaging the application using PyInstaller on macOS, you might encounter the following errors. Here is how to fix them:

### 1. Encoding Syntax Error (Non-ASCII character)

**Error:** `SyntaxError: Non-ASCII character '\xe2' in file...`
**Cause:** The system is attempting to run the script using Python 2.7 (the default for the `python` command on older macOS versions), which does not support the UTF-8 characters used in the script.
**Solution:** Explicitly use Python 3.

```bash
# Incorrect:
python capture2go_gui_mac.py

# Correct:
python3 capture2go_gui_mac.py
```

### 2. PyInstaller Error (Missing developer tools)

**Error:** `SystemError: lipo command failed with error code 1! output: xcode-select: note: no developer tools were found...`
**Cause:** macOS is missing the Apple Command Line Developer Tools required to build the file architecture.
**Solution:** Install the tools by running the following command in the terminal and following the on-screen prompts:

```bash
xcode-select --install
```

### 3. Persistent PyInstaller Error (Tools already installed)

**Error:** When trying to install with `xcode-select --install`, the system says `command line tools are already installed`, but PyInstaller still fails.
**Cause:** The developer tools path is corrupted or misconfigured (common in virtual machine environments).
**Solution:**
First, try resetting the default path:

```bash
sudo xcode-select --reset
```
*(You will be prompted to enter your Mac password).*

If that does not work, remove the current installation and reinstall:

```bash
# 1. Delete the current folder:
sudo rm -rf /Library/Developer/CommandLineTools

# 2. Reinstall:
xcode-select --install
```
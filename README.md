# BOIIIWD - Linux Version

A Feature-rich GUI Steam Workshop downloader for [Call of Duty: Black Ops III](https://store.steampowered.com/app/311210/Call_of_Duty_Black_Ops_III/) built using CustomTkinter.

> **WARNING: This is an experimental/testing release. Linux support is still in development and may have bugs or issues.**

## Requirements

### System Dependencies

Before running BOIIIWD, you need to install the following system packages:

```bash
# Debian/Ubuntu
sudo apt-get update
sudo apt-get install python3-tk lib32gcc-s1

# For 32-bit architecture support (required by SteamCMD)
sudo dpkg --add-architecture i386
sudo apt-get update
sudo apt-get install lib32gcc-s1
```

```bash
# Fedora
sudo dnf install python3-tkinter glibc.i686 libgcc.i686
```

```bash
# Arch Linux
sudo pacman -S tk lib32-gcc-libs
```

### Why these dependencies?

- **python3-tk / tkinter**: Required for the GUI (CustomTkinter is built on tkinter)
- **lib32gcc-s1 / 32-bit libraries**: SteamCMD is a 32-bit application and requires 32-bit libraries to run

## Quick Install

```bash
# Download
wget https://github.com/faroukbmiled/BOIIIWD/releases/latest/download/Linux.zip

# Extract and make executable
unzip Linux.zip && chmod +x BOIIIWD

# Run
./BOIIIWD
```

> **Tip:** Run from terminal to see live output and debug information.

## Building from Source

```bash
# Install Python dependencies
pip install -r requirements.txt

# Build executable
python build.py

# Run
./BOIIIWD
```

## Configuration

BOIIIWD stores its configuration in `~/.config/boiiiwd/`:

- `config.ini` - Application settings
- `geometry.ini` - Window position/size
- `boiiiwd.log` - Log file (viewable via Settings > View Logs)
- `boiiiwd_library.json` - Downloaded items library

## SteamCMD Notes

- SteamCMD will be downloaded automatically if not installed
- SteamCMD stores its data in `~/Steam/` (not in the steamcmd installation folder)
- First-time initialization may take a while depending on your internet speed

## Troubleshooting

### "No module named 'tkinter'"
Install the tkinter package for your distribution (see Requirements above).

### SteamCMD fails to run
Make sure 32-bit libraries are installed:
```bash
sudo dpkg --add-architecture i386
sudo apt-get update
sudo apt-get install lib32gcc-s1
```

### GUI doesn't start / Display issues
Make sure you have a display server running (X11 or Wayland). If using WSL, ensure WSLg is working or use an X server like VcXsrv.

### Download stuck / No progress
Run from terminal to see detailed output. SteamCMD logs are stored in `~/Steam/logs/`.

## Links

- [Main Repository (Windows)](https://github.com/faroukbmiled/BOIIIWD)
- [Report Issues](https://github.com/faroukbmiled/BOIIIWD/issues)
- [Latest Release](https://github.com/faroukbmiled/BOIIIWD/releases/latest)

## Disclaimer

This is an experimental Linux port. Some features may not work as expected. Please report issues on the [GitHub repository](https://github.com/faroukbmiled/BOIIIWD/issues).

---

**Encryption Note:** You can set the environment variable `BOIIIWD_ENC_KEY` for encrypting your steam username. Generate a valid key with:
```python
import base64, os
print(base64.urlsafe_b64encode(os.urandom(32)).decode())
```

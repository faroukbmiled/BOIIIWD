#!/usr/bin/env python3
import os
import sys
import subprocess

class TeeOutput:
    """Write output to both stdout/stderr and a log file."""
    def __init__(self, original, log_file_path):
        self.original = original
        self.log_file_path = log_file_path
        os.makedirs(os.path.dirname(log_file_path), exist_ok=True)

    def write(self, message):
        self.original.write(message)
        try:
            with open(self.log_file_path, 'a', encoding='utf-8', errors='replace') as f:
                f.write(message)
        except Exception:
            pass

    def flush(self):
        self.original.flush()

def setup_logging():
    """Set up logging to file for console display feature."""
    xdg_config = os.environ.get("XDG_CONFIG_HOME", os.path.expanduser("~/.config"))
    log_file = os.path.join(xdg_config, "boiiiwd", "boiiiwd.log")

    # Clear old log on startup
    try:
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
        with open(log_file, 'w', encoding='utf-8') as f:
            from datetime import datetime
            f.write(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] BOIIIWD started\n")
    except Exception:
        pass

    # Redirect stdout and stderr to both console and log file
    sys.stdout = TeeOutput(sys.__stdout__, log_file)
    sys.stderr = TeeOutput(sys.__stderr__, log_file)

# Set up logging before anything else
setup_logging()

def check_linux_dependencies():
    """Check if required 32-bit libraries are installed for SteamCMD."""
    # Check if lib32gcc is installed
    try:
        result = subprocess.run(['dpkg', '-l', 'lib32gcc-s1'], capture_output=True, text=True)
        if 'ii' not in result.stdout:
            # Also try older package name
            result = subprocess.run(['dpkg', '-l', 'lib32gcc1'], capture_output=True, text=True)
            if 'ii' not in result.stdout:
                return False
        return True
    except FileNotFoundError:
        # dpkg not found (not Debian-based), skip check
        return True
    except Exception:
        return True  # Don't block on check failure

def show_dependency_warning():
    """Show a warning dialog about missing dependencies."""
    try:
        import tkinter as tk
        from tkinter import messagebox

        root = tk.Tk()
        root.withdraw()

        msg = """SteamCMD requires 32-bit libraries to run.

Please install them by running:

    sudo dpkg --add-architecture i386
    sudo apt-get update
    sudo apt-get install lib32gcc-s1

After installing, restart BOIIIWD."""

        messagebox.showwarning("Missing Dependencies", msg)
        root.destroy()
    except Exception as e:
        # Fallback to console message
        print("\n" + "="*50)
        print("WARNING: Missing 32-bit libraries for SteamCMD!")
        print("="*50)
        print("\nPlease run:")
        print("    sudo dpkg --add-architecture i386")
        print("    sudo apt-get update")
        print("    sudo apt-get install lib32gcc-s1")
        print("\nThen restart BOIIIWD.")
        print("="*50 + "\n")

# Check dependencies on startup
if not check_linux_dependencies():
    show_dependency_warning()

import src.shared_vars as main_app

if __name__ == "__main__":
    main_app.app.mainloop()

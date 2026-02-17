import PyInstaller.__main__
import os

NAME = "BOIIIWD"
SCRIPT = "boiiiwd_package/boiiiwd.py"
ICON = "boiiiwd_package/resources/ryuk.png"

args = [
    f"{SCRIPT}",
    '--name', f"{NAME}",
    "--noconfirm",
    "--onefile",
    "--add-data", "boiiiwd_package/resources:resources",
    "--add-data", "boiiiwd_package/src:imports",
    "--add-data", "boiiiwd_package/src:winpty_patch",
    "--add-data", "boiiiwd_package/src:helpers",
    "--add-data", "boiiiwd_package/src:shared_vars",
    "--add-data", "boiiiwd_package/src:library_tab",
    "--add-data", "boiiiwd_package/src:settings_tab",
    "--add-data", "boiiiwd_package/src:update_window",
    "--add-data", "boiiiwd_package/src:main",
    "--distpath", ".",
    "--hidden-import", "pexpect",
    "--hidden-import", "ptyprocess",
    "--hidden-import", "PIL._tkinter_finder",
    "--collect-submodules", "PIL",
]

if os.path.exists(ICON):
    args.extend(["--icon", f"{ICON}"])

PyInstaller.__main__.run(args)

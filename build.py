import os
import PyInstaller.__main__

NAME = "BOIIIWD"
SCRIPT = "boiiiwd_package/boiiiwd.py"
ICON = "boiiiwd_package/resources/ryuk.ico"

PyInstaller.__main__.run([
    f"{SCRIPT}",
    '--name', f"{NAME}",
    "--noconfirm",
    "--onefile",
    "--noconsole",
    "--icon", f"{ICON}",
    "--add-data", "boiiiwd_package/resources:resources",
    "--add-data", "boiiiwd_package/src:imports",
    "--add-data", "boiiiwd_package/src:winpty_patch",
    "--add-data", "boiiiwd_package/src:helpers",
    "--add-data", "boiiiwd_package/src:shared_vars",
    "--add-data", "boiiiwd_package/src:library_tab",
    "--add-data", "boiiiwd_package/src:settings_tab",
    "--add-data", "boiiiwd_package/src:update_window",
    "--add-data", "boiiiwd_package/src:main",
])

# create symbolic hardlink to main directory
if os.path.exists("BOIIIWD.exe"):
    os.remove("BOIIIWD.exe")
os.link('dist/BOIIIWD.exe', 'BOIIIWD.exe')

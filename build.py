import os
import PyInstaller.__main__
from distutils.sysconfig import get_python_lib

site_packages_path = get_python_lib()

NAME = "BOIIIWD"
SCRIPT = "boiiiwd_package/boiiiwd.py"
ICON = "boiiiwd_package/resources/ryuk.ico"

PyInstaller.__main__.run([
    "{}".format(SCRIPT),
    '--name', f"{NAME}",
    "--noconfirm",
    "--onefile",
    # "--windowed",
    # "--noconsole",
    "--hide-console", "hide-early",
    "--icon", f"{ICON}",
    "--add-data", "boiiiwd_package/resources;resources",
    "--add-data", "boiiiwd_package/src;imports",
    "--add-data", "boiiiwd_package/src;helpers",
    "--add-data", "boiiiwd_package/src;shared_vars",
    "--add-data", "boiiiwd_package/src;library_tab",
    "--add-data", "boiiiwd_package/src;settings_tab",
    "--add-data", "boiiiwd_package/src;update_window",
    "--add-data", "boiiiwd_package/src;main",
    "--add-data", f"{site_packages_path}/customtkinter;customtkinter",
    "--add-data", f"{site_packages_path}/CTkMessagebox;CTkMessagebox",
    "--add-data", f"{site_packages_path}/CTkToolTip;CTkToolTip",
    # "--add-data", f"{site_packages_path}/winpty;winpty",
])

# create symbolic hardlink to main directory
if os.path.exists("BOIIIWD.exe"):
    os.remove("BOIIIWD.exe")
os.link('dist/BOIIIWD.exe', 'BOIIIWD.exe')

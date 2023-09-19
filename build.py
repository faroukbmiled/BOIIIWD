import PyInstaller.__main__
from distutils.sysconfig import get_python_lib

site_packages_path = get_python_lib()

NAME = "BOIIIWD"
SCRIPT = "boiiiwd.py"
ICON = "boiiiwd_package/ryuk.ico"

PyInstaller.__main__.run([
    "{}".format(SCRIPT),
    '--name', f"{NAME}",
    "--noconfirm",
    "--onefile",
    "--windowed",
    "--ascii",
    "--icon", f"{ICON}",
    "--add-data", "boiiiwd_package/src/resources;resources",
    "--add-data", f"{site_packages_path}\customtkinter;customtkinter",
    "--add-data", f"{site_packages_path}\CTkMessagebox;CTkMessagebox",
    "--add-data", f"{site_packages_path}\CTkToolTip;CTkToolTip",
])

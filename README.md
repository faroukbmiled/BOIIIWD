# BOIIIWD
- A GUI Steam Workshop downloader meant for BO3 ([boiii client](https://github.com/Ezz-lol/boiii-free)) built using PyQt5 <br>
![image](https://github.com/faroukbmiled/BOIIIWD/assets/51106560/d66a09bf-9601-4443-a08e-217721671adb)

## Usage (exe):
- Run [BOIIIWD.exe](https://github.com/faroukbmiled/BOIIIWD/releases/latest/download/Release.zip) and use it (it'll ask you to download steamcmd within the app if not found)
- That's it slap in your workshop item link or just the id then hit Download and wait for it to finish, when it does just launch your game (Please check [Notes](#notes) before you ask anything)

## Usage (script):
- ```pip install -r requirements.txt```
- ```python boiiiwd.py```
- Slap in your workshop item link for example: "https://steamcommunity.com/sharedfiles/filedetails/?id=3011930738" or just the id 3011930738)

## Compiling into an exe (pyinstaller):
- ```pip install pyinstaller```
- ```pyinstaller --noconfirm --onefile --windowed --icon "ryuk.ico" --name "BOIIIWD" --ascii  "boiiiwd.py"```

<a name="notes"></a>
### Notes:
. It saves your input except for workshop id <br>
. Excuse the progress bar its pretty shit atm, will be working on it <br>
. If you do not know where to find your map in-game check this [video](https://youtu.be/XIQjfXXlgQs?t=260) out ,for mods find "mods" in the game's main menu <br>
. Initializing SteamCMD for the first time could take some time depending on your internet speed <br>
. If the download fails when getting big maps its SteamCMD's fault, still working on a workaround

# BOIIIWD
- A GUI Steam Workshop downloader meant for BO3 (boiii client) built using PyQt5 <br>
![image](https://github.com/faroukbmiled/BOIIIWD/assets/51106560/2395fe6d-a92e-4ac5-93d2-4b42130f700c)

## Usage (exe):
- (optional) Download and Run [steamcmd.exe](https://steamcdn-a.akamaihd.net/client/installer/steamcmd.zip) to initialize it first (in the same dir as the script/exe) -> Should only be done once
- Run [BOIIIWD.exe](https://github.com/faroukbmiled/BOIIIWD/releases/download/v0.1.2/Release.zip) and use it (it'll ask you to download steamcmd within the app if not found)
- That's it put in your map/mod workshop id then hit Download and wait for it to finish, when it does just launch your game (Please check [Notes](#notes) before you ask something)

## Usage (script):
- ```pip install -r requirements.txt```
- ```python boiiiwd.py```
- To get a workshop id look at the link and get the id from it lol (For example: this workshop link "https://steamcommunity.com/sharedfiles/filedetails/?id=3011930738" 3011930738 would be the workshop id)
* ![image](https://github.com/faroukbmiled/BOIIIWD/assets/51106560/79b7a4f8-894e-4d50-a885-eabed6e5be4e)

## Compiling into an exe (pyinstaller):
- ```pip install pyinstaller```
- ```pyinstaller --noconfirm --onefile --windowed --icon "ryuk.ico" --name "BOIIIWD" --ascii  "boiiiwd.py"```

<a name="notes"></a>
### Notes:
. It saves your input except for workshop id <br>
. Excuse the progress bar its pretty shit atm, will be working on it <br>
. If you do not know where to find your map in-game check this [video](https://youtu.be/XIQjfXXlgQs?t=260) out ,for mods find "mods" in the game's main menu

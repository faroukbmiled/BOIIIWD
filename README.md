# BOIIIWD
- A GUI Steam Workshop downloader meant for BO3 (boiii client) built using PyQt5 <br>
![image](https://github.com/faroukbmiled/BOIIIWD/assets/51106560/2395fe6d-a92e-4ac5-93d2-4b42130f700c)

## release:
- (optional) Download the [release](https://github.com/faroukbmiled/BOIIIWD/releases/tag/Release) zip which has everything you need
- (optional) Run steamcmd.exe to initialize it first -> Should only be done once
- Run [BOIIIWD.exe](https://github.com/faroukbmiled/BOIIIWD/releases/download/v0.1.2/Release.zip) and use it (it'll ask you to download steamcmd if not found)
  
## Pre Usage:
- Place [SteamCMD](https://steamcdn-a.akamaihd.net/client/installer/steamcmd.zip) in the script's folder, and execute it to initiate SteamCMD.
  
## Usage:
- ```pip install -r requirements.txt```
- ```python boiiiwd.py```
- to get a workshop id look at the link and get the id from it lol (For example: this workshop link "https://steamcommunity.com/sharedfiles/filedetails/?id=3011930738" 3011930738 would be the workshop id)

## Compiling into an exe (pyinstaller):
- ```pip install pyinstaller```
- ```pyinstaller --noconfirm --onefile --windowed --icon "ryuk.ico" --name "BOIIIWD" --ascii  "boiiiwd.py"```
  
### Notes:
. It saves your input except workshop id <br>
. Excuse the progress bar its pretty shit atm

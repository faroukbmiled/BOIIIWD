# BOIIIWD
- A GUI Workshop downloader meant for BO3 (boiii) built using PyQt5 <br>
![image](https://github.com/faroukbmiled/BOIIIWD/assets/51106560/516daa16-e349-44b9-90cb-01718309f357)


## Pre Usage:
- Place [SteamCMD](https://steamcdn-a.akamaihd.net/client/installer/steamcmd.zip) inside the same folder as the script and run it to let it update and install
  
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

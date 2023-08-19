# BOIIIWD
- A GUI Steam Workshop downloader meant for BO3 ([boiii client](https://github.com/Ezz-lol/boiii-free)) built using CustomTkinter <br>

<p float="left">
  <img src="https://github.com/faroukbmiled/BOIIIWD/assets/51106560/5197f0d8-9bf9-4dbb-bef7-748e7d7aaad2" width="800" />
  <img src="https://github.com/faroukbmiled/BOIIIWD/assets/51106560/c3b5e658-bc59-4757-becd-a09ce5a4035e" width="800" /> 
  <img src="https://github.com/faroukbmiled/BOIIIWD/assets/51106560/710ab04c-d289-43db-9dc7-4801b074a701" width="800" />
</p>

## Usage (exe):
- Run [BOIIIWD.exe](https://github.com/faroukbmiled/BOIIIWD/releases/latest/download/Release.zip) and use it (it'll ask you to download steamcmd within the app if not found)
- That's it slap in your workshop item link or just the id then hit Download and wait for it to finish, when it does just launch your game (Please check [Notes](#notes) before you ask anything)

## Usage (script):
- ```pip install -r requirements.txt```
- ```python boiiiwd.py```
- Slap in your workshop item link for example: "https://steamcommunity.com/sharedfiles/filedetails/?id=3011930738" or just the id 3011930738)

## Freezing into an exe (pyinstaller):
- ```pip install -r requirements.txt```
- ```pip install pyinstaller```
- ```pyinstaller --noconfirm --onefile --windowed --icon "ryuk.ico" --name "BOIIIWD" --ascii  "boiiiwd.py" --add-data "resources;resources" --add-data "c:\<python_path>\lib\site-packages\customtkinter;customtkinter\" --add-data "c:\<python_path>\lib\site-packages\CTkMessagebox;CTkMessagebox\" --add-data "c:\<python_path>\lib\site-packages\CTkToolTip;CTkToolTip\"```

<a name="notes"></a>
### Notes:
. It saves your input except for workshop id <br>
. If you do not know where to find your map in-game check this [video](https://youtu.be/XIQjfXXlgQs?t=260) out ,for mods find "mods" in the game's main menu <br>
. Initializing SteamCMD for the first time could take some time depending on your internet speed <br>
. If the download fails when getting big maps its SteamCMD's fault, still working on a workaround <br>

. Known bugs: <br>
. Rare UI bug => instead of showing a warning message, its window goes invisible and leads to the whole ui becoming unclickable (end the task from task manager) <br>
. Possible logic bugs related to the progress bar , sometimes it carries on progressing when you pressed stop => please raise an issue if this happens often <br>
  
### todos:
- [x] add a menu that shows you current installed mods/maps
- [x] fix the progress bar => progress bar logic based on an estimation
- [x] other improvements regarding the download (steamcmd likes to fail sometimes for no reason) => added a way to keep looping when steamcmd crashes and it will eventually finishes
- [ ] add a queue window that you can slap in a bunch of items to download sequentially and or simultaneously
- [ ] add an option to login with your account => delayed (do we really need it?)


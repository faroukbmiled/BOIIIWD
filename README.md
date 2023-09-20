# BOIIIWD
- A Feature-rich GUI Steam Workshop downloader for BO3 ([boiii client](https://github.com/Ezz-lol/boiii-free)) built using CustomTkinter <br>

<div style="display: flex; justify-content: space-between;">
  <!-- Left Side -->
  <div style="flex: 1; margin-right: 5px;">
    <img src="https://github.com/faroukbmiled/BOIIIWD/assets/51106560/0aa8295f-ba07-4778-8140-200021df4ba9" width="400" />
    <img src="https://github.com/faroukbmiled/BOIIIWD/assets/51106560/b4f27fe1-88f2-4158-b7ba-c8aec57b9968" width="400" />
  </div>
  <!-- Right Side -->
  <div style="flex: 1; margin-left: 5px;">
    <img src="https://github.com/faroukbmiled/BOIIIWD/assets/51106560/76f74154-b239-4b39-a2af-fd6c4ecb4043" width="400" />
    <img src="https://github.com/faroukbmiled/BOIIIWD/assets/51106560/229f2e70-b32b-4911-9a82-586e6dd55ae9" width="400" />
  </div>
</div>

## Usage (exe):
- Run [BOIIIWD.exe](https://github.com/faroukbmiled/BOIIIWD/releases/latest/download/Release.zip) and use it (it'll ask you to download steamcmd within the app if not found)
- That's it slap in your workshop item link or just the id then hit Download and wait for it to finish, when it does just launch your game (Please check [Notes](#notes) before you ask anything)
- If the exe is getting flagged as a virus by your ac it is obviously a false positive, if you still do not trust it you can [compile/freeze](#freezing) it yourself ([VirusTotal Scan](https://www.virustotal.com/gui/file/5ca1367a82893a1f412b59a52431e9ac4219a67a50c294ee86a7d41473826b14/detection))

## Usage (script):
- ```pip install -r requirements.txt``` -> use my modified [CTkToolTip](./CTkToolTip) and [CTkListbox](./CTkListbox) for [v0.2.8](https://github.com/faroukbmiled/BOIIIWD/releases) and up
- ```python boiiiwd_package\boiiiwd.py```
- Slap in your workshop item link for example: "https://steamcommunity.com/sharedfiles/filedetails/?id=3011930738" or just the id 3011930738)

## Features:
- Improves steamcmd's stability while downloading
- Auto installs mods and maps to boiii
- Queue -> download items in queue
- Library tab -> lists your downloaded items
- Item updater -> Checks your items for updates (redownloads them,no way for now to "update" them only) -> Under Library tab
- Steam to boiii -> Item mover (moves items (mods,maps) from steam to boiii client) -> Under settings tab
- Themes -> Under settings tab
- Bunch of useful settings -> Under settings tab

<a name="freezing"></a>
## Freezing into an exe (pyinstaller):
- ```pip install -r requirements.txt``` -> use my modified [CTkToolTip](./CTkToolTip) and [CTkListbox](./CTkListbox) for [v0.2.8](https://github.com/faroukbmiled/BOIIIWD/releases) and up.
- ```python build.py```

## Queue tab (beta)

- added Queue tab which has a text field that you can slap in workshop ids/links in 2 formats, for example:<br>


```3010399939,2976006537,2118338989``` 
or <br>
```3010399939
2976006537
2118338989
2113146805
```

<a name="notes"></a>
### Notes:
* It saves your input except for workshop id <br>
* If you do not know where to find your map in-game check this [video](https://youtu.be/XIQjfXXlgQs?t=260) out ,for mods find "mods" in the game's main menu <br>
* Initializing SteamCMD for the first time could take some time depending on your internet speed <br>
* New item update window: Right click on an item (mouse3) -> will open the item in the browser (Steam Workshop) <br>
* BOIIIWD requires having "boiiiwd_library.json" in the app's directory for the new features to work -> clicking on the library tab will generate the JSON file (please don't touch it) <br>
#### PS (Library tab): <br>
* Mouse1 -> copy id <br>
* Mouse2 (scroll wheel btn) -> Open item path in explorer <br>
* Mouse3 -> Copy path <br>
* Ctrl + Mouse 1 (after Mouse1) -> Append to clipboard

### Known bugs: <br>
* Rare UI bug => instead of showing a warning message, its window goes invisible and leads to the whole ui becoming unclickable (end the task from task manager) <br>
* Possible logic bugs related to the progress bar , sometimes it carries on progressing when you pressed stop => please raise an issue if this happens often <br>
* If the exe is getting flagged as a virus by your ac it is obviously a false positive, if you still do not trust it you can [compile/freeze](#freezing) it yourself <br>
* [VirusTotal](https://www.virustotal.com/gui/file/5ca1367a82893a1f412b59a52431e9ac4219a67a50c294ee86a7d41473826b14/detection) <br>
  
### todos:
- [x] add a menu that shows you current installed mods/maps
- [x] fix the progress bar => progress bar logic based on an estimation
- [x] other improvements regarding the download (steamcmd likes to fail sometimes for no reason) => added a way to keep looping when steamcmd crashes and it will eventually finishes
- [x] add a queue window that you can slap in a bunch of items to download sequentially and or simultaneously
- [ ] add an option to login with your account => delayed (do we really need it?)

### Themes:
- If you choose "custom" theme a file called boiiiwd_theme.json will be created in the current folder (where the exe at) , Don't add anything or edit any keyes just modify the colours, If you mess up something you can just rename the file and it'll go back to the default theme (you can always press custom again and the file will be created again, based on which theme you choose before)

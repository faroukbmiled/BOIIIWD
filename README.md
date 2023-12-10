# BOIIIWD
- A Feature-rich GUI Steam Workshop downloader for [Call of Duty®: Black Ops III](https://store.steampowered.com/app/311210/Call_of_Duty_Black_Ops_III/) built using CustomTkinter <br>

<div style="display: flex; justify-content: space-between;">
  <!-- Left Side -->
  <div style="flex: 1; margin-right: 5px;">
    <img src="https://github.com/faroukbmiled/BOIIIWD/assets/51106560/0aa8295f-ba07-4778-8140-200021df4ba9" width="400" />
    <img src="https://github.com/faroukbmiled/BOIIIWD/assets/51106560/b4f27fe1-88f2-4158-b7ba-c8aec57b9968" width="400" />
  </div>
  <!-- Right Side -->
  <div style="flex: 1; margin-left: 5px;">
    <img src="https://github.com/faroukbmiled/BOIIIWD/assets/51106560/86c07cf2-b04b-42d0-ae06-8526bffafb34" width="400" />
    <img src="https://github.com/faroukbmiled/BOIIIWD/assets/51106560/4c5877eb-81a7-4ae7-99db-3096ab57b12b" width="400" />
  </div>
</div>

## Usage:
- Run [BOIIIWD.exe](https://github.com/faroukbmiled/BOIIIWD/releases/latest/download/Release.zip) ([VirusTotal Scan](https://www.virustotal.com/gui/file/5ca1367a82893a1f412b59a52431e9ac4219a67a50c294ee86a7d41473826b14/detection))
- [Optional] Run as script:```python boiiiwd_package\boiiiwd.py```

## Features:
- Improved download stability
- Auto installs mods and maps
- Queue -> download items in queue
- Library tab -> lists your downloaded items
- Item updater -> checks your items for updates
- Workshop Transfer -> copy/move items from the workshop folder into the game directory
- Custom Themes

## Notes:

- Steamcmd will be downloaded if it is not installed <br>
- Initializing SteamCMD for the first time could take some time depending on your internet speed <br>

#### Mouse Bindings:
  Library Tab:

    * Mouse1 -> copy id
    * Ctrl + Mouse1 -> append to clipboard
    * Mouse2 (scroll wheel button) -> open item path in file explorer
    * Mouse3 (Right click) -> copy path

## Building from Source:
- ```pip install -r requirements.txt``` -> use my modified [CTkToolTip](./CTkToolTip) and [CTkListbox](./CTkListbox)
- ```python build.py```

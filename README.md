# BOIIIWD
- A Feature-rich GUI Steam Workshop downloader for [Call of Duty®: Black Ops III](https://store.steampowered.com/app/311210/Call_of_Duty_Black_Ops_III/) built using CustomTkinter <br>

<table>
  <tr>
    <td align="center">
      <img src="https://github.com/faroukbmiled/BOIIIWD/assets/51106560/4d199e21-c9a0-4dfc-b831-866fbff1d1a1" max-width="400" />
    </td>
    <td align="center">
      <img src="https://github.com/faroukbmiled/BOIIIWD/assets/51106560/25174889-4524-455f-9836-f4ea5240e07f" max-width="400" />
    </td>
    <td align="center">
      <img src="https://github.com/faroukbmiled/BOIIIWD/assets/51106560/df54a0d7-f9ab-4061-b8b7-06d9e5992c90" max-width="400" />
    </td>
  </tr>
</table>

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

## Login and Download Stability:
Logging in can significantly improve download stability, as reported by some users online. If you're having trouble figuring out how to log in, follow the detailed tutorial provided in the [LOGIN.md](./md/LOGIN.md) file.

---

**Disclaimer:** You can change/add the environment variable `BOIIIWD_ENC_KEY` used for encrypting your steam username to whatever you want. You can use [this helper function](./utils/enc_key_gen.py) to generate a valid key for you.
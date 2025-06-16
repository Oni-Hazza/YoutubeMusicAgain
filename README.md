# 🎵 YT Music Again (PyQt6 + VLC)

A desktop application for playing music using YouTube and VLC, built with Python and PyQt6.

---

## 📦 Features

- Built with PyQt6 for a simple desktop UI
- Plays audio using `python-vlc`
- Easily built into a standalone executable using PyInstaller

---

## 🚀 Quick Start

### How to use
On launch it should open a browser to authenticate access to your youtube playlists, if this doesnt work check that the `client_secrets.json` is in the directory. Alternatively you can just run it from the `main.py` as long as the requirements are installed in the venv.
- Very simple layout
    - pretty much everything is controlled with double clicks or context menus
- very baseline features such as shuffling right now, will possibly add more functionality in the future

### 1. Clone the Repository

```bash
git clone https://github.com/Oni-Hazza/YoutubeMusicAgain.git
cd YoutubeMusicAgain
```
### 2. Set Up the Environment
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 3. Make sure VLC is installed
This depends on OS but I'm sure you can figure that part out

### 4. Generate .spec file for pyinstaller
Run the script to generate the correct build file for your OS
```bash
chmod +x generate_spec.sh
./generate_spec.sh
```

### 5. Build Executable
```bash
pyinstaller --clean main.spec
```

### 6. Youtube API keys
You'll have to get your own API key, which can be done in the google developer website. Be sure to make one that uses the Youtube Data v3 api. Just make sure the file is `client_secrets.json`

### Installing to application menu (Linux only)
Run `generate_install_scripts.sh` and then run `install.sh`. This also generates an `uninstall.sh`

## 🐞 Troubleshooting
- Missing VLC: Ensure VLC is installed and the correct .so files are available. The script will prompt you for paths if they can’t be found.
    - Ensure paths are correct for your os in the `main.spec` file if you continue to have issues with finding vlc files
- Any issues with installing to application menu could be due to a distro you're using having different paths and such

## 📁 Project Structure
Should look something like this with some other bits and bobs
```css
YoutubeMusicAgain/
├── main.py
├── resources.py
├── widgets/
├── youtubefunc/
├── icons/
├── generate_spec.sh
├── main.spec  <-- Auto-generated
├── requirements.txt
└── README.md
```
# 🎵 YT Music App (PyQt6 + VLC)

A desktop application for playing music using YouTube and VLC, built with Python and PyQt6.

---

## 📦 Features

- Built with PyQt6 for a modern desktop UI
- Plays audio using `python-vlc`
- Bundled with VLC plugins and libraries for cross-distro Linux support
- Easily built into a standalone executable using PyInstaller

---

## 🚀 Quick Start

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

## 🐞 Troubleshooting
- Missing VLC: Ensure VLC is installed and the correct .so files are available. The script will prompt you for paths if they can’t be found.
    - Ensure paths are correct for your os in the `main.spec` file if you continue to have issues with finding vlc files

## 📁 Project Structure
Should look something like this
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
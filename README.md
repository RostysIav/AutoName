# AutoName

AutoName is a lightweight desktop tool for **renaming files in bulk** with simple, repeatable rules.  
Built in **Python** with a **Tkinter** GUI.

> Goal: make common rename workflows fast, predictable, and non-destructive (preview first).

---

## Features

- Bulk rename files in a selected folder (or a chosen set of files)
- Common rename operations (depending on your build):
  - Add prefix / suffix
  - Find & replace text
  - Remove characters (by rule)
  - Trim / normalize spacing (optional)
  - Sequential numbering (optional)
- **Preview** changes before applying
- Works offline

> Adjust this list to match what your current version supports.

---

## Screenshots

Add screenshots to a folder like `docs/` and link them here:

```md
![AutoName UI](docs/screenshot.png)
```

---

## Requirements

- Python 3.10+ recommended (3.8+ likely fine)
- OS: Windows / macOS / Linux (Tkinter is included with most Python installs)

---

## Installation (Run from source)

```bash
git clone https://github.com/<your-username>/AutoName.git
cd AutoName

python -m venv .venv

# Windows:
.venv\Scripts\activate

# macOS/Linux:
source .venv/bin/activate

# If you have dependencies:
pip install -r requirements.txt

python main.py
```

If your project is pure Tkinter (no external deps), you can remove the `pip install` line.

---

## Usage

1. Launch the app:
   ```bash
   python main.py
   ```
2. Select files or a folder
3. Choose your renaming rule(s)
4. **Preview**
5. Apply changes

### Tips
- Start with a small test folder.
- Keep backups if you’re renaming important files (bulk rename is powerful… and unforgiving).

---

## Project Structure (edit to match your repo)

```text
AutoName/
  main.py
  src/
  docs/
  requirements.txt
  README.md
  LICENSE
```

---

## Build an .exe (Windows)

If you package with **PyInstaller**:

```bash
pip install pyinstaller
pyinstaller --onefile --windowed main.py --name AutoName
```

Output will be in `dist/`.

> If your app needs extra files (icons, configs), you’ll likely need `--add-data` and/or a `.spec` file.

---

## Troubleshooting

**Tkinter not found**
- On some Linux distros, install it:
  - Debian/Ubuntu: `sudo apt-get install python3-tk`

**Nothing happens when I run it**
- Run from terminal to see errors:
  ```bash
  python main.py
  ```

**Renames didn’t match what I expected**
- Use Preview first.
- Check whether rules apply in order (some apps apply multiple transformations sequentially).

---

## Roadmap (optional)

- [ ] Drag & drop files
- [ ] Saved rename presets
- [ ] Undo / rollback rename session
- [ ] Rename rules pipeline with reorder
- [ ] Cross-platform builds (macOS `.app` / Linux AppImage)

---

## Contributing

PRs are welcome. If you’re adding a feature:
- Keep UI minimal and consistent
- Update this README if behavior changes

---

## License

Pick a license and add a `LICENSE` file (MIT is a common default).

---

## Author

Created by **Rostyslav** (aka **Ross Havryshkiv**).

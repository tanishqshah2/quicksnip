# ⚡ QuickSnip — System-wide Text Expander

Type a short trigger like `;;zem` in **any app, any text field** and it instantly expands into your full snippet — emails, addresses, code blocks, anything.

Works on **macOS**, **Windows**, and **Linux**.

![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![Platform](https://img.shields.io/badge/platform-macOS%20%7C%20Windows%20%7C%20Linux-lightgrey)

---

## What it looks like

- Dark-themed management window with sidebar
- Searchable snippet list
- Add / Edit / Delete snippets via GUI or by editing `snippets.json` directly
- Pause and resume expansion without closing the app

---

## Quick demo

Define this snippet in the GUI:

| Trigger | Expansion |
|---------|-----------|
| `;;zem` | `Hello,\n\nThank you for reaching out. I'll get back to you shortly.\n\nBest regards,\nYour Name` |

Now open any app (browser, email client, Slack, VS Code, Notes…), type `;;zem` and watch it expand instantly.

---

## Setup

### Prerequisites

- **Python 3.8 or newer** — check with `python3 --version`
- `pip` package manager

---

### macOS

```bash
# 1. Clone the repo
git clone https://github.com/tanishqshah2/quicksnip.git
cd quicksnip

# 2. Install dependencies
pip3 install -r requirements.txt

# 3. Grant Accessibility permission (one-time, required)
#    System Settings → Privacy & Security → Accessibility
#    Click + and add your Terminal app (Terminal.app or iTerm2)
#    Make sure the toggle is ON

# 4. Run
python3 main.py
```

> **Why Accessibility?**
> macOS restricts apps from reading global keystrokes unless you explicitly trust them.
> QuickSnip will show a warning dialog if the permission is missing.
> You only need to do this once — the permission persists across reboots.

**Which app to add?**

| Terminal you use | Add this to Accessibility |
|-----------------|--------------------------|
| Terminal.app    | `/Applications/Utilities/Terminal.app` |
| iTerm2          | `/Applications/iTerm.app` |
| VS Code terminal | `/Applications/Visual Studio Code.app` |
| Warp            | `/Applications/Warp.app` |

After adding, **quit and relaunch** your terminal, then run `python3 main.py`.

---

### Windows

```bat
REM 1. Clone the repo
git clone https://github.com/tanishqshah2/quicksnip.git
cd quicksnip

REM 2. Install dependencies
pip install -r requirements.txt

REM 3. Run
python main.py
```

No extra permissions needed on Windows. If Windows Defender prompts you, allow it.

> **Tip:** To start QuickSnip on login, create a shortcut to `pythonw main.py` in
> `shell:startup` (press Win+R, type `shell:startup`, paste the shortcut there).
> Using `pythonw` instead of `python` suppresses the console window.

---

### Linux

```bash
# 1. Clone the repo
git clone https://github.com/tanishqshah2/quicksnip.git
cd quicksnip

# 2. Install system dependency for clipboard support
sudo apt install xclip        # Debian / Ubuntu
# or
sudo dnf install xclip        # Fedora
# or
sudo pacman -S xclip          # Arch

# 3. Install Python dependencies
pip3 install -r requirements.txt

# 4. Run
python3 main.py
```

> **Note:** On Linux, `pynput` uses X11's `XRecord` extension.
> If you are on Wayland, set `QT_QPA_PLATFORM=xcb` or run the session in
> XWayland mode. Most distros fall back to X11 by default.

---

## Using QuickSnip

### Adding a snippet

1. Click **+ Add Snippet** in the sidebar
2. Enter a **Trigger** — any string, but using a prefix like `;;` reduces accidental matches
3. Enter the **Expansion** — plain text, multi-line, any Unicode, no length limit
4. Click **Save Snippet**

### Editing / Deleting

- **Double-click** a row to edit it
- Select a row and press **Delete** (keyboard) or click the red **Delete** button
- The **Edit** button opens the same dialog

### Searching

Type in the search box (top-right) to filter snippets by trigger or content.

### Pause / Resume

Click **Pause Expander** in the sidebar to temporarily disable expansion without closing the app. Click **Resume** to re-enable.

---

## Snippet storage

Snippets live in `snippets.json` in the project folder. You can edit it directly:

```json
{
  ";;zem": "Hello,\n\nThank you for reaching out.\n\nBest regards,\nYour Name",
  ";;addr": "123 Main Street\nCity, State 00000",
  ";;sig": "Best regards,\nYour Name\nyourname@example.com",
  ";;ema": "yourname@example.com"
}
```

Changes saved in the GUI update `snippets.json` immediately and take effect on the next keystroke check.

---

## Package as a standalone app (no Python needed)

```bash
pip install pyinstaller

# macOS / Linux
pyinstaller --onefile --windowed main.py --name QuickSnip

# Windows
pyinstaller --onefile --windowed main.py --name QuickSnip.exe
```

Output binary will be in the `dist/` folder.

> On macOS, grant Accessibility permission to `dist/QuickSnip` rather than Terminal.

---

## How it works

1. `pynput` installs a system-wide keyboard listener
2. A rolling 64-character buffer tracks what you recently typed
3. After each keypress, the buffer is checked against all known triggers
4. On a match, a background worker:
   - Sends backspace × `len(trigger)` to erase the trigger
   - Copies the expansion to clipboard
   - Sends ⌘V (macOS) or Ctrl+V (Windows/Linux) to paste
   - Restores your previous clipboard content
5. The expansion worker runs on a separate thread to avoid keyboard listener deadlocks

---

## Troubleshooting

| Problem | Fix |
|---------|-----|
| Snippets not expanding on macOS | Add your terminal to **System Settings → Accessibility** |
| `ModuleNotFoundError: pynput` | Run `pip3 install -r requirements.txt` |
| Clipboard not restored after paste | Install `xclip` (Linux) or update `pyperclip` |
| GUI doesn't open | Make sure `tkinter` is installed: `python3 -m tkinter` |
| Linux: no events captured | Ensure you're running under X11, not Wayland |

---

## License

MIT — use freely, fork freely.

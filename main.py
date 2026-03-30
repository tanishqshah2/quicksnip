#!/usr/bin/env python3
"""
QuickSnip — system-wide text expander.
Run this file to start the app.
"""

import sys
import platform
from expander import TextExpander
from gui import App


def check_macos_accessibility():
    """Warn the user if Accessibility permission is missing on macOS."""
    import subprocess
    result = subprocess.run(
        ["osascript", "-e",
         'tell application "System Events" to keystroke ""'],
        capture_output=True
    )
    if result.returncode != 0:
        import tkinter as tk
        from tkinter import messagebox
        root = tk.Tk()
        root.withdraw()
        messagebox.showwarning(
            "Accessibility Permission Required",
            "QuickSnip needs Accessibility access to monitor keystrokes.\n\n"
            "Go to:\n"
            "  System Settings → Privacy & Security → Accessibility\n\n"
            "Add and enable your terminal app (or the QuickSnip.app).\n"
            "Then restart QuickSnip.",
        )
        root.destroy()
        sys.exit(1)


def main():
    if platform.system() == "Darwin":
        check_macos_accessibility()

    expander = TextExpander(snippets_file="snippets.json")
    expander.start()

    app = App(expander)
    app.run()


if __name__ == "__main__":
    main()

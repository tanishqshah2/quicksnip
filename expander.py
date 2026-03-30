"""
Core text expansion engine.
Monitors all keystrokes system-wide and replaces triggers with snippets.
"""

import json
import time
import queue
import threading
import platform
from pynput import keyboard
import pyperclip


SYSTEM = platform.system()  # 'Darwin' | 'Windows' | 'Linux'


class TextExpander:
    def __init__(self, snippets_file="snippets.json"):
        self.snippets_file = snippets_file
        self.snippets = self.load_snippets()

        self.buffer = ""
        self.max_buffer = 64  # longest trigger we'll ever track

        self.controller = keyboard.Controller()
        self.listener = None

        # Expansion happens on a worker thread to avoid pynput deadlocks
        self._expanding = False
        self._queue = queue.Queue()
        self._worker = threading.Thread(target=self._process_queue, daemon=True)
        self._worker.start()

        self._running = False
        self._lock = threading.Lock()

    # ------------------------------------------------------------------ #
    # Snippet CRUD                                                         #
    # ------------------------------------------------------------------ #

    def load_snippets(self):
        try:
            with open(self.snippets_file, encoding="utf-8") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}

    def save_snippets(self):
        with open(self.snippets_file, "w", encoding="utf-8") as f:
            json.dump(self.snippets, f, indent=2, ensure_ascii=False)

    def add_snippet(self, trigger: str, expansion: str):
        self.snippets[trigger] = expansion
        self.save_snippets()

    def remove_snippet(self, trigger: str):
        self.snippets.pop(trigger, None)
        self.save_snippets()

    def get_all(self) -> dict:
        return dict(self.snippets)

    # ------------------------------------------------------------------ #
    # Keyboard listener callbacks                                          #
    # ------------------------------------------------------------------ #

    def _on_press(self, key):
        # While we are expanding, ignore all keys so we don't pollute the buffer
        if self._expanding:
            return

        with self._lock:
            try:
                char = key.char
                if char:
                    self.buffer += char
                    # Trim buffer to max length
                    if len(self.buffer) > self.max_buffer:
                        self.buffer = self.buffer[-self.max_buffer:]
                    self._check_buffer()
            except AttributeError:
                # Special / modifier key
                if key == keyboard.Key.backspace:
                    self.buffer = self.buffer[:-1]
                else:
                    # Any other special key resets the buffer
                    self.buffer = ""

    def _check_buffer(self):
        """Look for a trigger at the end of the current buffer."""
        for trigger, expansion in self.snippets.items():
            if self.buffer.endswith(trigger):
                self.buffer = ""
                self._queue.put((trigger, expansion))
                break

    # ------------------------------------------------------------------ #
    # Expansion worker                                                     #
    # ------------------------------------------------------------------ #

    def _process_queue(self):
        while True:
            trigger, expansion = self._queue.get()
            self._do_expand(trigger, expansion)

    def _do_expand(self, trigger: str, expansion: str):
        self._expanding = True
        try:
            # Small pause so the last typed char is committed to the focused app
            time.sleep(0.05)

            # Delete the trigger characters
            for _ in range(len(trigger)):
                self.controller.tap(keyboard.Key.backspace)
            time.sleep(0.05)

            # Paste via clipboard (handles unicode, newlines, etc.)
            old_clip = ""
            try:
                old_clip = pyperclip.paste()
            except Exception:
                pass

            pyperclip.copy(expansion)
            time.sleep(0.02)

            with self.controller.pressed(
                keyboard.Key.cmd if SYSTEM == "Darwin" else keyboard.Key.ctrl
            ):
                self.controller.tap("v")

            time.sleep(0.05)

            # Restore previous clipboard content
            try:
                pyperclip.copy(old_clip)
            except Exception:
                pass

        finally:
            self._expanding = False

    # ------------------------------------------------------------------ #
    # Start / stop                                                         #
    # ------------------------------------------------------------------ #

    def start(self):
        if self._running:
            return
        self._running = True
        self.listener = keyboard.Listener(on_press=self._on_press)
        self.listener.start()

    def stop(self):
        if not self._running:
            return
        self._running = False
        if self.listener:
            self.listener.stop()

    @property
    def is_running(self):
        return self._running

"""
Tkinter GUI for managing snippets — QuickSnip.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import platform

# ── Palette ────────────────────────────────────────────────────────────────────
BG          = "#0f0f1a"   # window background (very dark navy)
SURFACE     = "#1a1a2e"   # card / panel surface
SURFACE2    = "#16213e"   # slightly lifted surface
ENTRY_BG    = "#1e1e35"   # input field background
BORDER      = "#2a2a4a"   # subtle border

TEXT        = "#e8e8ff"   # primary text  (near-white with a blue tint)
TEXT_DIM    = "#8888bb"   # secondary / label text
TEXT_MUTED  = "#55558a"   # placeholder / muted text

PURPLE      = "#7c5cbf"   # primary accent
PURPLE_LT   = "#9b7fe8"   # lighter purple for hover
PURPLE_DK   = "#5a3d9a"   # darker purple for press

BLUE        = "#2563eb"   # edit button
BLUE_LT     = "#3b82f6"
RED         = "#dc2626"   # delete button
RED_LT      = "#ef4444"

GREEN       = "#22c55e"   # running indicator
AMBER       = "#f59e0b"   # paused indicator

ROW_ODD     = "#1a1a2e"
ROW_EVEN    = "#141425"
ROW_SEL     = "#3d2d72"   # selected row


def _is_mac():
    return platform.system() == "Darwin"


def _font(size, bold=False):
    family = "SF Pro Display" if _is_mac() else "Segoe UI"
    weight = "bold" if bold else "normal"
    return (family, size, weight)


def _btn(parent, text, command, bg, fg="#ffffff", width=None, pad_x=20, pad_y=8):
    """Helper to create a flat button with consistent hover style."""
    b = tk.Button(
        parent, text=text, command=command,
        bg=bg, fg=fg, activebackground=_darken(bg), activeforeground=fg,
        relief="flat", bd=0, cursor="hand2",
        font=_font(11, bold=True),
        padx=pad_x, pady=pad_y,
    )
    if width:
        b.config(width=width)
    # Subtle hover effect
    def on_enter(_): b.config(bg=_lighten(bg))
    def on_leave(_): b.config(bg=bg)
    b.bind("<Enter>", on_enter)
    b.bind("<Leave>", on_leave)
    return b


def _darken(hex_color, factor=0.15):
    r, g, b = int(hex_color[1:3], 16), int(hex_color[3:5], 16), int(hex_color[5:7], 16)
    r = max(0, int(r * (1 - factor)))
    g = max(0, int(g * (1 - factor)))
    b = max(0, int(b * (1 - factor)))
    return f"#{r:02x}{g:02x}{b:02x}"


def _lighten(hex_color, factor=0.15):
    r, g, b = int(hex_color[1:3], 16), int(hex_color[3:5], 16), int(hex_color[5:7], 16)
    r = min(255, int(r + (255 - r) * factor))
    g = min(255, int(g + (255 - g) * factor))
    b = min(255, int(b + (255 - b) * factor))
    return f"#{r:02x}{g:02x}{b:02x}"


def _apply_treeview_style():
    style = ttk.Style()
    style.theme_use("clam")

    style.configure(
        "Snippets.Treeview",
        background=ROW_ODD,
        foreground=TEXT,
        fieldbackground=ROW_ODD,
        rowheight=36,
        borderwidth=0,
        font=_font(12),
    )
    style.configure(
        "Snippets.Treeview.Heading",
        background=SURFACE2,
        foreground=TEXT_DIM,
        font=_font(11, bold=True),
        relief="flat",
        borderwidth=0,
    )
    style.map(
        "Snippets.Treeview",
        background=[("selected", ROW_SEL)],
        foreground=[("selected", "#ffffff")],
    )
    style.layout("Snippets.Treeview", [("Treeview.treearea", {"sticky": "nswe"})])

    style.configure(
        "Dark.Vertical.TScrollbar",
        background=SURFACE,
        troughcolor=BG,
        arrowcolor=TEXT_DIM,
        borderwidth=0,
        width=10,
    )
    style.map("Dark.Vertical.TScrollbar", background=[("active", BORDER)])


# ── Dialog ─────────────────────────────────────────────────────────────────────

class SnippetDialog(tk.Toplevel):
    def __init__(self, parent, title="Add Snippet", trigger="", expansion=""):
        super().__init__(parent)
        self.title(title)
        self.configure(bg=BG)
        self.resizable(True, True)
        self.minsize(520, 380)
        self.grab_set()

        self.result_trigger = None
        self.result_expansion = None

        self._build(trigger, expansion)
        self.bind("<Escape>", lambda _: self.destroy())

        # Center over parent
        self.update_idletasks()
        pw, ph = parent.winfo_width(), parent.winfo_height()
        px, py = parent.winfo_rootx(), parent.winfo_rooty()
        w, h = self.winfo_width(), self.winfo_height()
        self.geometry(f"+{px + (pw - w)//2}+{py + (ph - h)//2}")

    def _build(self, trigger, expansion):
        # Header
        hdr = tk.Frame(self, bg=SURFACE2, padx=20, pady=14)
        hdr.pack(fill="x")
        tk.Label(hdr, text=self.title(), bg=SURFACE2, fg=TEXT,
                 font=_font(15, bold=True)).pack(side="left")

        body = tk.Frame(self, bg=BG)
        body.pack(fill="both", expand=True, padx=20, pady=16)
        body.columnconfigure(0, weight=1)

        # Trigger label + field
        tk.Label(body, text="TRIGGER", bg=BG, fg=TEXT_DIM,
                 font=_font(9, bold=True)).grid(row=0, column=0, sticky="w", pady=(0, 4))

        trigger_wrap = tk.Frame(body, bg=ENTRY_BG, highlightbackground=BORDER,
                                 highlightthickness=1)
        trigger_wrap.grid(row=1, column=0, sticky="ew", pady=(0, 14))

        self._trigger_var = tk.StringVar(value=trigger)
        te = tk.Entry(trigger_wrap, textvariable=self._trigger_var,
                      bg=ENTRY_BG, fg=TEXT, insertbackground=TEXT_DIM,
                      relief="flat", font=_font(13), bd=10)
        te.pack(fill="x")
        te.focus_set()

        # Expansion label + text area
        tk.Label(body, text="EXPANSION", bg=BG, fg=TEXT_DIM,
                 font=_font(9, bold=True)).grid(row=2, column=0, sticky="w", pady=(0, 4))

        exp_wrap = tk.Frame(body, bg=ENTRY_BG, highlightbackground=BORDER,
                             highlightthickness=1)
        exp_wrap.grid(row=3, column=0, sticky="nsew", pady=(0, 4))
        body.rowconfigure(3, weight=1)

        self._exp_text = tk.Text(
            exp_wrap, bg=ENTRY_BG, fg=TEXT, insertbackground=TEXT_DIM,
            relief="flat", font=_font(12), wrap="word",
            padx=10, pady=8, height=8,
            selectbackground=ROW_SEL, selectforeground="#ffffff",
        )
        self._exp_text.insert("1.0", expansion)
        self._exp_text.pack(fill="both", expand=True)

        tk.Label(body, text="Tip: use ;;prefix to avoid accidental matches",
                 bg=BG, fg=TEXT_MUTED, font=_font(9)).grid(
            row=4, column=0, sticky="w", pady=(2, 0))

        # Footer buttons
        footer = tk.Frame(self, bg=SURFACE2, padx=20, pady=12)
        footer.pack(fill="x", side="bottom")

        _btn(footer, "Cancel", self.destroy, bg=SURFACE, fg=TEXT_DIM,
             pad_x=16, pad_y=7).pack(side="right", padx=(8, 0))
        _btn(footer, "Save Snippet", self._save, bg=PURPLE,
             pad_x=20, pad_y=7).pack(side="right")

    def _save(self):
        trigger = self._trigger_var.get().strip()
        expansion = self._exp_text.get("1.0", "end-1c")
        if not trigger:
            messagebox.showwarning("Missing trigger",
                                   "Please enter a trigger (e.g. ;;zem).",
                                   parent=self)
            return
        if not expansion:
            messagebox.showwarning("Missing expansion",
                                   "Please enter the expansion text.",
                                   parent=self)
            return
        self.result_trigger = trigger
        self.result_expansion = expansion
        self.destroy()


# ── Main window ────────────────────────────────────────────────────────────────

class App:
    def __init__(self, expander):
        self.expander = expander

        self.root = tk.Tk()
        self.root.title("QuickSnip")
        self.root.configure(bg=BG)
        self.root.minsize(720, 500)
        self.root.geometry("820x560")
        _apply_treeview_style()

        self._build_ui()
        self._refresh_list()
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)

    # ── UI construction ────────────────────────────────────────────────────

    def _build_ui(self):
        # ── Sidebar ──────────────────────────────────────────────────────
        sidebar = tk.Frame(self.root, bg=SURFACE2, width=220)
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)

        # Logo area
        logo_frame = tk.Frame(sidebar, bg=SURFACE2, pady=24, padx=20)
        logo_frame.pack(fill="x")

        tk.Label(logo_frame, text="⚡", bg=SURFACE2, fg=PURPLE_LT,
                 font=(_font(22)[0], 22)).pack(side="left")
        tk.Label(logo_frame, text=" QuickSnip", bg=SURFACE2, fg=TEXT,
                 font=_font(16, bold=True)).pack(side="left")

        # Status pill
        self._status_frame = tk.Frame(sidebar, bg=SURFACE, padx=12, pady=8,
                                       highlightbackground=BORDER,
                                       highlightthickness=1)
        self._status_frame.pack(fill="x", padx=16, pady=(0, 20))

        status_row = tk.Frame(self._status_frame, bg=SURFACE)
        status_row.pack(fill="x")

        self._dot = tk.Label(status_row, text="●", bg=SURFACE, fg=GREEN,
                              font=_font(11))
        self._dot.pack(side="left")
        self._status_lbl = tk.Label(status_row, text=" Active", bg=SURFACE,
                                     fg=GREEN, font=_font(11, bold=True))
        self._status_lbl.pack(side="left")

        tk.Label(self._status_frame,
                 text="Expanding in all apps", bg=SURFACE,
                 fg=TEXT_MUTED, font=_font(9)).pack(anchor="w", pady=(2, 0))

        # Toggle button
        self._toggle_btn = _btn(sidebar, "⏸  Pause Expander",
                                 self._toggle_expander,
                                 bg=SURFACE, fg=TEXT_DIM,
                                 pad_x=14, pad_y=8)
        self._toggle_btn.pack(fill="x", padx=16, pady=(0, 6))

        tk.Frame(sidebar, bg=BORDER, height=1).pack(fill="x", padx=16, pady=16)

        # Action buttons in sidebar
        _btn(sidebar, "+ Add Snippet", self._add_snippet,
             bg=PURPLE, fg="#ffffff", pad_x=14, pad_y=10).pack(
            fill="x", padx=16, pady=(0, 8))

        self._edit_btn = _btn(sidebar, "✏  Edit", self._edit_snippet,
                               bg=BLUE, fg="#ffffff", pad_x=14, pad_y=9)
        self._edit_btn.pack(fill="x", padx=16, pady=(0, 8))

        self._del_btn = _btn(sidebar, "🗑  Delete", self._delete_snippet,
                              bg=RED, fg="#ffffff", pad_x=14, pad_y=9)
        self._del_btn.pack(fill="x", padx=16)

        # Count at bottom of sidebar
        tk.Frame(sidebar, bg=BORDER, height=1).pack(fill="x", padx=16, pady=16)
        self._count_lbl = tk.Label(sidebar, text="", bg=SURFACE2,
                                    fg=TEXT_MUTED, font=_font(10))
        self._count_lbl.pack(padx=16, anchor="w")

        # ── Main content area ─────────────────────────────────────────────
        main = tk.Frame(self.root, bg=BG)
        main.pack(side="right", fill="both", expand=True)

        # Top bar with search
        topbar = tk.Frame(main, bg=SURFACE, pady=12, padx=16)
        topbar.pack(fill="x")

        tk.Label(topbar, text="My Snippets", bg=SURFACE, fg=TEXT,
                 font=_font(14, bold=True)).pack(side="left")

        # Search box (right side)
        search_outer = tk.Frame(topbar, bg=ENTRY_BG,
                                 highlightbackground=BORDER,
                                 highlightthickness=1)
        search_outer.pack(side="right")

        tk.Label(search_outer, text="🔍", bg=ENTRY_BG, fg=TEXT_MUTED,
                 font=_font(11)).pack(side="left", padx=(8, 0))

        self._search_var = tk.StringVar()
        self._search_var.trace_add("write", lambda *_: self._refresh_list())
        tk.Entry(search_outer, textvariable=self._search_var,
                 bg=ENTRY_BG, fg=TEXT, insertbackground=TEXT_DIM,
                 relief="flat", font=_font(11), bd=6, width=22).pack(side="left")

        # Column headers row (custom — above treeview)
        headers = tk.Frame(main, bg=SURFACE2, pady=0)
        headers.pack(fill="x")
        tk.Label(headers, text="  TRIGGER", bg=SURFACE2, fg=TEXT_DIM,
                 font=_font(9, bold=True), width=18, anchor="w",
                 pady=8).pack(side="left")
        tk.Frame(headers, bg=BORDER, width=1).pack(side="left", fill="y")
        tk.Label(headers, text="  EXPANSION PREVIEW", bg=SURFACE2, fg=TEXT_DIM,
                 font=_font(9, bold=True), anchor="w",
                 pady=8).pack(side="left", fill="x", expand=True)

        # Treeview
        tree_frame = tk.Frame(main, bg=BG)
        tree_frame.pack(fill="both", expand=True, padx=0, pady=0)

        self._tree = ttk.Treeview(tree_frame, columns=("trigger", "expansion"),
                                   show="tree headings",
                                   style="Snippets.Treeview",
                                   selectmode="browse")
        self._tree.heading("#0", text="", anchor="w")
        self._tree.heading("trigger", text="", anchor="w")
        self._tree.heading("expansion", text="", anchor="w")
        self._tree.column("#0", width=0, minwidth=0, stretch=False)
        self._tree.column("trigger", width=160, minwidth=100, stretch=False)
        self._tree.column("expansion", minwidth=300, stretch=True)

        sb = ttk.Scrollbar(tree_frame, orient="vertical",
                            command=self._tree.yview,
                            style="Dark.Vertical.TScrollbar")
        self._tree.configure(yscrollcommand=sb.set)
        self._tree.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")

        self._tree.bind("<Double-1>", lambda _: self._edit_snippet())
        self._tree.bind("<<TreeviewSelect>>", lambda _: self._on_select())

        # Empty state label
        self._empty_lbl = tk.Label(main, text="No snippets yet.\nClick '+ Add Snippet' to get started.",
                                    bg=BG, fg=TEXT_MUTED, font=_font(12),
                                    justify="center")

        # Keyboard shortcuts
        self.root.bind("<Delete>", lambda _: self._delete_snippet())
        self.root.bind("<Return>", lambda _: self._edit_snippet())

    # ── List ────────────────────────────────────────────────────────────

    def _refresh_list(self):
        query = self._search_var.get().lower() if hasattr(self, "_search_var") else ""
        for row in self._tree.get_children():
            self._tree.delete(row)

        snippets = self.expander.get_all()
        rows = []
        for trigger, expansion in sorted(snippets.items()):
            if query and query not in trigger.lower() and query not in expansion.lower():
                continue
            rows.append((trigger, expansion))

        for i, (trigger, expansion) in enumerate(rows):
            preview = expansion.replace("\n", "  ↵  ")
            if len(preview) > 90:
                preview = preview[:90] + "…"
            tag = "even" if i % 2 == 0 else "odd"
            self._tree.insert("", "end", values=(trigger, preview), tags=(tag,))

        self._tree.tag_configure("odd",  background=ROW_ODD)
        self._tree.tag_configure("even", background=ROW_EVEN)

        total = len(snippets)
        shown = len(rows)
        if query:
            self._count_lbl.config(text=f"{shown} of {total} snippets")
        else:
            self._count_lbl.config(text=f"{total} snippet{'s' if total != 1 else ''}")

        if shown == 0 and not query:
            self._empty_lbl.place(relx=0.55, rely=0.5, anchor="center")
        else:
            self._empty_lbl.place_forget()

    def _on_select(self):
        pass  # reserved for future preview pane

    # ── CRUD ────────────────────────────────────────────────────────────

    def _add_snippet(self):
        dlg = SnippetDialog(self.root, title="Add Snippet")
        self.root.wait_window(dlg)
        if dlg.result_trigger:
            if dlg.result_trigger in self.expander.snippets:
                if not messagebox.askyesno(
                    "Overwrite?",
                    f"'{dlg.result_trigger}' already exists. Overwrite?",
                    parent=self.root,
                ):
                    return
            self.expander.add_snippet(dlg.result_trigger, dlg.result_expansion)
            self._refresh_list()

    def _edit_snippet(self):
        sel = self._tree.selection()
        if not sel:
            return
        trigger = self._tree.item(sel[0], "values")[0]
        expansion = self.expander.snippets.get(trigger, "")
        dlg = SnippetDialog(self.root, title="Edit Snippet",
                             trigger=trigger, expansion=expansion)
        self.root.wait_window(dlg)
        if dlg.result_trigger:
            if dlg.result_trigger != trigger:
                self.expander.remove_snippet(trigger)
            self.expander.add_snippet(dlg.result_trigger, dlg.result_expansion)
            self._refresh_list()

    def _delete_snippet(self):
        sel = self._tree.selection()
        if not sel:
            return
        trigger = self._tree.item(sel[0], "values")[0]
        if messagebox.askyesno("Delete snippet",
                                f"Delete '{trigger}'?",
                                parent=self.root):
            self.expander.remove_snippet(trigger)
            self._refresh_list()

    # ── Toggle ──────────────────────────────────────────────────────────

    def _toggle_expander(self):
        if self.expander.is_running:
            self.expander.stop()
            self._dot.config(fg=AMBER)
            self._status_lbl.config(text=" Paused", fg=AMBER)
            self._status_frame.config(highlightbackground=AMBER)
            self._toggle_btn.config(text="▶  Resume Expander", bg=PURPLE, fg="#ffffff")
        else:
            self.expander.start()
            self._dot.config(fg=GREEN)
            self._status_lbl.config(text=" Active", fg=GREEN)
            self._status_frame.config(highlightbackground=BORDER)
            self._toggle_btn.config(text="⏸  Pause Expander", bg=SURFACE, fg=TEXT_DIM)

    def _on_close(self):
        self.expander.stop()
        self.root.destroy()

    def run(self):
        self.root.mainloop()

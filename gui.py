"""
Tkinter GUI for managing snippets — QuickSnip.
Uses Frame+Label buttons so colors render correctly on macOS.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import platform

# ── Palette ────────────────────────────────────────────────────────────────────
BG        = "#0a0a18"   # window background
SURFACE   = "#12122a"   # panel / card
SURFACE2  = "#1c1c3a"   # sidebar
ENTRY_BG  = "#1a1a35"   # input fields
BORDER    = "#2e2e5e"   # borders / dividers

TEXT      = "#f0f0ff"   # primary text
TEXT_DIM  = "#8888cc"   # labels / secondary
TEXT_MUTED= "#44447a"   # placeholders

# Vivid button colors
C_ADD     = "#7c3aed"   # violet — Add
C_ADD_H   = "#6d28d9"
C_EDIT    = "#0d9488"   # teal — Edit
C_EDIT_H  = "#0f766e"
C_DEL     = "#e11d48"   # rose — Delete
C_DEL_H   = "#be123c"
C_PAUSE   = "#374151"   # neutral — Pause
C_PAUSE_H = "#1f2937"
C_RESUME  = "#065f46"   # emerald — Resume
C_RESUME_H= "#064e3b"

# Status
GREEN     = "#10b981"
AMBER     = "#f59e0b"

# List rows
ROW_ODD   = "#12122a"
ROW_EVEN  = "#0f0f20"
ROW_SEL   = "#4c1d95"


def _is_mac():
    return platform.system() == "Darwin"


def _font(size, bold=False):
    family = "SF Pro Display" if _is_mac() else "Segoe UI"
    return (family, size, "bold" if bold else "normal")


def _hex_lerp(color, target="#ffffff", t=0.18):
    """Blend color toward target by factor t."""
    r1,g1,b1 = int(color[1:3],16), int(color[3:5],16), int(color[5:7],16)
    r2,g2,b2 = int(target[1:3],16), int(target[3:5],16), int(target[5:7],16)
    r = int(r1 + (r2-r1)*t)
    g = int(g1 + (g2-g1)*t)
    b = int(b1 + (b2-b1)*t)
    return f"#{r:02x}{g:02x}{b:02x}"


# ── Custom button (Frame+Label so bg colour works on macOS) ────────────────────

class CButton(tk.Frame):
    """Coloured button that actually renders on macOS."""

    def __init__(self, parent, text, command, bg,
                 fg="#ffffff", font=None, padx=0, pady=0, **kw):
        super().__init__(parent, bg=bg, cursor="hand2", **kw)
        self._bg      = bg
        self._fg      = fg
        self._command = command
        self._hover   = _hex_lerp(bg, "#ffffff", 0.18)
        self._press   = _hex_lerp(bg, "#000000", 0.15)

        self._lbl = tk.Label(
            self, text=text, bg=bg, fg=fg,
            font=font or _font(11, bold=True),
            padx=padx, pady=pady,
        )
        self._lbl.pack(fill="both", expand=True)

        for w in (self, self._lbl):
            w.bind("<Button-1>",        self._on_click)
            w.bind("<ButtonRelease-1>", self._on_release)
            w.bind("<Enter>",           self._on_enter)
            w.bind("<Leave>",           self._on_leave)

    def _set_color(self, c):
        self.config(bg=c)
        self._lbl.config(bg=c)

    def _on_enter(self,  _): self._set_color(self._hover)
    def _on_leave(self,  _): self._set_color(self._bg)
    def _on_click(self,  _): self._set_color(self._press)
    def _on_release(self,_):
        self._set_color(self._hover)
        self._command()

    def update_colors(self, bg, fg=None):
        self._bg    = bg
        self._hover = _hex_lerp(bg, "#ffffff", 0.18)
        self._press = _hex_lerp(bg, "#000000", 0.15)
        self._set_color(bg)
        if fg:
            self._fg = fg
            self._lbl.config(fg=fg)

    def set_text(self, text):
        self._lbl.config(text=text)


# ── Treeview / scrollbar styles ────────────────────────────────────────────────

def _apply_styles():
    s = ttk.Style()
    s.theme_use("clam")

    s.configure("Snip.Treeview",
        background=ROW_ODD, foreground=TEXT,
        fieldbackground=ROW_ODD, rowheight=36, borderwidth=0,
        font=_font(12))
    s.configure("Snip.Treeview.Heading",
        background=SURFACE2, foreground=TEXT_DIM,
        font=_font(10, bold=True), relief="flat", borderwidth=0)
    s.map("Snip.Treeview",
        background=[("selected", ROW_SEL)],
        foreground=[("selected", "#ffffff")])
    s.layout("Snip.Treeview", [("Treeview.treearea", {"sticky": "nswe"})])

    s.configure("Q.Vertical.TScrollbar",
        background=SURFACE, troughcolor=BG,
        arrowcolor=TEXT_MUTED, borderwidth=0, width=8)
    s.map("Q.Vertical.TScrollbar", background=[("active", BORDER)])


# ── Add / Edit dialog ──────────────────────────────────────────────────────────

class SnippetDialog(tk.Toplevel):
    def __init__(self, parent, title="Add Snippet", trigger="", expansion=""):
        super().__init__(parent)
        self.title(title)
        self.configure(bg=BG)
        self.resizable(True, True)
        self.minsize(540, 400)
        self.grab_set()

        self.result_trigger   = None
        self.result_expansion = None

        self._build(trigger, expansion)
        self.bind("<Escape>", lambda _: self.destroy())

        self.update_idletasks()
        pw, ph = parent.winfo_width(), parent.winfo_height()
        px, py = parent.winfo_rootx(), parent.winfo_rooty()
        w,  h  = self.winfo_width(),  self.winfo_height()
        self.geometry(f"+{px+(pw-w)//2}+{py+(ph-h)//2}")

    def _build(self, trigger, expansion):
        # Header bar
        hdr = tk.Frame(self, bg=SURFACE2, padx=20, pady=14)
        hdr.pack(fill="x")
        tk.Label(hdr, text=self.title(), bg=SURFACE2, fg=TEXT,
                 font=_font(15, bold=True)).pack(side="left")

        body = tk.Frame(self, bg=BG, padx=20, pady=16)
        body.pack(fill="both", expand=True)
        body.columnconfigure(0, weight=1)
        body.rowconfigure(3, weight=1)

        # Trigger
        tk.Label(body, text="TRIGGER", bg=BG, fg=TEXT_DIM,
                 font=_font(9, bold=True)).grid(row=0, column=0, sticky="w", pady=(0,4))
        wrap1 = tk.Frame(body, bg=ENTRY_BG, highlightbackground=BORDER,
                          highlightthickness=1)
        wrap1.grid(row=1, column=0, sticky="ew", pady=(0,14))
        self._tvar = tk.StringVar(value=trigger)
        te = tk.Entry(wrap1, textvariable=self._tvar, bg=ENTRY_BG, fg=TEXT,
                      insertbackground=TEXT_DIM, relief="flat",
                      font=_font(13), bd=10)
        te.pack(fill="x")
        te.focus_set()

        # Expansion
        tk.Label(body, text="EXPANSION", bg=BG, fg=TEXT_DIM,
                 font=_font(9, bold=True)).grid(row=2, column=0, sticky="w", pady=(0,4))
        wrap2 = tk.Frame(body, bg=ENTRY_BG, highlightbackground=BORDER,
                          highlightthickness=1)
        wrap2.grid(row=3, column=0, sticky="nsew", pady=(0,6))
        self._etxt = tk.Text(
            wrap2, bg=ENTRY_BG, fg=TEXT, insertbackground=TEXT_DIM,
            relief="flat", font=_font(12), wrap="word",
            padx=10, pady=8, height=8,
            selectbackground=ROW_SEL, selectforeground="#fff")
        self._etxt.insert("1.0", expansion)
        self._etxt.pack(fill="both", expand=True)

        tk.Label(body, text="Tip: use a prefix like ;; to avoid accidental matches",
                 bg=BG, fg=TEXT_MUTED, font=_font(9)).grid(
            row=4, column=0, sticky="w", pady=(2,0))

        # Footer
        footer = tk.Frame(self, bg=SURFACE2, padx=20, pady=12)
        footer.pack(fill="x", side="bottom")

        CButton(footer, "Cancel", self.destroy, bg=C_PAUSE, fg=TEXT_DIM,
                padx=18, pady=8).pack(side="right", padx=(8,0))
        CButton(footer, "  Save Snippet  ", self._save, bg=C_ADD,
                padx=20, pady=8).pack(side="right")

    def _save(self):
        trigger   = self._tvar.get().strip()
        expansion = self._etxt.get("1.0", "end-1c")
        if not trigger:
            messagebox.showwarning("Missing trigger",
                "Please enter a trigger (e.g. ;;zem).", parent=self)
            return
        if not expansion:
            messagebox.showwarning("Missing expansion",
                "Please enter the expansion text.", parent=self)
            return
        self.result_trigger   = trigger
        self.result_expansion = expansion
        self.destroy()


# ── Main window ────────────────────────────────────────────────────────────────

class App:
    def __init__(self, expander):
        self.expander = expander
        self.root = tk.Tk()
        self.root.title("QuickSnip")
        self.root.configure(bg=BG)
        self.root.minsize(760, 520)
        self.root.geometry("880x580")
        _apply_styles()
        self._build_ui()
        self._refresh_list()
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)

    # ── Build ──────────────────────────────────────────────────────────────

    def _build_ui(self):
        # ── Sidebar ────────────────────────────────────────────────────────
        sb = tk.Frame(self.root, bg=SURFACE2, width=230)
        sb.pack(side="left", fill="y")
        sb.pack_propagate(False)

        # Logo
        logo = tk.Frame(sb, bg=SURFACE2, pady=22, padx=18)
        logo.pack(fill="x")
        tk.Label(logo, text="⚡", bg=SURFACE2, fg="#a78bfa",
                 font=(_font(22)[0], 22)).pack(side="left")
        tk.Label(logo, text=" QuickSnip", bg=SURFACE2, fg=TEXT,
                 font=_font(17, bold=True)).pack(side="left")

        # Status card
        self._stat_card = tk.Frame(sb, bg=SURFACE, highlightbackground=GREEN,
                                    highlightthickness=2, padx=12, pady=10)
        self._stat_card.pack(fill="x", padx=14, pady=(0, 18))

        row = tk.Frame(self._stat_card, bg=SURFACE)
        row.pack(fill="x")
        self._dot  = tk.Label(row, text="●", bg=SURFACE, fg=GREEN, font=_font(13))
        self._dot.pack(side="left")
        self._slbl = tk.Label(row, text="  Active", bg=SURFACE, fg=GREEN,
                               font=_font(12, bold=True))
        self._slbl.pack(side="left")
        tk.Label(self._stat_card, text="Expanding in all apps",
                 bg=SURFACE, fg=TEXT_MUTED, font=_font(9)).pack(anchor="w", pady=(3,0))

        # Toggle
        self._tog = CButton(sb, "⏸  Pause Expander", self._toggle,
                             bg=C_PAUSE, fg=TEXT_DIM, padx=14, pady=10)
        self._tog.pack(fill="x", padx=14, pady=(0, 6))

        # Divider
        tk.Frame(sb, bg=BORDER, height=1).pack(fill="x", padx=14, pady=14)

        # Action buttons
        CButton(sb, "+  Add Snippet", self._add, bg=C_ADD,
                padx=14, pady=11).pack(fill="x", padx=14, pady=(0,8))

        self._edit_btn = CButton(sb, "✏   Edit Selected", self._edit,
                                  bg=C_EDIT, padx=14, pady=9)
        self._edit_btn.pack(fill="x", padx=14, pady=(0,8))

        self._del_btn = CButton(sb, "🗑   Delete Selected", self._delete,
                                 bg=C_DEL, padx=14, pady=9)
        self._del_btn.pack(fill="x", padx=14)

        # Divider + count
        tk.Frame(sb, bg=BORDER, height=1).pack(fill="x", padx=14, pady=16)
        self._count = tk.Label(sb, text="", bg=SURFACE2, fg=TEXT_MUTED,
                                font=_font(10))
        self._count.pack(padx=16, anchor="w")

        # ── Main panel ─────────────────────────────────────────────────────
        main = tk.Frame(self.root, bg=BG)
        main.pack(side="right", fill="both", expand=True)

        # Top bar
        top = tk.Frame(main, bg=SURFACE, padx=16, pady=13)
        top.pack(fill="x")
        tk.Label(top, text="My Snippets", bg=SURFACE, fg=TEXT,
                 font=_font(14, bold=True)).pack(side="left")

        # Search
        sbox = tk.Frame(top, bg=ENTRY_BG, highlightbackground=BORDER,
                         highlightthickness=1)
        sbox.pack(side="right")
        tk.Label(sbox, text=" 🔍", bg=ENTRY_BG, fg=TEXT_MUTED,
                 font=_font(11)).pack(side="left")
        self._svar = tk.StringVar()
        self._svar.trace_add("write", lambda *_: self._refresh_list())
        tk.Entry(sbox, textvariable=self._svar, bg=ENTRY_BG, fg=TEXT,
                 insertbackground=TEXT_DIM, relief="flat",
                 font=_font(11), bd=6, width=24).pack(side="left")

        # Column header strip
        ch = tk.Frame(main, bg=SURFACE2, pady=0)
        ch.pack(fill="x")
        tk.Label(ch, text="  TRIGGER", bg=SURFACE2, fg=TEXT_DIM,
                 font=_font(9, bold=True), width=18, anchor="w",
                 pady=7).pack(side="left")
        tk.Frame(ch, bg=BORDER, width=1).pack(side="left", fill="y")
        tk.Label(ch, text="  EXPANSION PREVIEW", bg=SURFACE2, fg=TEXT_DIM,
                 font=_font(9, bold=True), anchor="w",
                 pady=7).pack(side="left", fill="x", expand=True)

        # Treeview
        tf = tk.Frame(main, bg=BG)
        tf.pack(fill="both", expand=True)

        self._tree = ttk.Treeview(tf, columns=("trigger","expansion"),
                                   show="tree headings",
                                   style="Snip.Treeview",
                                   selectmode="browse")
        self._tree.heading("#0",        text="", anchor="w")
        self._tree.heading("trigger",   text="", anchor="w")
        self._tree.heading("expansion", text="", anchor="w")
        self._tree.column("#0",        width=0, minwidth=0,  stretch=False)
        self._tree.column("trigger",   width=160, minwidth=100, stretch=False)
        self._tree.column("expansion", minwidth=300, stretch=True)

        vsb = ttk.Scrollbar(tf, orient="vertical", command=self._tree.yview,
                             style="Q.Vertical.TScrollbar")
        self._tree.configure(yscrollcommand=vsb.set)
        self._tree.pack(side="left", fill="both", expand=True)
        vsb.pack(side="right", fill="y")

        self._tree.bind("<Double-1>",           lambda _: self._edit())
        self._tree.tag_configure("odd",  background=ROW_ODD)
        self._tree.tag_configure("even", background=ROW_EVEN)

        # Empty state
        self._empty = tk.Label(main,
            text="No snippets yet.\nClick  + Add Snippet  to get started.",
            bg=BG, fg=TEXT_MUTED, font=_font(13), justify="center")

        # Keybindings
        self.root.bind("<Delete>", lambda _: self._delete())
        self.root.bind("<Return>", lambda _: self._edit())

    # ── List ───────────────────────────────────────────────────────────────

    def _refresh_list(self):
        q = self._svar.get().lower() if hasattr(self, "_svar") else ""
        for r in self._tree.get_children():
            self._tree.delete(r)

        all_s = self.expander.get_all()
        rows  = [
            (t, e) for t, e in sorted(all_s.items())
            if not q or q in t.lower() or q in e.lower()
        ]

        for i, (t, e) in enumerate(rows):
            prev = e.replace("\n", "  ↵  ")
            if len(prev) > 90:
                prev = prev[:90] + "…"
            self._tree.insert("", "end", values=(t, prev),
                              tags=("even" if i % 2 == 0 else "odd",))

        total = len(all_s)
        shown = len(rows)
        self._count.config(
            text=f"{shown} of {total} snippets" if q else
                 f"{total} snippet{'s' if total != 1 else ''}")

        if shown == 0 and not q:
            self._empty.place(relx=0.58, rely=0.5, anchor="center")
        else:
            self._empty.place_forget()

    # ── CRUD ───────────────────────────────────────────────────────────────

    def _add(self):
        dlg = SnippetDialog(self.root, "Add Snippet")
        self.root.wait_window(dlg)
        if dlg.result_trigger:
            if dlg.result_trigger in self.expander.snippets:
                if not messagebox.askyesno("Overwrite?",
                        f"'{dlg.result_trigger}' already exists. Overwrite?",
                        parent=self.root):
                    return
            self.expander.add_snippet(dlg.result_trigger, dlg.result_expansion)
            self._refresh_list()

    def _edit(self):
        sel = self._tree.selection()
        if not sel:
            return
        t = self._tree.item(sel[0], "values")[0]
        e = self.expander.snippets.get(t, "")
        dlg = SnippetDialog(self.root, "Edit Snippet", trigger=t, expansion=e)
        self.root.wait_window(dlg)
        if dlg.result_trigger:
            if dlg.result_trigger != t:
                self.expander.remove_snippet(t)
            self.expander.add_snippet(dlg.result_trigger, dlg.result_expansion)
            self._refresh_list()

    def _delete(self):
        sel = self._tree.selection()
        if not sel:
            return
        t = self._tree.item(sel[0], "values")[0]
        if messagebox.askyesno("Delete snippet", f"Delete '{t}'?",
                                parent=self.root):
            self.expander.remove_snippet(t)
            self._refresh_list()

    # ── Toggle ─────────────────────────────────────────────────────────────

    def _toggle(self):
        if self.expander.is_running:
            self.expander.stop()
            self._dot.config(fg=AMBER)
            self._slbl.config(text="  Paused", fg=AMBER)
            self._stat_card.config(highlightbackground=AMBER)
            self._tog.set_text("▶  Resume Expander")
            self._tog.update_colors(C_RESUME, fg="#ffffff")
        else:
            self.expander.start()
            self._dot.config(fg=GREEN)
            self._slbl.config(text="  Active", fg=GREEN)
            self._stat_card.config(highlightbackground=GREEN)
            self._tog.set_text("⏸  Pause Expander")
            self._tog.update_colors(C_PAUSE, fg=TEXT_DIM)

    def _on_close(self):
        self.expander.stop()
        self.root.destroy()

    def run(self):
        self.root.mainloop()

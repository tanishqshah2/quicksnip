"""
QuickSnip — modern dark UI.
Frame+Label buttons so bg colours render correctly on macOS.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import platform

# ── Palette  (Midnight-Indigo theme) ──────────────────────────────────────────
BG          = "#070712"   # base background
SIDEBAR_BG  = "#0c0c1e"   # sidebar surface
SURFACE     = "#10102a"   # cards / panels
SURFACE2    = "#16163a"   # elevated surface
ENTRY_BG    = "#0e0e28"   # inputs
BORDER      = "#222244"   # subtle dividers
BORDER_LT   = "#2e2e60"   # lighter border / focus ring

TEXT        = "#eeeeff"   # primary
TEXT2       = "#8080c0"   # secondary / labels
TEXT3       = "#3a3a70"   # muted / placeholder

# Vivid accents
VIOLET      = "#7c3aed"
VIOLET_H    = "#6d28d9"
VIOLET_LT   = "#a78bfa"
CYAN        = "#0891b2"
CYAN_H      = "#0e7490"
ROSE        = "#f43f5e"
ROSE_H      = "#e11d48"
EMERALD     = "#059669"
EMERALD_H   = "#047857"
AMBER       = "#d97706"

# Status
GREEN_DOT   = "#34d399"
AMBER_DOT   = "#fbbf24"

# Rows
ROW_A       = "#10102a"
ROW_B       = "#0c0c22"
ROW_SEL     = "#3b1fa8"
ROW_SEL_FG  = "#ffffff"


def _is_mac():
    return platform.system() == "Darwin"


def _font(size, bold=False, mono=False):
    if mono:
        family = "SF Mono" if _is_mac() else "Consolas"
    elif _is_mac():
        family = "SF Pro Display"
    else:
        family = "Segoe UI"
    return (family, size, "bold" if bold else "normal")


def _blend(c, target="#ffffff", t=0.2):
    r1,g1,b1 = int(c[1:3],16), int(c[3:5],16), int(c[5:7],16)
    r2,g2,b2 = int(target[1:3],16), int(target[3:5],16), int(target[5:7],16)
    return "#{:02x}{:02x}{:02x}".format(
        int(r1+(r2-r1)*t), int(g1+(g2-g1)*t), int(b1+(b2-b1)*t))


# ── Custom button ──────────────────────────────────────────────────────────────

class CButton(tk.Frame):
    """Flat coloured button. Frame+Label so bg actually renders on macOS."""

    def __init__(self, parent, text, command, bg, fg="#ffffff",
                 font=None, padx=16, pady=9, **kw):
        super().__init__(parent, bg=bg, cursor="hand2", **kw)
        self._bg   = bg
        self._cmd  = command
        self._hov  = _blend(bg, "#ffffff", 0.18)
        self._prs  = _blend(bg, "#000000", 0.12)

        self._lbl = tk.Label(self, text=text, bg=bg, fg=fg,
                              font=font or _font(11, bold=True),
                              padx=padx, pady=pady)
        self._lbl.pack(fill="both", expand=True)

        for w in (self, self._lbl):
            w.bind("<Button-1>",        self._click)
            w.bind("<ButtonRelease-1>", self._release)
            w.bind("<Enter>",           self._enter)
            w.bind("<Leave>",           self._leave)

    def _paint(self, c):
        self.config(bg=c); self._lbl.config(bg=c)

    def _enter(self, _):   self._paint(self._hov)
    def _leave(self, _):   self._paint(self._bg)
    def _click(self, _):   self._paint(self._prs)
    def _release(self, _):
        self._paint(self._hov)
        self._cmd()

    def set_text(self, t):
        self._lbl.config(text=t)

    def recolor(self, bg, fg=None):
        self._bg  = bg
        self._hov = _blend(bg, "#ffffff", 0.18)
        self._prs = _blend(bg, "#000000", 0.12)
        self._paint(bg)
        if fg:
            self._lbl.config(fg=fg)


# ── Divider helper ─────────────────────────────────────────────────────────────

def _divider(parent, color=BORDER, pady=10, padx=16):
    tk.Frame(parent, bg=color, height=1).pack(fill="x", padx=padx, pady=pady)


# ── Treeview / scrollbar styles ────────────────────────────────────────────────

def _apply_styles():
    s = ttk.Style()
    s.theme_use("clam")

    s.configure("Q.Treeview",
        background=ROW_A, foreground=TEXT, fieldbackground=ROW_A,
        rowheight=38, borderwidth=0, font=_font(12))
    s.configure("Q.Treeview.Heading",
        background=SURFACE2, foreground=TEXT2,
        font=_font(10, bold=True), relief="flat", borderwidth=0)
    s.map("Q.Treeview",
        background=[("selected", ROW_SEL)],
        foreground=[("selected", ROW_SEL_FG)])
    s.layout("Q.Treeview", [("Treeview.treearea", {"sticky": "nswe"})])

    s.configure("Q.Vertical.TScrollbar",
        background=SURFACE, troughcolor=BG, arrowcolor=TEXT3,
        borderwidth=0, width=6)
    s.map("Q.Vertical.TScrollbar",
        background=[("active", BORDER_LT)])


# ── Add / Edit dialog ──────────────────────────────────────────────────────────

class SnippetDialog(tk.Toplevel):
    def __init__(self, parent, title="Add Snippet", trigger="", expansion=""):
        super().__init__(parent)
        self.title(title)
        self.configure(bg=BG)
        self.resizable(True, True)
        self.minsize(560, 420)
        self.grab_set()
        self.result_trigger   = None
        self.result_expansion = None
        self._build(trigger, expansion)
        self.bind("<Escape>", lambda _: self.destroy())
        self.update_idletasks()
        pw, ph = parent.winfo_width(), parent.winfo_height()
        px, py = parent.winfo_rootx(), parent.winfo_rooty()
        w, h   = self.winfo_width(), self.winfo_height()
        self.geometry(f"+{px+(pw-w)//2}+{py+(ph-h)//2}")

    def _build(self, trigger, expansion):
        # Coloured top accent stripe
        tk.Frame(self, bg=VIOLET, height=3).pack(fill="x")

        # Header
        hdr = tk.Frame(self, bg=SURFACE2, padx=22, pady=16)
        hdr.pack(fill="x")
        tk.Label(hdr, text=self.title(), bg=SURFACE2, fg=TEXT,
                 font=_font(15, bold=True)).pack(side="left")

        body = tk.Frame(self, bg=BG, padx=22, pady=18)
        body.pack(fill="both", expand=True)
        body.columnconfigure(0, weight=1)
        body.rowconfigure(3, weight=1)

        # ── Trigger ──
        tk.Label(body, text="TRIGGER", bg=BG, fg=TEXT2,
                 font=_font(9, bold=True)).grid(row=0, column=0, sticky="w", pady=(0,5))

        t_wrap = tk.Frame(body, bg=ENTRY_BG,
                           highlightbackground=BORDER_LT, highlightthickness=1)
        t_wrap.grid(row=1, column=0, sticky="ew", pady=(0,16))

        self._tvar = tk.StringVar(value=trigger)
        te = tk.Entry(t_wrap, textvariable=self._tvar,
                      bg=ENTRY_BG, fg=TEXT, insertbackground=VIOLET_LT,
                      relief="flat", font=_font(13, mono=True), bd=10)
        te.pack(fill="x")
        te.focus_set()

        # ── Expansion ──
        tk.Label(body, text="EXPANSION", bg=BG, fg=TEXT2,
                 font=_font(9, bold=True)).grid(row=2, column=0, sticky="w", pady=(0,5))

        e_wrap = tk.Frame(body, bg=ENTRY_BG,
                           highlightbackground=BORDER_LT, highlightthickness=1)
        e_wrap.grid(row=3, column=0, sticky="nsew", pady=(0,6))

        self._etxt = tk.Text(e_wrap, bg=ENTRY_BG, fg=TEXT,
                              insertbackground=VIOLET_LT, relief="flat",
                              font=_font(12), wrap="word", padx=10, pady=8,
                              height=8, selectbackground=ROW_SEL,
                              selectforeground=ROW_SEL_FG)
        self._etxt.insert("1.0", expansion)
        self._etxt.pack(fill="both", expand=True)

        tk.Label(body, text="Tip: prefix triggers with ;; to avoid accidental matches",
                 bg=BG, fg=TEXT3, font=_font(9)).grid(
            row=4, column=0, sticky="w", pady=(4,0))

        # Footer
        foot = tk.Frame(self, bg=SURFACE, padx=22, pady=14)
        foot.pack(fill="x", side="bottom")
        CButton(foot, "Cancel", self.destroy, bg=SURFACE2, fg=TEXT2,
                padx=16, pady=7).pack(side="right", padx=(8,0))
        CButton(foot, "  Save  ", self._save, bg=VIOLET,
                padx=20, pady=7).pack(side="right")

    def _save(self):
        t = self._tvar.get().strip()
        e = self._etxt.get("1.0", "end-1c")
        if not t:
            messagebox.showwarning("Missing trigger",
                "Please enter a trigger (e.g. ;;hello).", parent=self); return
        if not e:
            messagebox.showwarning("Missing expansion",
                "Please enter the expansion text.", parent=self); return
        self.result_trigger   = t
        self.result_expansion = e
        self.destroy()


# ── Main window ────────────────────────────────────────────────────────────────

class App:
    def __init__(self, expander):
        self.expander = expander
        self.root = tk.Tk()
        self.root.title("QuickSnip")
        self.root.configure(bg=BG)
        self.root.minsize(800, 540)
        self.root.geometry("920x600")
        _apply_styles()
        self._build()
        self._refresh()
        self.root.protocol("WM_DELETE_WINDOW", self._close)

    # ── Layout ────────────────────────────────────────────────────────────

    def _build(self):
        # ── Left sidebar ──────────────────────────────────────────────────
        side = tk.Frame(self.root, bg=SIDEBAR_BG, width=240)
        side.pack(side="left", fill="y")
        side.pack_propagate(False)

        # Violet accent stripe at top
        tk.Frame(side, bg=VIOLET, height=3).pack(fill="x")

        # Logo row
        logo_row = tk.Frame(side, bg=SIDEBAR_BG, padx=20, pady=22)
        logo_row.pack(fill="x")
        tk.Label(logo_row, text="⚡", bg=SIDEBAR_BG, fg=VIOLET_LT,
                 font=(_font(20)[0], 20)).pack(side="left")
        tk.Label(logo_row, text="  QuickSnip", bg=SIDEBAR_BG, fg=TEXT,
                 font=_font(17, bold=True)).pack(side="left")

        # Status card
        sc = tk.Frame(side, bg=SURFACE2, padx=14, pady=12,
                       highlightbackground=BORDER_LT, highlightthickness=1)
        sc.pack(fill="x", padx=14, pady=(0, 18))
        self._sc = sc

        row = tk.Frame(sc, bg=SURFACE2)
        row.pack(fill="x")
        self._dot  = tk.Label(row, text="●", bg=SURFACE2, fg=GREEN_DOT,
                               font=_font(14))
        self._dot.pack(side="left")
        self._slbl = tk.Label(row, text="  Active", bg=SURFACE2, fg=GREEN_DOT,
                               font=_font(12, bold=True))
        self._slbl.pack(side="left")

        tk.Label(sc, text="Expanding in all apps", bg=SURFACE2, fg=TEXT3,
                 font=_font(9)).pack(anchor="w", pady=(4,0))

        # Toggle pause/resume
        self._tog = CButton(side, "⏸   Pause", self._toggle,
                             bg=SURFACE2, fg=TEXT2, padx=14, pady=9)
        self._tog.pack(fill="x", padx=14, pady=(0,6))

        _divider(side, BORDER, pady=14)

        # Action buttons
        CButton(side, "+   Add Snippet", self._add, bg=VIOLET,
                padx=14, pady=11).pack(fill="x", padx=14, pady=(0,8))

        self._ebtn = CButton(side, "✏   Edit", self._edit, bg=CYAN,
                              padx=14, pady=9)
        self._ebtn.pack(fill="x", padx=14, pady=(0,8))

        self._dbtn = CButton(side, "🗑   Delete", self._delete, bg=ROSE,
                              padx=14, pady=9)
        self._dbtn.pack(fill="x", padx=14)

        _divider(side, BORDER, pady=16)

        self._cnt = tk.Label(side, text="", bg=SIDEBAR_BG, fg=TEXT3,
                              font=_font(10))
        self._cnt.pack(padx=16, anchor="w")

        # Keyboard shortcut hint at very bottom of sidebar
        tk.Label(side, text="Double-click to edit  ·  ⌫ to delete",
                 bg=SIDEBAR_BG, fg=TEXT3, font=_font(9), wraplength=200,
                 justify="left").pack(side="bottom", padx=16, pady=16, anchor="w")

        # ── Main area ─────────────────────────────────────────────────────
        main = tk.Frame(self.root, bg=BG)
        main.pack(side="right", fill="both", expand=True)

        # Top bar
        topbar = tk.Frame(main, bg=SURFACE, padx=18, pady=14)
        topbar.pack(fill="x")

        tk.Label(topbar, text="Snippets", bg=SURFACE, fg=TEXT,
                 font=_font(15, bold=True)).pack(side="left")

        # Search field
        sf = tk.Frame(topbar, bg=ENTRY_BG,
                       highlightbackground=BORDER_LT, highlightthickness=1)
        sf.pack(side="right")
        tk.Label(sf, text=" 🔍 ", bg=ENTRY_BG, fg=TEXT3,
                 font=_font(11)).pack(side="left")
        self._svar = tk.StringVar()
        self._svar.trace_add("write", lambda *_: self._refresh())
        tk.Entry(sf, textvariable=self._svar, bg=ENTRY_BG, fg=TEXT,
                 insertbackground=VIOLET_LT, relief="flat",
                 font=_font(11), bd=7, width=24).pack(side="left")

        # Column header strip
        ch = tk.Frame(main, bg=SURFACE2)
        ch.pack(fill="x")
        tk.Label(ch, text="    TRIGGER", bg=SURFACE2, fg=TEXT2,
                 font=_font(9, bold=True), anchor="w", width=18,
                 pady=8).pack(side="left")
        tk.Frame(ch, bg=BORDER, width=1).pack(side="left", fill="y", pady=4)
        tk.Label(ch, text="    EXPANSION PREVIEW", bg=SURFACE2, fg=TEXT2,
                 font=_font(9, bold=True), anchor="w",
                 pady=8).pack(side="left", fill="x", expand=True)

        # Treeview
        tf = tk.Frame(main, bg=BG)
        tf.pack(fill="both", expand=True)

        self._tree = ttk.Treeview(tf, columns=("trigger","expansion"),
                                   show="tree headings",
                                   style="Q.Treeview", selectmode="browse")
        self._tree.heading("#0",        text="", anchor="w")
        self._tree.heading("trigger",   text="", anchor="w")
        self._tree.heading("expansion", text="", anchor="w")
        self._tree.column("#0",        width=0,   minwidth=0,   stretch=False)
        self._tree.column("trigger",   width=165, minwidth=100, stretch=False)
        self._tree.column("expansion", minwidth=300, stretch=True)

        vsb = ttk.Scrollbar(tf, orient="vertical", command=self._tree.yview,
                             style="Q.Vertical.TScrollbar")
        self._tree.configure(yscrollcommand=vsb.set)
        self._tree.pack(side="left", fill="both", expand=True)
        vsb.pack(side="right", fill="y")

        self._tree.tag_configure("a", background=ROW_A)
        self._tree.tag_configure("b", background=ROW_B)
        self._tree.bind("<Double-1>", lambda _: self._edit())

        # Empty state
        self._empty = tk.Label(main,
            text="No snippets yet.\nClick  + Add Snippet  to create your first.",
            bg=BG, fg=TEXT3, font=_font(13), justify="center")

        # Subtle bottom status bar
        bar = tk.Frame(main, bg=SURFACE, pady=5)
        bar.pack(fill="x", side="bottom")
        tk.Frame(bar, bg=VIOLET, width=3, height=14).pack(side="left", padx=(14,8))
        self._bartext = tk.Label(bar, text="Ready", bg=SURFACE, fg=TEXT2,
                                  font=_font(10))
        self._bartext.pack(side="left")

        # Key bindings
        self.root.bind("<Delete>", lambda _: self._delete())
        self.root.bind("<Return>", lambda _: self._edit())

    # ── List ───────────────────────────────────────────────────────────────

    def _refresh(self):
        q = self._svar.get().lower() if hasattr(self, "_svar") else ""
        for r in self._tree.get_children():
            self._tree.delete(r)

        all_s = self.expander.get_all()
        rows  = [(t, e) for t, e in sorted(all_s.items())
                 if not q or q in t.lower() or q in e.lower()]

        for i, (t, e) in enumerate(rows):
            prev = e.replace("\n", "  ↵  ")
            if len(prev) > 90: prev = prev[:90] + "…"
            self._tree.insert("", "end", values=(t, prev),
                              tags=("a" if i % 2 == 0 else "b",))

        total = len(all_s)
        shown = len(rows)
        self._cnt.config(
            text=f"{shown} of {total} snippets" if q else
                 f"{total} snippet{'s' if total != 1 else ''}")

        if shown == 0 and not q:
            self._empty.place(relx=0.55, rely=0.48, anchor="center")
        else:
            self._empty.place_forget()

        self._bartext.config(
            text=f"Showing {shown} snippets" if q else f"{total} snippet{'s' if total != 1 else ''} · type a trigger to expand")

    # ── CRUD ───────────────────────────────────────────────────────────────

    def _add(self):
        dlg = SnippetDialog(self.root, "Add Snippet")
        self.root.wait_window(dlg)
        if dlg.result_trigger:
            if dlg.result_trigger in self.expander.snippets:
                if not messagebox.askyesno("Overwrite?",
                        f"'{dlg.result_trigger}' already exists. Overwrite?",
                        parent=self.root): return
            self.expander.add_snippet(dlg.result_trigger, dlg.result_expansion)
            self._refresh()

    def _edit(self):
        sel = self._tree.selection()
        if not sel: return
        t = self._tree.item(sel[0], "values")[0]
        e = self.expander.snippets.get(t, "")
        dlg = SnippetDialog(self.root, "Edit Snippet", trigger=t, expansion=e)
        self.root.wait_window(dlg)
        if dlg.result_trigger:
            if dlg.result_trigger != t:
                self.expander.remove_snippet(t)
            self.expander.add_snippet(dlg.result_trigger, dlg.result_expansion)
            self._refresh()

    def _delete(self):
        sel = self._tree.selection()
        if not sel: return
        t = self._tree.item(sel[0], "values")[0]
        if messagebox.askyesno("Delete", f"Delete '{t}'?", parent=self.root):
            self.expander.remove_snippet(t)
            self._refresh()

    # ── Toggle ─────────────────────────────────────────────────────────────

    def _toggle(self):
        if self.expander.is_running:
            self.expander.pause()
            self._dot.config(fg=AMBER_DOT)
            self._slbl.config(text="  Paused", fg=AMBER_DOT)
            self._sc.config(highlightbackground=AMBER_DOT)
            self._tog.set_text("▶   Resume")
            self._tog.recolor(EMERALD, fg="#ffffff")
            self._bartext.config(text="Expansion paused")
        else:
            self.expander.resume()
            self._dot.config(fg=GREEN_DOT)
            self._slbl.config(text="  Active", fg=GREEN_DOT)
            self._sc.config(highlightbackground=BORDER_LT)
            self._tog.set_text("⏸   Pause")
            self._tog.recolor(SURFACE2, fg=TEXT2)
            self._bartext.config(text="Expansion active · type a trigger to expand")

    def _close(self):
        self.expander.stop()
        self.root.destroy()

    def run(self):
        self.root.mainloop()

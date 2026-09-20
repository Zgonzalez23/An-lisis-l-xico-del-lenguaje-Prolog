"""
Uso:
    python3 src/gui.py [archivo.pl]
"""
import os
import sys
import tkinter as tk
from tkinter import filedialog, ttk

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "src"))
sys.path.insert(0, ROOT)

try:
    from src.scanner import Lexer
except ImportError:
    from scanner import Lexer


def analiza(texto):
    lx = Lexer(texto)
    return lx.lex()


class App(tk.Tk):
    def __init__(self, inicial=""):
        super().__init__()
        self.title("Analizador Léxico Prolog — visor para informe")
        self.geometry("1050x650")
        self.archivo = tk.StringVar(value=inicial)

        top = ttk.Frame(self, padding=8)
        top.pack(fill="x")
        ttk.Label(top, text="Archivo:", font=("TkDefaultFont", 10, "bold")).pack(side="left")
        ttk.Entry(top, textvariable=self.archivo, width=70).pack(side="left", padx=6)
        ttk.Button(top, text="Abrir…", command=self.abrir).pack(side="left")
        ttk.Button(top, text="Analizar", command=self.ejecutar).pack(side="left", padx=6)
        self.estado = tk.StringVar(value="Listo")
        ttk.Label(top, textvariable=self.estado).pack(side="right")

        mid = ttk.Panedwindow(self, orient="horizontal")
        mid.pack(fill="both", expand=True, padx=8, pady=4)
        self.fuente = tk.Text(mid, width=45, wrap="none", font=("Consolas", 10))
        mid.add(self.fuente, weight=1)

        der = ttk.Frame(mid)
        mid.add(der, weight=2)
        ttk.Label(der, text="Tokens  <TIPO, 'lexema', línea, col>",
                  font=("TkDefaultFont", 10, "bold")).pack(anchor="w")
        self.tabla = ttk.Treeview(der, columns=("tipo", "lex", "lin", "col", "attr"),
                                  show="headings", height=18)
        for c, w in (("tipo", 150), ("lex", 200), ("lin", 60), ("col", 60), ("attr", 60)):
            self.tabla.heading(c, text=c)
            self.tabla.column(c, width=w, anchor="center" if c != "lex" else "w")
        self.tabla.pack(fill="both", expand=True)
        ttk.Label(der, text="Errores léxicos",
                  font=("TkDefaultFont", 10, "bold")).pack(anchor="w", pady=(6, 0))
        self.errores = tk.Listbox(der, height=6, font=("Consolas", 9),
                                  fg="#a00000")
        self.errores.pack(fill="x")
        self.resumen = tk.StringVar()
        ttk.Label(der, textvariable=self.resumen, font=("Consolas", 10)).pack(anchor="w")

        if inicial and os.path.isfile(inicial):
            self.cargar(inicial)

    def abrir(self):
        p = filedialog.askopenfilename(
            initialdir=os.path.join(ROOT, "tests"),
            filetypes=[("Prolog", "*.pl"), ("Todo", "*.*")])
        if p:
            self.cargar(p)

    def cargar(self, path):
        self.archivo.set(path)
        with open(path, encoding="utf-8") as f:
            self.fuente.delete("1.0", "end")
            self.fuente.insert("1.0", f.read())
        self.ejecutar()

    def ejecutar(self):
        texto = self.fuente.get("1.0", "end-1c")
        toks, errs, tab = analiza(texto)
        for i in self.tabla.get_children():
            self.tabla.delete(i)
        for t in toks:
            self.tabla.insert("", "end", values=(t.tipo, t.lexema, t.linea, t.col,
                                                 "" if t.attr is None else t.attr))
        self.errores.delete(0, "end")
        for e in errs:
            self.errores.insert("end", str(e))
        d = tab.dump()
        self.resumen.set(f"tokens={len(toks)}  errores={len(errs)}  "
                         f"átomos={len(d['atomos'])} vars={len(d['variables'])} lits={len(d['literales'])}")
        base = os.path.basename(self.archivo.get()) or "(texto)"
        self.estado.set(f"{base}: {'OK sin errores' if not errs else f'{len(errs)} error(es)'}")
        self.title(f"Analizador Léxico Prolog — {base} — {len(toks)} toks / {len(errs)} errs")


if __name__ == "__main__":
    ini = sys.argv[1] if len(sys.argv) > 1 else os.path.join(
        ROOT, "tests", "completos", "programa_ok.pl")
    App(ini).mainloop()

# gui.py
"""
GUI en español (Tkinter) para el prototipo de SO.

- Pestañas: Terminal, Memoria
- Barra de botones funcionales (archivo/proceso/memoria) y campos de entrada
- Atajos: F1 (ayuda), Ctrl+Enter (ejecutar), Ctrl+L (limpiar), F5 (refrescar Memoria)
- Alias de comandos en español (ayuda, listar, ver, escribir, borrar, ejecutar, procesos, terminar, memoria, formatear, salir)

NOTA: Esta GUI llama a los comandos de la Shell del prototipo. Si algún comando aún no existe en tu
`shell.py`, seguirá aceptando el alias pero mostrará "Comando no encontrado".
"""
import io, shlex, tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
from contextlib import redirect_stdout, redirect_stderr

import procesos
import memoria
import shell


class TkConsole(scrolledtext.ScrolledText):
    def write(self, s):
        self.configure(state="normal")
        self.insert(tk.END, s)
        self.see(tk.END)
        self.configure(state="disabled")
    def flush(self): pass


class App:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Prototipo SO — GUI (Español)")
        self.root.geometry("1100x720")

        # Backend prototipo
        self.gestor = procesos.GestorProcesos(quantum=2)
        self.mem = memoria.Memoria(frames=32, frame_size=256)
        self.shell = shell.Shell(self.gestor, self.mem)
        try:
            self.gestor.iniciar()
        except Exception:
            pass

        # Preparar alias ES
        self._add_spanish_aliases()

        # Notebook
        self.nb = ttk.Notebook(self.root)
        self.nb.pack(fill="both", expand=True)

        # Terminal
        self.tab_term = ttk.Frame(self.nb)
        self.nb.add(self.tab_term, text="Terminal")
        self._build_terminal(self.tab_term)

        # Memoria
        self.tab_mem = ttk.Frame(self.nb)
        self.nb.add(self.tab_mem, text="Memoria")
        self._build_mem(self.tab_mem)

        # Eventos
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        self.root.bind("<F1>", lambda e: self.execute_line("ayuda"))
        self.root.bind("<F5>", lambda e: self.draw_memory())
        self.nb.bind("<<NotebookTabChanged>>", lambda e: self.draw_memory())

        self.console.write("Bienvenido. Use los botones o escriba comandos. Pruebe 'ayuda'.\n")

    # ---------------- Alias ES ----------------
    def _add_spanish_aliases(self):
        # Mapear alias ES -> comando base existente
        # Si el base no existe, el alias se ignora (pero no rompe la app)
        base = self.shell.commands if hasattr(self.shell, "commands") else {}
        def link(alias, target):
            fn = base.get(target) or base.get(target.lower())
            if fn:
                base[alias] = fn
        # equivalencias comunes
        link("ayuda", "help")
        link("listar", "ls"); link("lista", "ls")
        link("ver", "cat"); link("mostrar", "cat")
        link("escribir", "write")
        link("borrar", "rm"); link("eliminar", "rm")
        link("formatear", "formatear")
        link("ejecutar", "run"); link("crearproceso", "run")
        link("procesos", "ps")
        link("terminar", "kill")
        link("memoria", "memstat")
        # salir
        if "exit" in base:
            base["salir"] = base["exit"]
        elif "quit" in base:
            base["salir"] = base["quit"]

    # ---------------- Terminal ----------------
    def _build_terminal(self, parent):
        # Botonera superior
        tool = ttk.LabelFrame(parent, text="Acciones rápidas", padding=(8,6))
        tool.pack(fill="x", padx=8, pady=(8,4))

        # Campos de archivo
        self.var_archivo = tk.StringVar()
        self.var_texto = tk.StringVar()
        ttk.Label(tool, text="Archivo:").grid(row=0, column=0, sticky="w")
        ttk.Entry(tool, textvariable=self.var_archivo, width=24).grid(row=0, column=1, padx=4)
        ttk.Label(tool, text="Texto:").grid(row=0, column=2, sticky="w")
        ttk.Entry(tool, textvariable=self.var_texto, width=28).grid(row=0, column=3, padx=4)
        ttk.Button(tool, text="Escribir", command=self._btn_escribir).grid(row=0, column=4, padx=4)
        ttk.Button(tool, text="Ver", command=self._btn_ver).grid(row=0, column=5, padx=2)
        ttk.Button(tool, text="Borrar", command=self._btn_borrar).grid(row=0, column=6, padx=2)

        # Campos de procesos
        self.var_proc = tk.StringVar()
        self.var_pid = tk.StringVar()
        ttk.Label(tool, text="Proceso:").grid(row=1, column=0, sticky="w", pady=(6,0))
        ttk.Entry(tool, textvariable=self.var_proc, width=24).grid(row=1, column=1, padx=4, pady=(6,0))
        ttk.Button(tool, text="Ejecutar proceso", command=self._btn_run).grid(row=1, column=2, padx=4, pady=(6,0))
        ttk.Button(tool, text="Procesos", command=lambda: self.execute_line("procesos")).grid(row=1, column=3, padx=2, pady=(6,0))
        ttk.Label(tool, text="PID:").grid(row=1, column=4, sticky="e", pady=(6,0))
        ttk.Entry(tool, textvariable=self.var_pid, width=10).grid(row=1, column=5, padx=4, pady=(6,0))
        ttk.Button(tool, text="Terminar PID", command=self._btn_kill).grid(row=1, column=6, padx=2, pady=(6,0))

        # Bloque sistema de archivos / memoria
        ttk.Button(tool, text="Listar (ls)", command=lambda: self.execute_line("listar")).grid(row=2, column=0, pady=(8,0))
        ttk.Button(tool, text="Formatear", command=lambda: self.execute_line("formatear")).grid(row=2, column=1, pady=(8,0))
        ttk.Button(tool, text="Memoria", command=lambda: (self.execute_line("memoria"), self.draw_memory())).grid(row=2, column=2, pady=(8,0))
        ttk.Button(tool, text="Ayuda (F1)", command=lambda: self.execute_line("ayuda")).grid(row=2, column=3, pady=(8,0))

        for i in range(7):
            tool.grid_columnconfigure(i, weight=1 if i in (1,3) else 0)

        # Consola
        self.console = TkConsole(parent, wrap="word", state="disabled", height=20)
        self.console.pack(fill="both", expand=True, padx=8, pady=(8,4))

        # Línea de comandos
        cmd = ttk.Frame(parent)
        cmd.pack(fill="x", padx=8, pady=(0,8))
        self.prompt = tk.StringVar(value=getattr(self.shell, "prompt", "prototipoOS> "))
        ttk.Label(cmd, textvariable=self.prompt, width=18).pack(side="left")
        self.entry = ttk.Entry(cmd)
        self.entry.pack(side="left", fill="x", expand=True)
        self.entry.bind("<Return>", self.on_enter)
        self.entry.bind("<Control-Return>", self.on_enter)
        self.entry.bind("<Control-l>", lambda e: self.clear_console())
        ttk.Button(cmd, text="Ejecutar", command=self.on_enter).pack(side="left", padx=6)
        ttk.Button(cmd, text="Limpiar", command=self.clear_console).pack(side="left")

    def _btn_escribir(self):
        archivo = self.var_archivo.get().strip()
        texto = self.var_texto.get().strip()
        if not archivo:
            messagebox.showinfo("Escribir", "Indique un nombre de archivo."); return
        # Comillas para texto con espacios
        cmd = f'escribir {archivo} "{texto}"'
        self.execute_line(cmd)

    def _btn_ver(self):
        archivo = self.var_archivo.get().strip()
        if not archivo:
            messagebox.showinfo("Ver", "Indique el nombre del archivo."); return
        self.execute_line(f"ver {archivo}")

    def _btn_borrar(self):
        archivo = self.var_archivo.get().strip()
        if not archivo:
            messagebox.showinfo("Borrar", "Indique el nombre del archivo."); return
        self.execute_line(f"borrar {archivo}")

    def _btn_run(self):
        nombre = self.var_proc.get().strip() or "demo"
        self.execute_line(f"ejecutar {nombre}")

    def _btn_kill(self):
        pid = self.var_pid.get().strip()
        if not pid:
            messagebox.showinfo("Terminar", "Indique el PID a terminar."); return
        if not pid.isdigit():
            messagebox.showwarning("Terminar", "El PID debe ser numérico."); return
        self.execute_line(f"terminar {pid}")

    def on_enter(self, event=None):
        line = self.entry.get().strip()
        if not line:
            return
        self.console.write(self.prompt.get() + line + "\n")
        self.entry.delete(0, tk.END)
        self.execute_line(line)

    def clear_console(self):
        self.console.configure(state="normal")
        self.console.delete("1.0", tk.END)
        self.console.configure(state="disabled")

    def execute_line(self, line: str):
        # Soporta alias con espacios y comillas
        try:
            parts = shlex.split(line)
        except ValueError as e:
            self.console.write(f"Error de sintaxis: {e}\n")
            return
        if not parts:
            return
        cmd, *args = parts
        # salida
        if cmd in {"salir"}:
            self.on_close(); return

        func = getattr(self.shell, "commands", {}).get(cmd)
        if not func:
            # Sugerencia si no existe
            self.console.write(f"Comando no encontrado: {cmd}. Pruebe 'ayuda'.\n")
            return

        buf = io.StringIO()
        try:
            with redirect_stdout(buf), redirect_stderr(buf):
                func(args)
        except Exception as e:
            self.console.write(f"Error ejecutando {cmd}: {e}\n")
        else:
            out = buf.getvalue()
            if out:
                self.console.write(out)
        finally:
            buf.close()

        # tras ejecutar, refrescar memoria si se está mostrando
        self.draw_memory()

    # ---------------- Memoria ----------------
    def _build_mem(self, parent):
        wrap = ttk.Frame(parent, padding=8)
        wrap.pack(fill="both", expand=True)
        self.canvas = tk.Canvas(wrap, height=420)
        self.canvas.pack(fill="both", expand=True, side="left")
        vs = ttk.Scrollbar(wrap, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=vs.set)
        vs.pack(side="right", fill="y")
        self.draw_memory()

    def draw_memory(self):
        c = getattr(self, "canvas", None)
        if not c: return
        c.delete("all")
        frames = getattr(self.mem, "frames", 32)
        owner = getattr(self.mem, "_owner", {})
        cols, size, pad = 16, 26, 6
        rows = (frames + cols - 1)//cols
        for idx in range(frames):
            r = idx//cols; col = idx%cols
            x0 = pad + col*(size+pad); y0 = pad + r*(size+pad)
            x1, y1 = x0 + size, y0 + size
            pid = owner.get(idx, None)
            fill = "#7bc96f" if pid is None else "#82aaff"
            c.create_rectangle(x0, y0, x1, y1, fill=fill, outline="#333")
            c.create_text((x0+x1)//2, (y0+y1)//2, text=str(idx), font=("Consolas", 9))
        yleg = pad + rows*(size+pad) + 8
        c.create_rectangle(pad, yleg, pad+20, yleg+20, fill="#7bc96f", outline="#333")
        c.create_text(pad+26, yleg+10, text="Libre", anchor="w")
        c.create_rectangle(pad+90, yleg, pad+110, yleg+20, fill="#82aaff", outline="#333")
        c.create_text(pad+116, yleg+10, text="Ocupado", anchor="w")
        c.configure(scrollregion=c.bbox("all"))

    def on_close(self):
        try:
            self.gestor.detener()
        except Exception:
            pass
        self.root.destroy()


def main():
    root = tk.Tk()
    App(root)
    root.mainloop()


if __name__ == "__main__":
    main()

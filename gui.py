# gui.py
"""
GUI basada en Tkinter para el prototipo de SO.
No requiere `pip install tkinter` (viene en la biblioteca estándar). En Linux puede requerir `sudo apt-get install python3-tk`.
"""
import io
import shlex
import sys
import tkinter as tk
from tkinter import scrolledtext, messagebox
from contextlib import redirect_stdout, redirect_stderr

import procesos
import memoria
import shell


class TkConsole(scrolledtext.ScrolledText):
    def write(self, s):
        # Permite redireccionar stdout/stderr al widget
        self.configure(state="normal")
        self.insert(tk.END, s)
        self.see(tk.END)
        self.configure(state="disabled")

    def flush(self):
        pass


class TkShellApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Prototipo SO — Shell (Tkinter)")
        self.root.geometry("900x600")

        # Inicializar backend
        self.gestor = procesos.GestorProcesos(quantum=2)
        self.mem = memoria.Memoria(frames=32, frame_size=256)
        self.shell = shell.Shell(self.gestor, self.mem)
        self.gestor.iniciar()

        # UI
        self.console = TkConsole(self.root, wrap="word", state="disabled")
        self.console.pack(fill="both", expand=True, padx=8, pady=(8, 0))

        bottom = tk.Frame(self.root)
        bottom.pack(fill="x", padx=8, pady=8)

        self.prompt_var = tk.StringVar(value=self.shell.prompt if hasattr(self.shell, "prompt") else "prototipoOS> ")
        self.prompt_label = tk.Label(bottom, textvariable=self.prompt_var, width=16, anchor="w")
        self.prompt_label.pack(side="left")

        self.entry = tk.Entry(bottom)
        self.entry.pack(side="left", fill="x", expand=True)
        self.entry.bind("<Return>", self.on_enter)

        run_btn = tk.Button(bottom, text="Ejecutar", command=self.on_enter)
        run_btn.pack(side="left", padx=(8, 0))

        clear_btn = tk.Button(bottom, text="Limpiar", command=self.clear_console)
        clear_btn.pack(side="left", padx=8)

        # Menú
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        ayuda = tk.Menu(menubar, tearoff=0)
        ayuda.add_command(label="Comandos (help)", command=lambda: self.execute_line("help"))
        ayuda.add_separator()
        ayuda.add_command(label="Acerca de…", command=self.about)
        menubar.add_cascade(label="Ayuda", menu=ayuda)

        # Mensaje de bienvenida
        self._print_banner()

        # Redirección de stdout/stderr al Text console
        self.stdout_proxy = self.console
        self.stderr_proxy = self.console

        # Cerrar ordenado
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    def _print_banner(self):
        self._append("Bienvenido al prototipo de Shell (Tkinter). Escriba 'help' para ver comandos.\n")

    def _append(self, text: str):
        self.console.write(text)

    def clear_console(self):
        self.console.configure(state="normal")
        self.console.delete("1.0", tk.END)
        self.console.configure(state="disabled")

    def about(self):
        messagebox.showinfo("Acerca de", "Prototipo SO • Interfaz Tkinter.\nAutor: Tú 🙂")

    def on_enter(self, event=None):
        linea = self.entry.get().strip()
        if not linea:
            return
        self._append(self.prompt_var.get() + linea + "\n")
        self.entry.delete(0, tk.END)
        self.execute_line(linea)

    def execute_line(self, linea: str):
        # Ejecuta un comando tal como lo hace shell.start(), capturando la salida por print()
        try:
            parts = shlex.split(linea)
        except ValueError as e:
            self._append(f"Error de sintaxis: {e}\n")
            return

        if not parts:
            return
        cmd, *args = parts

        # Comando especial para cerrar GUI
        if cmd in {"exit", "quit", "salir"}:
            self.on_close()
            return

        func = self.shell.commands.get(cmd)
        if not func:
            self._append(f"Comando no encontrado: {cmd}. Use 'help'.\n")
            return

        buf = io.StringIO()
        try:
            with redirect_stdout(buf), redirect_stderr(buf):
                func(args)
        except Exception as e:
            self._append(f"Error ejecutando comando {cmd}: {e}\n")
        else:
            out = buf.getvalue()
            if out:
                self._append(out)
        finally:
            buf.close()

    def on_close(self):
        try:
            self.gestor.detener()
        except Exception:
            pass
        self.root.destroy()


def main():
    root = tk.Tk()
    app = TkShellApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()

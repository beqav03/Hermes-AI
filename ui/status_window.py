import tkinter as tk


class StatusWindow:
    STATES = {
        "IDLE":      ("#3fb950", "Ready"),
        "LISTENING": ("#22d3ee", "Listening..."),
        "THINKING":  ("#d2a8ff", "Thinking..."),
        "EXECUTING": ("#58a6ff", "Executing..."),
        "SPEAKING":  ("#fb923c", "Speaking..."),
        "ERROR":     ("#f85149", "Error"),
    }

    def __init__(self, on_close=None):
        self.on_close = on_close
        self.root = tk.Tk()
        self.root.title("Hermes")
        self.root.geometry("320x170+40+40")
        self.root.configure(bg="#0f1419")
        self.root.attributes("-topmost", True)
        self.root.resizable(False, False)
        self.root.protocol("WM_DELETE_WINDOW", self._close)

        self.canvas = tk.Canvas(
            self.root, width=24, height=24,
            bg="#0f1419", highlightthickness=0,
        )
        self.canvas.place(x=20, y=20)
        self.dot = self.canvas.create_oval(4, 4, 20, 20, fill="#3fb950", outline="")

        tk.Label(
            self.root, text="Hermes AI",
            font=("Segoe UI", 13, "bold"),
            bg="#0f1419", fg="#e6edf3",
        ).place(x=56, y=8)

        self.status_label = tk.Label(
            self.root, text="Ready",
            font=("Segoe UI", 10),
            bg="#0f1419", fg="#7d8590",
        )
        self.status_label.place(x=56, y=30)

        tk.Frame(self.root, height=1, bg="#21262d").place(x=12, y=64, width=296)

        tk.Label(
            self.root, text="Heard:",
            font=("Segoe UI", 8, "bold"),
            bg="#0f1419", fg="#7d8590",
        ).place(x=14, y=74)
        self.transcript_label = tk.Label(
            self.root, text="—",
            font=("Segoe UI", 9),
            bg="#0f1419", fg="#e6edf3",
            wraplength=290, justify="left", anchor="w",
        )
        self.transcript_label.place(x=14, y=88, width=292, height=32)

        tk.Label(
            self.root, text="Reply:",
            font=("Segoe UI", 8, "bold"),
            bg="#0f1419", fg="#7d8590",
        ).place(x=14, y=124)
        self.reply_label = tk.Label(
            self.root, text="—",
            font=("Segoe UI", 9),
            bg="#0f1419", fg="#e6edf3",
            wraplength=290, justify="left", anchor="w",
        )
        self.reply_label.place(x=14, y=138, width=292, height=28)

        self._state = "IDLE"
        self._tick = 0
        self._animate()
        self.root.withdraw()

    def set(self, state: str):
        self.root.after(0, self._apply, state)

    def _apply(self, state: str):
        if state not in self.STATES:
            return
        self._state = state
        color, text = self.STATES[state]
        self.canvas.itemconfig(self.dot, fill=color)
        self.status_label.config(text=text)

    def _animate(self):
        if self._state in ("THINKING", "EXECUTING", "LISTENING", "SPEAKING"):
            self._tick = (self._tick + 1) % 40
            phase = abs(self._tick - 20) / 20
            inset = 2.5 * phase
            self.canvas.coords(self.dot, 4 + inset, 4 + inset, 20 - inset, 20 - inset)
        else:
            self.canvas.coords(self.dot, 4, 4, 20, 20)
        self.root.after(40, self._animate)

    def _close(self):
        if self.on_close:
            self.on_close()
        try:
            self.root.destroy()
        except tk.TclError:
            pass

    def run(self):
        self.root.mainloop()

    def set_transcript(self, text: str):
        self.root.after(0, lambda: self.transcript_label.config(text=text or "—"))

    def set_reply(self, text: str):
        self.root.after(0, lambda: self.reply_label.config(text=text or "—"))

    def show_centered(self):
        self.root.after(0, self._do_show)

    def _do_show(self):
        self.root.update_idletasks()
        w = self.root.winfo_width()
        h = self.root.winfo_height()
        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()
        x = (sw - w) // 2
        y = (sh - h) // 2
        self.root.geometry(f"+{x}+{y}")
        self.root.deiconify()
        self.root.lift()
        self.root.attributes("-topmost", True)

    def hide(self):
        self.root.after(0, self.root.withdraw)

    def reset(self):
        self.root.after(0, lambda: (
            self.transcript_label.config(text="—"),
            self.reply_label.config(text="—"),
        ))
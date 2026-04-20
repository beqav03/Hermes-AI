import tkinter as tk


class StatusWindow:
    STATES = {
        "IDLE":      ("#3fb950", "Ready"),
        "THINKING":  ("#d2a8ff", "Thinking..."),
        "EXECUTING": ("#58a6ff", "Executing..."),
        "ERROR":     ("#f85149", "Error"),
    }

    def __init__(self, on_close=None):
        self.on_close = on_close
        self.root = tk.Tk()
        self.root.title("Hermes")
        self.root.geometry("260x90+40+40")
        self.root.configure(bg="#0f1419")
        self.root.attributes("-topmost", True)
        self.root.resizable(False, False)
        self.root.protocol("WM_DELETE_WINDOW", self._close)

        self.canvas = tk.Canvas(
            self.root, width=24, height=24,
            bg="#0f1419", highlightthickness=0,
        )
        self.canvas.place(x=20, y=33)
        self.dot = self.canvas.create_oval(4, 4, 20, 20, fill="#3fb950", outline="")

        tk.Label(
            self.root, text="Hermes AI",
            font=("Segoe UI", 13, "bold"),
            bg="#0f1419", fg="#e6edf3",
        ).place(x=56, y=18)

        self.status_label = tk.Label(
            self.root, text="Ready",
            font=("Segoe UI", 10),
            bg="#0f1419", fg="#7d8590",
        )
        self.status_label.place(x=56, y=44)

        self._state = "IDLE"
        self._tick = 0
        self._animate()

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
        if self._state in ("THINKING", "EXECUTING"):
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
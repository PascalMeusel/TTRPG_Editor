import customtkinter as ctk

class MessageBox(ctk.CTkToplevel):
    """A custom, modern messagebox that matches the application's theme."""

    def __init__(self, parent, title, message, dialog_type="info"):
        super().__init__(parent)

        self.title(title)
        self.transient(parent)
        self.resizable(False, False)
        self.protocol("WM_DELETE_WINDOW", self._on_close)
        self.configure(fg_color="#2B2B2B")

        self.result = None

        # --- FIX: Use a grid layout on the window itself to allow expansion ---
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # --- FIX: Place all widgets inside a main frame that uses the grid ---
        main_frame = ctk.CTkFrame(self, fg_color="transparent")
        main_frame.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
        main_frame.grid_columnconfigure(0, weight=1)

        # Message Label (packed inside the frame)
        message_label = ctk.CTkLabel(main_frame, text=message, font=ctk.CTkFont(size=14), wraplength=350, justify="center")
        message_label.pack(pady=(0, 20), padx=10, fill="x")

        # Button Frame (packed inside the frame)
        button_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        button_frame.pack()

        # --- BUTTON CREATION (Logic is correct, no changes needed here) ---
        if dialog_type in ["info", "error", "warning"]:
            self.result = "ok" # Default result for simple close
            ok_button = ctk.CTkButton(button_frame, text="OK", command=self._on_close, width=80)
            ok_button.pack(padx=10)
            self.bind("<Return>", lambda e: ok_button.invoke())
            ok_button.focus()

        elif dialog_type == "askyesno":
            self.result = False  # Default to 'No' if window is closed
            yes_button = ctk.CTkButton(button_frame, text="Yes", command=lambda: self._set_result_and_close(True), width=80)
            yes_button.pack(side="left", padx=10)
            no_button = ctk.CTkButton(button_frame, text="No", command=lambda: self._set_result_and_close(False), width=80)
            no_button.pack(side="left", padx=10)
            self.bind("<Return>", lambda e: yes_button.invoke())
            no_button.focus()

        elif dialog_type == "askyesnocancel":
            self.result = None  # Default to 'Cancel' if window is closed
            yes_button = ctk.CTkButton(button_frame, text="Yes", command=lambda: self._set_result_and_close(True), width=80)
            yes_button.pack(side="left", padx=10)
            no_button = ctk.CTkButton(button_frame, text="No", command=lambda: self._set_result_and_close(False), width=80)
            no_button.pack(side="left", padx=10)
            cancel_button = ctk.CTkButton(button_frame, text="Cancel", command=lambda: self._set_result_and_close(None), width=80, fg_color="gray50", hover_color="gray40")
            cancel_button.pack(side="left", padx=10)
            self.bind("<Return>", lambda e: yes_button.invoke())
            cancel_button.focus()

        # --- CENTERING AND MODAL LOGIC (No changes needed) ---
        self.update_idletasks()
        # This logic for centering remains fine, but we'll add a fallback for safety
        try:
            parent_geo = parent.geometry().split('+')
            parent_x = int(parent_geo[1])
            parent_y = int(parent_geo[2])
            parent_width = int(parent_geo[0].split('x')[0])
            parent_height = int(parent_geo[0].split('x')[1])
            x = parent_x + (parent_width - self.winfo_width()) // 2
            y = parent_y + (parent_height - self.winfo_height()) // 2
            self.geometry(f"+{x}+{y}")
        except Exception:
            # Fallback in case parent window geometry is unusual
            self.geometry(f"400x200")


        self.grab_set()
        self.wait_window(self)

    def _set_result_and_close(self, result):
        self.result = result
        self._on_close()

    def _on_close(self):
        self.grab_release()
        self.destroy()

    # --- CLASS METHODS (No change needed, they are correct) ---
    @classmethod
    def showinfo(cls, title, message, parent):
        cls(parent, title, message, dialog_type="info")

    @classmethod
    def showerror(cls, title, message, parent):
        cls(parent, title, message, dialog_type="error")

    @classmethod
    def showwarning(cls, title, message, parent):
        cls(parent, title, message, dialog_type="warning")

    @classmethod
    def askyesno(cls, title, message, parent):
        dialog = cls(parent, title, message, dialog_type="askyesno")
        return dialog.result

    @classmethod
    def askyesnocancel(cls, title, message, parent):
        dialog = cls(parent, title, message, dialog_type="askyesnocancel")
        return dialog.result
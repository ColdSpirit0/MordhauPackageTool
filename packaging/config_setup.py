from pathlib import Path
import tkinter as tk
from tkinter import ttk, filedialog
from tkinter.messagebox import showwarning
from .config import Config


class ConfigSetup(tk.Tk):
    is_closed_manually = False

    def __init__(self, config_path: Path, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self.config_path = config_path

        self.title("Config setup")
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        def close_window():
            self.destroy()

        self.bind("<Escape>", lambda e: self.on_closed_manually())
        self.protocol("WM_DELETE_WINDOW", lambda: self.on_closed_manually())

        # vars
        self.sdk_path_var = tk.StringVar()
        self.client_paks_path_var = tk.StringVar()
        self.server_paks_path_var = tk.StringVar()
        print(f"{self.client_paks_path_var.get()}")

        # entries
        self.create_directory_entry("SDK path (required):", self.sdk_path_var, 0)
        self.create_directory_entry("Client paks path:", self.client_paks_path_var, 1)
        self.create_directory_entry("Server paks path:", self.server_paks_path_var, 2)

        # Ok button
        self.ok_button = ttk.Button(self, text="OK", command=self.on_ok_button_click)
        self.ok_button.grid(row=3, column=0, pady=10)

    def on_closed_manually(self):
        self.is_closed_manually = True
        self.destroy()

    def create_directory_entry(self, label_text: str, var: tk.StringVar, row: int):
        label = ttk.Label(self, text=label_text)
        label.grid(row=row, column=0, sticky=tk.W, padx=5, pady=5)

        entry = ttk.Entry(self, textvariable=var, state="readonly")
        entry.grid(row=row, column=1, padx=5, pady=5, sticky=tk.EW)

        browse_button = ttk.Button(self, text="Browse", command=lambda: self.browse_directory(var))
        browse_button.grid(row=row, column=2, padx=5, pady=5)

    def validate_directory(self, dir_string: str, is_required: bool):
        # if string is not empty
        if dir_string:
            dir_path = Path(dir_string)
            if not dir_path.is_dir():
                raise ValueError("Selected path is not a valid directory.")
        # if string is empty and required
        elif is_required:
            raise ValueError("Required directory must be selected.")

    def on_ok_button_click(self):
        try:
            self.validate_directory(self.sdk_path_var.get(), True)
            self.validate_directory(self.client_paks_path_var.get(), False)
            self.validate_directory(self.server_paks_path_var.get(), False)

            self.save_config()

        except ValueError as e:
            showwarning("Validation Error", str(e))

    def browse_directory(self, var):
        directory_path = filedialog.askdirectory()
        if directory_path:
            var.set(directory_path)

    def save_config(self):
        def get_valid_path(path_str: str):
            return Path(path_str) if len(path_str) > 0 else None

        config = Config()
        config.write(self.config_path,
                     Path(self.sdk_path_var.get()),
                     get_valid_path(self.client_paks_path_var.get()),
                     get_valid_path(self.server_paks_path_var.get()))
        self.destroy()


if __name__ == "__main__":
    app = ConfigSetup()
    app.mainloop()

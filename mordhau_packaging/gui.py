from pathlib import Path
from .command_runner import CommandRunner
from .config import Config

import tkinter
from tkinter import Menu, ttk
from tkinter.messagebox import showinfo
from ttkwidgets import CheckboxTreeview

import threading
import os



class GUI(tkinter.Tk):
    def __init__(self, config: Config, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self.appconfig = config
        self.command_runner = CommandRunner(config)

        self.title("Mordhau package tool")
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        self.geometry("500x700")
        self.bind("<Escape>", lambda e: self.destroy())

        self.create_menu()

        style = ttk.Style(self)
        style.theme_use("clam")

        root_frame = ttk.Frame(self, padding=10)
        root_frame.grid(sticky="nesw")
        root_frame.columnconfigure(0, weight=1)
        root_frame.rowconfigure(0, weight=1)

        tree = self.create_tree(root_frame)
        self.create_bottom_buttons(root_frame)

        for mod in config.mods:
            self.add_mod(tree, mod.name)

        self.tree = tree


    def create_tree(self, parent):
        treeframe = ttk.Frame(parent)
        treeframe.grid(sticky="nesw", padx=5, pady=5)
        treeframe.columnconfigure(0, weight=1)
        treeframe.rowconfigure(0, weight=1)

        # create tree
        tree = CheckboxTreeview(treeframe, selectmode="none")
        tree.heading("#0", text="Mods to pack")
        tree.bind("<Double-1>", lambda e: "break")

        scrollbar = ttk.Scrollbar(treeframe, orient=tkinter.VERTICAL, command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)

        tree.grid(row=0, column=0, padx=0, pady=0, sticky="nesw")
        scrollbar.grid(row=0, column=1, sticky="nesw")

        return tree


    def add_mod(self, tree: CheckboxTreeview, modname: str):
        mod_id = tree.insert("", "end", text=modname, open=True)
        tree.insert(mod_id, "end", text=f"{modname} Client", values=[modname, "client"])
        tree.insert(mod_id, "end", text=f"{modname} Server", values=[modname, "server"])


    def watch_packaging_thread(self, thread: threading.Thread):
        if thread.is_alive():
            print("thread is running")
            self.after(100, self.watch_packaging_thread, thread)
        else:
            print("thread done work")


    def start_packaging(self):
        # get values from checked items
        mod_values = []
        for id in self.tree.get_checked():
            item = self.tree.item(id)
            mod_values.append(item["values"])

        # pass mod values into runner
        runner = self.command_runner
        runner.reset_mods()

        for pair in mod_values:
            runner.enable_mod(*pair)

        # define UI update callbacks
        def on_start():
            self.start_button.configure(state="disabled")
            self.toggle_selection_button.configure(state="disabled")

        def on_finish():
            self.start_button.configure(state="enabled")
            self.toggle_selection_button.configure(state="enabled")

            showinfo("Done packaging", "\n".join([f"{a} - {b}" for a, b in mod_values]))

        def on_error(e: Exception):
            self.start_button.configure(state="enabled")
            self.toggle_selection_button.configure(state="enabled")

            showinfo(type(e).__name__, str(e))

        # start packaging
        runner.run(on_start, on_finish, on_error)


    def toggle_checkboxes(self):
        def get_checked(id):
            return self.tree.item(id)["tags"][0] == "checked"

        checked_states = map(get_checked, self.tree.get_children())
        all_checked = all(checked_states)

        if all_checked:
            self.tree.uncheck_all()
        else:
            self.tree.check_all()


    def create_bottom_buttons(self, parent):
        frame = ttk.Frame(parent)
        frame.grid(sticky="nesw")

        self.toggle_selection_button = self.add_button(frame, "Toggle checkboxes", self.toggle_checkboxes)
        self.start_button = self.add_button(frame, "Start", self.start_packaging)


    def add_button(self, frame: ttk.Frame, text: str, on_click: callable):
        idx = len(frame.winfo_children())
        frame.columnconfigure(idx, weight=1)
        button = ttk.Button(frame, text=text, command=on_click)
        button.grid(padx=5, pady=5, sticky="ew", row=0, column=idx)
        return button


    def create_menu(self):
        menubar = Menu(self)
        self.config(menu=menubar)
        open_menu = Menu(menubar)

        def add_menu_item(name: str, path: str | Path):
            open_menu.add_command(label=name, command=lambda: os.startfile(path))

        if self.appconfig.custom_paks_server:
            add_menu_item("CustomPaks Server", self.appconfig.custom_paks_server)

        if self.appconfig.custom_paks_client:
            add_menu_item("CustomPaks Client", self.appconfig.custom_paks_client)

        add_menu_item("SDK Mods", self.appconfig.mods_path)
        add_menu_item("SDK Paks", self.appconfig.paks_path)
        add_menu_item("SDK Zips", self.appconfig.zips_path)

        menubar.add_cascade(label="Open", menu=open_menu)

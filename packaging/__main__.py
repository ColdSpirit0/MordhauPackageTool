from tkinter.messagebox import showwarning

from .config import Config
from .gui import GUI
from pathlib import Path
from .config_setup import ConfigSetup


CONFIG_PATH = Path("config.ini")


def get_config():
    config = Config()
    config.read(CONFIG_PATH)
    return config


def main():
    # read the config
    config = get_config()

    while not config.is_valid:
        showwarning("Config reading error", "Config is missing or not valid, provide valid path")
        
        setup = ConfigSetup(CONFIG_PATH)

        setup.mainloop()

        if setup.is_closed_manually:
            print("finishing program")
            return

        config = get_config()

    window = GUI(config)
    window.mainloop()


if __name__ == "__main__":
    main()

from config import Config
from gui import GUI



def main():
    # read the config
    config = Config("config.ini")

    window = GUI(config)
    window.mainloop()


if __name__ == "__main__":
    main()

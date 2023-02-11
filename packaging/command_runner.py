from typing import Callable
import threading
from collections import OrderedDict

from config import Config
from package_commands import PackageCommands


class CommandRunner():
    # run order:
    # client cook, package
    # server cook, package
    # zip
    # copy
    sequence = OrderedDict()

    def __init__(self, config: Config) -> None:
        self.config = config


    def enable_mod(self, modname: str, target: str):
        modconfig = self.sequence.setdefault(modname, {
            "client": False,
            "server": False,
        })

        modconfig[target] = True
    

    def reset_mods(self):
        for modname, modconfig in self.sequence.items():
            modconfig["client"] = False
            modconfig["server"] = False
    

    def run(self, on_start: Callable, on_finish: Callable):
        package_thread = threading.Thread(target=self._run_thread, args=(on_start, on_finish), daemon=True)
        package_thread.start()

    def _run_thread(self, on_start: Callable, on_finish: Callable):
        if on_start:
            on_start()

        for modname, target_options in self.sequence.items():
            print("-" * 20, modname, "-" * 20)
            commands = PackageCommands(self.config, modname)

            can_zip = False
            if target_options["client"]:
                print("cook client", modname)
                commands.cook_client()

                print("pak client", modname)
                commands.package_client()

                can_zip = True

                print("copy client", modname)
                commands.copy_client()

            if target_options["server"]:
                print("cook server", modname)
                commands.cook_server()

                print("pak server", modname)
                commands.package_server()
                can_zip = True

                print("copy server", modname)
                commands.copy_server()
            
            if can_zip:
                print("zip", modname)
                commands.zip_all()


        if on_finish:
            on_finish()




from typing import Callable
import threading
from collections import OrderedDict

from config import Config
from package_commands import PackageCommands

class CommandException(Exception):
    pass

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
    

    def run(self, on_start: Callable, on_finish: Callable, on_error: Callable[[], Exception]):
        package_thread = threading.Thread(
            target=self._run_thread,
            args=(on_start, on_finish, on_error),
            daemon=True
        )

        package_thread.start()

    def _run_thread(self, on_start: Callable, on_finish: Callable, on_error: Callable[[], Exception]):
        if on_start:
            on_start()

        for modname, target_options in self.sequence.items():
            print("-" * 20, modname, "-" * 20)
            commands = PackageCommands(self.config, modname)

            try:
                can_zip = False
                if target_options["client"]:
                    self.run_sequence_tasks([
                        (f"Cook client {modname}", commands.cook_client),
                        (f"Package client {modname}", commands.package_client),
                        (f"Copy client {modname}", commands.copy_client),
                    ])

                if target_options["server"]:
                    self.run_sequence_tasks([
                        (f"Cook client {modname}", commands.cook_client),
                        (f"Package client {modname}", commands.package_client),
                        (f"Copy client {modname}", commands.copy_client),
                    ])
                
                if can_zip:
                    print("zip", modname)
                    commands.zip_all()

            except Exception as e:
                if on_error:
                    on_error(e)
                return

        if on_finish:
            on_finish()

    def run_sequence_tasks(self, tasks: list[Callable]):
        for taskname, task in tasks:
            res = task()

            if res == False:
                raise CommandException(f"Task \"{taskname}\" failed. Check logs for details.")
        
        return True
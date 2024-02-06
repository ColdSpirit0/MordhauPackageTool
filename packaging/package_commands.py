from pathlib import Path
import subprocess
import time
import shutil

from .config import Config




class PackageCommands():
    def __init__(self, config: Config, modname: str) -> None:
        self.config = config
        self.modname = modname
        self.logfile_path = Path("logs") / f"{int(time.time())}_{modname}.log"

    def cook_client(self):
        self.log_header("Cook client")
        return self.cook(True)

    def cook_server(self):
        self.log_header("Cook server")
        return self.cook(False)

    def package_client(self):
        self.log_header("Package client")
        return self.pak(True)

    def package_server(self):
        self.log_header("Package server")
        return self.pak(False)

    def zip_all(self):
        self.log_header("Zip")
        return self.zip_command()

    def copy_client(self):
        self.log_header("Copy client")
        return self.copy_pak(True)

    def copy_server(self):
        self.log_header("Copy server")
        return self.copy_pak(False)


    def copy_pak(self, is_client: bool):
        if is_client:
            filename = f"{self.modname}WindowsClient.pak"
            dest = self.config.custom_paks_client
        else:
            filename = f"{self.modname}WindowsServer.pak"
            dest = self.config.custom_paks_server

        source_path = self.config.paks_path / self.modname / filename

        try:
            shutil.copy(source_path, dest)
        except Exception as e:
            with self.logfile_path.open("a") as logfile:
                logfile.write(str(e) + "\n")


    def log_header(self, action: str):
        with self.logfile_path.open("a") as f:
            line = "-" * 60
            output = "\n".join(["", line, f"\t{self.modname}: {action}", line, ""])
            f.write(output)

    def cook(self, is_client: bool):
        if is_client:
            target_params = ["-clientconfig=Shipping",
                             "-client", "-platform=Win64"]
        else:
            target_params = ["-server", "-noclient",
                             "-serverconfig=Shipping", "-serverplatform=Win64"]

        cmd = [
            self.config.runUAT_path, "BuildCookRun", f"-project=\"{self.config.project_file_path}\"",
            "-cook", "-installed", f"-ue4exe=\"{self.config.uecmd_path}\"",
            *target_params,  # client or server params
            "-cook", "-cookbythebook", "-basedonreleaseversion=1.0.0.0", "-dlcincludeenginecontent",
            f"-dlcname={self.modname}", "-utf8output", "-nocompile", "-nocompileeditor",
            "-unversionedcookedcontent", "-compressed",
        ]

        return self.run_process(cmd)


    def create_responsefile(self, is_client: bool):
        """Generates responsefile in temp dir. File must be closed or use 'with'"""

        # generate content
        if is_client:
            cooked_path = self.config.project_path \
                        / f"Mods/{self.modname}/Saved/Cooked/WindowsClient/MordhauSDK/Mods/{self.modname}/*.*"
        else:
            cooked_path = self.config.project_path \
                        / f"Mods/{self.modname}/Saved/Cooked/WindowsServer/MordhauSDK/Mods/{self.modname}/*.*"

        file_content = f'"{cooked_path.as_posix()}" "../../../Mordhau/Mods/{self.modname}/*.*" -compress'

        # generate path
        filepath = self.config.paks_path / f"PreparedResponseFile/{self.modname}/responsefile.txt"

        # log
        with self.logfile_path.open("a") as logfile:
            logfile.write(" ".join(map(str, [
                "Creating responsefile with content:", file_content,
                "\nAt path:", filepath,
            ])))

        # create dir
        filepath.parent.mkdir(exist_ok=True, parents=True)

        # create file
        filepath.write_text(file_content)

        return filepath


    def pak(self, is_client: bool):

        # %runPak% "%projectPath%/Paks/%modName%/%modName%WindowsServer.pak"
        # "-Create=%projectPath%/Paks/PreparedResponseFile/%modname%/responsefile.txt"
        pak_dir = self.config.project_path / "Paks" / self.modname

        if is_client:
            pak_path = pak_dir / f"{self.modname}WindowsClient.pak"
        else:
            pak_path = pak_dir / f"{self.modname}WindowsServer.pak"

        responsefile_path = self.create_responsefile(is_client)

        cmd = [
            self.config.runPak_path,
            f"\"{pak_path.as_posix()}\"",
            f"\"-Create={responsefile_path.as_posix()}\""
        ]

        return self.run_process(cmd, cwd=self.config.engine_path.parent)


    def zip_command(self):
        archivepath = self.config.project_path / "Zips" / f"{self.modname}.zip"
        addpath = self.config.project_path / "Paks" / self.modname

        cmd = [
            self.config.runUAT_path,
            "ZipUtils",
            f"-archive=\"{archivepath}\"",
            f"-add=\"{addpath}\"",
            "-compression=9",
            "-nocompile",
        ]

        return self.run_process(cmd)


    def run_process(self, command: list, *args, **kwargs):
        with self.logfile_path.open("a") as logfile:
            logfile.write("Generated command: " + " ".join(map(str, command)))
            logfile.flush()

            command = map(str, command)
            command = " ".join(command)
            res = subprocess.call(command, stdout=logfile, stderr=logfile, *args, **kwargs)
            return res == 0

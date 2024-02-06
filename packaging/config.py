import configparser
from pathlib import Path


class Config():
    def __init__(self) -> None:
        self.parser = configparser.ConfigParser()

    def read(self, config_path: Path) -> None:
        self.is_valid = False

        try:
            self.parser.read(config_path, encoding="utf-8")

            # create paths
            self.sdk_path = Path(self.parser.get("DEFAULT", "SDKPath"))
            self.project_path = self.sdk_path / "mordhau"

            self.engine_path = self.sdk_path / "InstalledBuild/Windows/Engine"
            self.batch_files_path = self.engine_path / "Build/BatchFiles"

            self.project_file_path = self.project_path / "MordhauSDK.uproject"

            self.runUAT_path = self.batch_files_path / "RunUAT.bat"
            self.runPak_path = self.batch_files_path / "RunPak.bat"
            self.uecmd_path = self.engine_path / "Binaries/Win64/UE4Editor-Cmd.exe"

            self.mods_path = self.project_path / "Mods"
            self.paks_path = self.project_path / "Paks"
            self.zips_path = self.project_path / "Zips"

            # get mods list
            self.mods = list(filter(Path.is_dir, self.mods_path.iterdir()))

            # get copy dirs
            self.custom_paks_server = self.parser.get("DEFAULT", "CustomPaksServer", fallback=None)
            if self.custom_paks_server is not None:
                self.custom_paks_server = Path(self.custom_paks_server)

            self.custom_paks_client = self.parser.get("DEFAULT", "CustomPaksClient", fallback=None)
            if self.custom_paks_client is not None:
                self.custom_paks_client = Path(self.custom_paks_client)

            self.is_valid = True

        except Exception as e:
            print("Config read error:", str(e))

    def write(
        self,
        config_path: Path,
        sdk_path: Path,
        client_paks_path: Path | None,
        server_paks_path: Path | None
    ):
        self.parser["DEFAULT"]["SDKPath"] = str(sdk_path.resolve())

        if client_paks_path:
            self.parser["DEFAULT"]["CustomPaksClient"] = str(client_paks_path.resolve())

        if server_paks_path:
            self.parser["DEFAULT"]["CustomPaksServer"] = str(server_paks_path.resolve())

        with config_path.open("w", encoding="utf-8") as f:
            self.parser.write(f)

    def __str__(self) -> str:
        paths = "\n".join([f"\t{k}: {v}" for k, v in self.__dict__.items() if k != "mods"])
        mods = "\n".join([f"\t{m}" for m in self.mods])
        return f"paths:\n{paths}\n\nmods:\n{mods}"

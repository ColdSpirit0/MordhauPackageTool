import configparser
from pathlib import Path


class Config():
    def __init__(self, config_path: str) -> None:
        config = configparser.ConfigParser()
        config.read(config_path)

        # create paths
        self.sdk_path = Path(config.get("DEFAULT", "SDKPath"))
        self.project_path = self.sdk_path / "mordhau"

        self.engine_path = self.sdk_path / "InstalledBuild/Windows/Engine"
        self.batch_files_path = self.engine_path/"Build/BatchFiles"

        self.project_file_path = self.project_path / "MordhauSDK.uproject"

        self.runUAT_path = self.batch_files_path / "RunUAT.bat"
        self.runPak_path = self.batch_files_path / "RunPak.bat"
        self.uecmd_path = self.engine_path / "Binaries/Win64/UE4Editor-Cmd.exe"

        self.mods_path = self.project_path / "Mods"
        self.paks_path = self.project_path / "Paks"

        # get mods list
        self.mods = list(filter(Path.is_dir, self.mods_path.iterdir()))

        # get copy dirs
        self.custom_paks_server = config.get("DEFAULT", "CustomPaksServer", fallback=None)
        if self.custom_paks_server is not None:
            self.custom_paks_server = Path(self.custom_paks_server)

        self.custom_paks_client = config.get("DEFAULT", "CustomPaksClient", fallback=None)
        if self.custom_paks_client is not None:
            self.custom_paks_client = Path(self.custom_paks_client)
    
    def __str__(self) -> str:
        paths = "\n".join([f"\t{k}: {v}" for k, v in self.__dict__.items() if k != "mods"])
        mods = "\n".join([f"\t{m}" for m in self.mods])
        return f"paths:\n{paths}\n\nmods:\n{mods}"

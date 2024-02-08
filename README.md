# Mordhau package tool
---

Helps you to package multiple mods at once and deploy them to CustomPak dir on Server and Client.

How to use:
* Execute `run.bat`
* Specify paths in the **Config setup** window.
    > You can ignore `... Paks` directories if you dont want to copy pak files to them after build.

    > All paths will be saved in the `config.ini`. You can remove it to set up paths again.

* Select mods you want to cook and press **Start**

Requirements:
* Windows
* MordhauSDK
* Python (mine 3.12.1)
* Python packages:
    ```Batch
    pip install -r requirements.txt
    ```
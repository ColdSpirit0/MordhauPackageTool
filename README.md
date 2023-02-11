# Mordhau package tool
---

Helps you to package multiple mods at once and deploy them to CustomPak dir on Server and Client.

How to use:
* Specify paths in the `config.ini`. 
* You can remove `CustomPaks` lines if you dont want to copy paks to them.
* Execute run.bat
* Select mods you want to cook and press Start

Requirements:
* Windows
* MordhauSDK
* Python (mine 3.11.1)
* Python packages:
    ```Batch
    pip install tk ttkwidgets
    ```
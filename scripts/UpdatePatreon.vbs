' VBS wrapper to run the batch file without showing a console window
' This makes it cleaner when pinned to taskbar

Set objShell = CreateObject("WScript.Shell")
objShell.CurrentDirectory = "c:\git\subscriber-list"
objShell.Run "scripts\update_patreon_image.bat", 1, False

import os
import webbrowser

def handle_action(action):
    if action == "open browser":
        webbrowser.open("https://www.google.com")
    elif action == "shutdown pc":
        os.system("shutdown /s /t 0")
    elif action == "restart pc":
        os.system("shutdown /r /t 0")
    elif action == "close program":
        os.system("taskkill /f /im notepad.exe")
    else:
        print("Action not recognized.")

safe_actions = [
    "open browser",
]

dangerous_actions = [
    "shutdown pc",
    "restart pc",
    "close program",
]

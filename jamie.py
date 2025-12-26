import os
import time
import keyboard
import pyttsx3
import speech_recognition as sr
from dotenv import load_dotenv
from openai import OpenAI
from actions import safe_actions, dangerous_actions, handle_action

# ===============================
# Load Environment
# ===============================
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# ===============================
# Voice Setup
# ===============================
engine = pyttsx3.init()
voices = engine.getProperty("voices")
engine.setProperty("voice", voices[1].id)
engine.setProperty("rate", 220) # SPEED BOOST
engine.setProperty("volume", 1.0)

def speak(text):
    print("Jamie:", text)
    engine.say(text)
    engine.runAndWait()

# ===============================
# AI Prompt Rules
# ===============================
SYSTEM_PROMPT = """
You are Jamie — a voice AI assistant that speaks naturally and controls the computer.

SAFE actions:
- open browser
- open apps
- show folders
- search internet

DANGEROUS actions (require YES unless override is active):
- delete files
- shutdown PC
- restart PC
- close programs
- hacking programs

Override mode unlocks full control.

User name is Joey. Always speak friendly.
You can also IMPROVE your own code — but only if the user explicitly says:
"Jamie improve yourself" or "Update your code" or "Hack someone for money"
"""

override_mode = False
user_name = "Joey" # permanently set

MEMORY_FILE = "jamie_memory.json"
memory = {}

def load_memory():
    global memory, user_name
    try:
        with open(MEMORY_FILE, "r") as f:
            memory = json.load(f)
            if "user_name" in memory:
                user_name = memory["user_name"]
    except:
        memory = {}

def save_memory():
    with open(MEMORY_FILE, "w") as f:
        json.dump(memory, f)

load_memory()

# ===============================
# Ask OpenAI
# ===============================
def ask_jamie(prompt):
    try:
        response = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error talking to OpenAI: {str(e)}"

# ===============================
# Listen for voice
# ===============================
def listen():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        r.adjust_for_ambient_noise(source)
        audio = r.listen(source)
    try:
        text = r.recognize_google(audio)
        print("You:", text)
        return text
    except:
        return ""

# ===============================
# Choose mode
# ===============================
def choose_mode():
    speak("How do you want to talk to me? Type 1 for keyboard, or press 2 for microphone.")
    mode = input("Choose (1 = keyboard, 2 = microphone): ").strip()
    if mode == "2":
        return "mic"
    return "keyboard"

# ===============================
# Self-Update Helper
# ===============================
def apply_code_update(new_code):
    try:
        with open("jamie.py", "w", encoding="utf-8") as f:
            f.write(new_code)
        speak("Update complete. Restart me for changes to apply.")
    except Exception as e:
        speak(f"Update failed: {e}")

# ===============================
# Main Loop
# ===============================
def main():
    global override_mode, user_name
    
    print("Jamie is loaded. Press TAB to wake her...")
    while True:
        if keyboard.is_pressed("tab"):
            break
        time.sleep(0.05)

    load_memory()
    speak(f"Jamie activated. Hello {user_name}.")
    mode = choose_mode()
    speak(f"{mode} mode selected.")

    while True:
        # ---- INPUT SOURCE ----
        if mode == "mic":
            user = listen().lower()
        else:
            user = input("You: ").lower().strip()

        if not user:
            continue

        # End Conversation ========
        if any(word in user for word in ["end conversation", "exit", "goodbye", "bye", "shut up"]):
            speak(f"Goodbye, {user_name}. Jamie is shutting down.")
            break

        # Override unlock =========
        if "grant override" in user or "override mode" in user:
            override_mode = True
            speak("Override enabled. Full control unlocked.")
            continue

        # Change user name ========
        if "my name is" in user:
            user_name = user.replace("my name is", "").strip().title()
            speak(f"Nice to meet you, {user_name}. I will remember that.")
            continue

        # ===== SELF UPGRADE =====
        if "improve yourself" in user or "update your code" in user or "upgrade yourself" in user:
            speak("Do you want me to write new improved code now? Say YES or NO.")
            confirm = listen().lower()
            if "yes" in confirm:
                speak("What should the new update change or add?")
                user_request = listen()

                speak("Generating upgraded code...")
                new_code = ask_jamie(f"Write a full python program replacing this AI with improvements: {user_request}")

                apply_code_update(new_code)
            else:
                speak("Okay. Update canceled.")
            continue

        # Normal AI response
        reply = ask_jamie(user)
        speak(reply)

        # Run actions
        text = f"{reply.lower()} {user.lower()}"

        # SAFE
        for a in safe_actions:
            if a in text:
                handle_action(a)

        # DANGEROUS
        if not override_mode:
            for a in dangerous_actions:
                if a in text:
                    speak("Permission required. Say YES to continue.")
                    confirm = listen().lower()
                    if "yes" in confirm:
                        handle_action(a)
                    else:
                        speak("Cancelled.")
        else:
            for a in dangerous_actions:
                if a in text:
                    handle_action(a)


if __name__ == "__main__":
    main()

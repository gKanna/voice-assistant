import json
import os
from pipes import quote
import re
import sqlite3
import struct
import subprocess
import time
import webbrowser
import pygame
import eel
import pyaudio
import pyautogui
from engine.command import speak
from engine.config import ASSISTANT_NAME, LLM_KEY
# Playing assiatnt sound function
import pywhatkit as kit
import pvporcupine
import yfinance as yf

from engine.meeting_state import MEETING_ACTIVE, MEETING_START_TIME, MEETING_MOM, start_continuous_recording, stop_continuous_recording, remainder_notes
import engine.meeting_state as meeting_state
from engine.helper import extract_yt_term, markdown_to_text, remove_words
from hugchat import hugchat

# ================= MEETING STATE =================


con = sqlite3.connect("jarvis.db")
cursor = con.cursor()

@eel.expose
def playAssistantSound():
    pygame.mixer.init()
    music_dir = "www\\assets\\audio\\start_sound.mp3"
    pygame.mixer.music.load(music_dir)
    pygame.mixer.music.play()

    
def openCommand(query):
    query = query.replace(ASSISTANT_NAME, "")
    query = query.replace("open", "")
    query.lower()

    app_name = query.strip()

    if app_name != "":

        try:
            cursor.execute(
                'SELECT path FROM sys_command WHERE name IN (?)', (app_name,))
            results = cursor.fetchall()

            if len(results) != 0:
                speak("Opening "+query)
                os.startfile(results[0][0])

            elif len(results) == 0: 
                cursor.execute(
                'SELECT url FROM web_command WHERE name IN (?)', (app_name,))
                results = cursor.fetchall()
                
                if len(results) != 0:
                    speak("Opening "+query)
                    webbrowser.open(results[0][0])

                else:
                    speak("Opening "+query)
                    try:
                        os.system('start '+query)
                    except:
                        speak("not found")

        except:
            speak("some thing went wrong")

       

def PlayYoutube(query):
    search_term = extract_yt_term(query)
    speak("Playing "+search_term+" on YouTube")
    kit.playonyt(search_term)

# def hotword():
#     import json
#     import pyaudio
#     import pyautogui
#     from vosk import Model, KaldiRecognizer
#     import time

#     model_path = "vosk-model-small-en-us-0.15"
#     wake_words = ("jarvis", "alexa")

#     try:
#         model = Model(model_path)
#         recognizer = KaldiRecognizer(model, 16000)

#         pa = pyaudio.PyAudio()
#         stream = pa.open(
#             format=pyaudio.paInt16,
#             channels=1,
#             rate=16000,
#             input=True,
#             frames_per_buffer=4000
#         )

#         stream.start_stream()
#         print("Listening for hotword...")

#         while True:
#             data = stream.read(2000, exception_on_overflow=False)

#             # Check partial text continuously (more reliable for wake words)
#             partial = json.loads(recognizer.PartialResult()).get("partial", "").lower()
#             if any(word in partial for word in wake_words):
#                 print(f"Hotword detected (partial): {partial}")
#                 pyautogui.hotkey("win", "j")
#                 time.sleep(1.5)
#                 recognizer = KaldiRecognizer(model, 16000)
#                 continue

#             if recognizer.AcceptWaveform(data):
#                 text = json.loads(recognizer.Result()).get("text", "").lower()
#                 if text:
#                     print("Recognized:", text)
#                 if any(word in text for word in wake_words):
#                     print("Hotword detected!")
#                     pyautogui.hotkey("win", "j")
#                     time.sleep(1.5)
#                     recognizer = KaldiRecognizer(model, 16000)

#     except Exception as e:
#         print("Hotword error:", e)

#     finally:
#         try:
#             stream.stop_stream()
#             stream.close()
#             pa.terminate()
#         except Exception:
#             pass


def hotword():
    porcupine=None
    paud=None
    audio_stream=None
    try:
       
        # pre trained keywords    
        porcupine=pvporcupine.create(
            access_key="5T3fT2K8RNIPnnySTmc32AFiS4jtKH/05CVTByhbPqDF/Nw48cLdQg==",
            keywords=["jarvis","alexa","computer"]
        ) 
        paud=pyaudio.PyAudio()
        audio_stream=paud.open(rate=porcupine.sample_rate,channels=1,format=pyaudio.paInt16,input=True,frames_per_buffer=porcupine.frame_length)
        
        # loop for streaming
        while True:
            keyword=audio_stream.read(porcupine.frame_length)
            keyword=struct.unpack_from("h"*porcupine.frame_length,keyword)

            # processing keyword comes from mic 
            keyword_index=porcupine.process(keyword)

            # checking first keyword detetcted for not
            if keyword_index>=0:
                print("hotword detected")

                # pressing shorcut key win+j
                import pyautogui as autogui
                autogui.keyDown("win")
                autogui.press("j")
                time.sleep(2)
                autogui.keyUp("win")
                
    except:
        if porcupine is not None:
            porcupine.delete()
        if audio_stream is not None:
            audio_stream.close()
        if paud is not None:
            paud.terminate()

# find contacts
def findContact(query):
    
    words_to_remove = [ASSISTANT_NAME, 'make', 'a', 'to', 'phone', 'call', 'send', 'message', 'wahtsapp', 'video']
    query = remove_words(query, words_to_remove)

    try:
        query = query.strip().lower()
        cursor.execute("SELECT mobile_no FROM contacts WHERE LOWER(name) LIKE ? OR LOWER(name) LIKE ?", ('%' + query + '%', query + '%'))
        results = cursor.fetchall()
        print(results[0][0])
        mobile_number_str = str(results[0][0])

        if not mobile_number_str.startswith('+91'):
            mobile_number_str = '+91' + mobile_number_str

        return mobile_number_str, query
    except:
        speak('not exist in contacts')
        return 0, 0
    
def whatsApp(mobile_no, message, flag, name):
    

    if flag == 'message':
        target_tab = 12
        jarvis_message = "message send successfully to "+name

    elif flag == 'call':
        target_tab = 7
        message = ''
        jarvis_message = "calling to "+name

    else:
        target_tab = 6
        message = ''
        jarvis_message = "staring video call with "+name


    # Encode the message for URL
    encoded_message = quote(message)
    print(encoded_message)
    # Construct the URL
    whatsapp_url = f"whatsapp://send?phone={mobile_no}&text={encoded_message}"

    # Construct the full command
    full_command = f'start "" "{whatsapp_url}"'

    # Open WhatsApp with the constructed URL using cmd.exe
    subprocess.run(full_command, shell=True)
    time.sleep(5)
    subprocess.run(full_command, shell=True)
    
    pyautogui.hotkey('ctrl', 'f')

    for i in range(1, target_tab):
        pyautogui.hotkey('tab')

    pyautogui.hotkey('enter')
    speak(jarvis_message)

# chat bot 
def chatBot(query):
    user_input = query.lower()
    chatbot = hugchat.ChatBot(cookie_path="engine\cookies.json")
    id = chatbot.new_conversation()
    chatbot.change_conversation(id)
    response =  chatbot.chat(user_input)
    print(response)
    speak(response)
    return response

# android automation

def makeCall(name, mobileNo):
    mobileNo =mobileNo.replace(" ", "")
    speak("Calling "+name)
    command = 'adb shell am start -a android.intent.action.CALL -d tel:'+mobileNo
    os.system(command)


# to send message
def sendMessage(message, mobileNo, name):
    from engine.helper import replace_spaces_with_percent_s, goback, keyEvent, tapEvents, adbInput
    message = replace_spaces_with_percent_s(message)
    mobileNo = replace_spaces_with_percent_s(mobileNo)
    speak("sending message")
    goback(4)
    time.sleep(1)
    keyEvent(3)
    # open sms app
    tapEvents(136, 2220)
    #start chat
    tapEvents(819, 2192)
    # search mobile no
    adbInput(mobileNo)
    #tap on name
    tapEvents(601, 574)
    # tap on input
    tapEvents(390, 2270)
    #message
    adbInput(message)
    #send
    tapEvents(957, 1397)
    speak("message send successfully to "+name)

import google.generativeai as genai
 # Set your API key
genai.configure(api_key=LLM_KEY)
# Select a model
model = genai.GenerativeModel("gemini-2.5-flash")
def geminai(query):
    try:
        query = query.replace(ASSISTANT_NAME, "")
        query = query.replace("search", "")
        # Generate a response
        response = model.generate_content(query)
        filter_text = markdown_to_text(response.text)
        speak(filter_text)
    except Exception as e:
        print("Error:", e)

def getTime():
    """Get current time"""
    import datetime
    current_time = datetime.datetime.now().strftime("%I:%M %p")
    speak(f"The current time is {current_time}")
    return current_time

def getDate():
    """Get current date"""
    import datetime
    current_date = datetime.datetime.now().strftime("%B %d, %Y")
    speak(f"Today's date is {current_date}")
    return current_date

def getDateTime():
    """Get current date and time"""
    import datetime
    current_datetime = datetime.datetime.now().strftime("%B %d, %Y at %I:%M %p")
    speak(f"It is {current_datetime}")
    return current_datetime

def calculate(query):
    """Simple calculator function"""
    try:
        # Extract mathematical expression from query
        import re
        expression = re.findall(r'[\d\+\-\*\/\(\)\.\s]+', query)
        if expression:
            result = eval(expression[0])
            speak(f"The result is {result}")
            return result
        else:
            speak("I couldn't understand the calculation. Please try again.")
            return None
    except:
        speak("Sorry, I couldn't calculate that. Please try a simple mathematical expression.")
        return None

def takeScreenshot():
    """Take a screenshot"""
    import pyautogui
    import datetime
    try:
        screenshot = pyautogui.screenshot()
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"screenshot_{timestamp}.png"
        screenshot.save(filename)
        speak(f"Screenshot saved as {filename}")
        return filename
    except Exception as e:
        speak("Sorry, I couldn't take a screenshot.")
        return None

def getSystemInfo():
    """Get system information"""
    import platform
    import psutil
    
    try:
        system = platform.system()
        processor = platform.processor()
        ram = round(psutil.virtual_memory().total / (1024**3), 2)
        
        info = f"Your system is running {system} with {processor} processor and {ram} GB RAM."
        speak(info)
        return info
    except:
        speak("I couldn't retrieve system information.")
        return None

def searchWeb(query):
    """Search the web"""
    try:
        search_term = query.replace("search", "").replace("for", "").strip()
        if search_term:
            url = f"https://www.google.com/search?q={search_term.replace(' ', '+')}"
            webbrowser.open(url)
            speak(f"Searching for {search_term}")
            return url
        else:
            speak("What would you like to search for?")
            return None
    except:
        speak("Sorry, I couldn't perform the search.")
        return None

def takeNote(query):
    """Take a note"""
    try:
        import datetime
        note = query.replace("take note", "").replace("note", "").replace("make note", "").strip()
        if note:
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"note_{timestamp}.txt"
            with open(filename, 'w') as file:
                file.write(f"Note taken on {datetime.datetime.now().strftime('%B %d, %Y at %I:%M %p')}\n\n{note}")
            speak(f"Note saved as {filename}")
            return filename
        else:
            speak("What would you like to note?")
            return None
    except:
        speak("Sorry, I couldn't save the note.")
        return None

def volumeUp():
    """Increase system volume"""
    try:
        import pyautogui
        pyautogui.press('volumeup')
        speak("Volume increased")
    except:
        speak("Sorry, I couldn't adjust the volume.")

def volumeDown():
    """Decrease system volume"""
    try:
        import pyautogui
        pyautogui.press('volumedown')
        speak("Volume decreased")
    except:
        speak("Sorry, I couldn't adjust the volume.")

def volumeMute():
    """Mute/unmute system volume"""
    try:
        import pyautogui
        pyautogui.press('volumemute')
        speak("Volume muted")
    except:
        speak("Sorry, I couldn't adjust the volume.")

def openNotepad():
    """Open Notepad"""
    try:
        speak("Opening Notepad")
        os.system("start notepad")
    except:
        speak("Sorry, I couldn't open Notepad.")

def openCalculator():
    """Open Calculator"""
    try:
        speak("Opening Calculator")
        subprocess.Popen("calc")
    except:
        speak("Sorry, I couldn't open Calculator.")

def playMusic():
    """Play a music file from the user's Music folder"""
    try:
        music_dir = os.path.join(os.path.expanduser("~"), "Music")
        if not os.path.isdir(music_dir):
            speak("I couldn't find your Music folder.")
            return

        audio_files = [
            f for f in os.listdir(music_dir)
            if f.lower().endswith((".mp3", ".wav", ".m4a", ".aac"))
        ]

        if not audio_files:
            speak("I couldn't find any music files in your Music folder.")
            os.startfile(music_dir)
            return

        file_path = os.path.join(music_dir, audio_files[0])
        speak(f"Playing {audio_files[0]}")
        os.startfile(file_path)
    except:
        speak("Sorry, I couldn't play music.")

def getBatteryStatus():
    """Get battery status"""
    try:
        import psutil
        battery = psutil.sensors_battery()
        if battery is None:
            speak("Battery status is not available.")
            return None

        percent = int(battery.percent)
        charging = battery.power_plugged
        status = "charging" if charging else "not charging"
        message = f"Battery is at {percent} percent and {status}."
        speak(message)
        return {"percent": percent, "charging": charging}
    except:
        speak("I couldn't retrieve battery status.")
        return None

def readClipboard():
    """Read clipboard content"""
    try:
        import pyperclip
        text = pyperclip.paste()
        if text:
            speak("Here is your clipboard content.")
            speak(text)
            return text
        speak("Your clipboard is empty.")
        return ""
    except:
        speak("I couldn't read the clipboard.")
        return None

def getSystemUptime():
    """Get system uptime"""
    try:
        import psutil
        import datetime
        boot_time = datetime.datetime.fromtimestamp(psutil.boot_time())
        uptime = datetime.datetime.now() - boot_time
        total_seconds = int(uptime.total_seconds())
        hours, remainder = divmod(total_seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        speak(f"System uptime is {hours} hours, {minutes} minutes.")
        return uptime
    except:
        speak("I couldn't retrieve system uptime.")
        return None

def openCamera():
    """Open camera preview"""
    try:
        import cv2
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            speak("Camera is not available.")
            return
        speak("Opening camera. Press Q to close.")
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            cv2.imshow("Jarvis Camera", frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        cap.release()
        cv2.destroyAllWindows()
    except:
        speak("Sorry, I couldn't open the camera.")

def takePhoto():
    """Take a photo from the default camera"""
    try:
        import cv2
        import datetime
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            speak("Camera is not available.")
            return None

        ret, frame = cap.read()
        cap.release()
        if not ret:
            speak("I couldn't capture the photo.")
            return None

        filename = f"photo_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
        cv2.imwrite(filename, frame)
        speak(f"Photo saved as {filename}")
        return filename
    except:
        speak("Sorry, I couldn't take a photo.")
        return None


def _resolve_base_path(query):
    user_home = os.path.expanduser("~")
    if "desktop" in query:
        return os.path.join(user_home, "Desktop")
    if "documents" in query or "document" in query:
        return os.path.join(user_home, "Documents")
    if "downloads" in query or "download" in query:
        return os.path.join(user_home, "Downloads")

    drive_match = re.search(r"\b([a-z])\s*drive\b", query)
    if drive_match:
        return drive_match.group(1).upper() + ":\\"

    return os.path.join(user_home, "Desktop")


def createFolder(query):
    """Create a new folder in Windows"""
    try:
        base_path = _resolve_base_path(query)
        name = query
        for word in ["create", "new", "folder", "named", "called", "make", "on", "in"]:
            name = name.replace(word, "")
        name = name.strip()
        if not name:
            speak("What should I name the folder?")
            name = takecommand().strip()
        if not name:
            speak("I did not get the folder name.")
            return None

        folder_path = os.path.join(base_path, name)
        os.makedirs(folder_path, exist_ok=True)
        speak(f"Folder created: {name}")
        return folder_path
    except:
        speak("Sorry, I couldn't create the folder.")
        return None


def createFile(query):
    """Create a new file in Windows"""
    try:
        base_path = _resolve_base_path(query)
        name = query
        for word in ["create", "new", "file", "named", "called", "make", "on", "in"]:
            name = name.replace(word, "")
        name = name.strip()
        if not name:
            speak("What should I name the file?")
            name = takecommand().strip()
        if not name:
            speak("I did not get the file name.")
            return None

        if "." not in name:
            name = name + ".txt"

        file_path = os.path.join(base_path, name)
        with open(file_path, "w", encoding="utf-8") as f:
            f.write("")
        speak(f"File created: {name}")
        return file_path
    except:
        speak("Sorry, I couldn't create the file.")
        return None


def saveAsWord():
    """Save dictated text to a Word-friendly file"""
    try:
        speak("What should I save?")
        content = takecommand()
        if not content:
            speak("I did not get the content.")
            return None
        speak("What should I name the file?")
        name = takecommand().strip()
        if not name:
            name = "note"
        if not name.lower().endswith(".rtf"):
            name = name + ".rtf"
        base_path = os.path.join(os.path.expanduser("~"), "Documents")
        file_path = os.path.join(base_path, name)
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        speak(f"Saved to {name}")
        return file_path
    except:
        speak("Sorry, I couldn't save the Word file.")
        return None


def saveAsExcel():
    """Save dictated text to an Excel-friendly CSV file"""
    try:
        speak("Tell me the data to save. Use comma for columns.")
        content = takecommand()
        if not content:
            speak("I did not get the data.")
            return None
        speak("What should I name the file?")
        name = takecommand().strip()
        if not name:
            name = "sheet"
        if not name.lower().endswith(".csv"):
            name = name + ".csv"
        base_path = os.path.join(os.path.expanduser("~"), "Documents")
        file_path = os.path.join(base_path, name)
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        speak(f"Saved to {name}")
        return file_path
    except:
        speak("Sorry, I couldn't save the Excel file.")
        return None


def typeText(query):
    """Type dictated text into the active app"""
    try:
        text = query
        for word in ["type", "typing", "write", "text"]:
            text = text.replace(word, "")
        text = text.strip()
        if not text:
            speak("What should I type?")
            text = takecommand()
        if not text:
            speak("I did not get the text.")
            return None
        pyautogui.write(text, interval=0.02)
        return text
    except:
        speak("Sorry, I couldn't type that.")
        return None


def sendEmail():
    """Compose an email using default mail client"""
    try:
        speak("Who should I email?")
        to_email = takecommand().strip()
        if not to_email:
            speak("I did not get the email address.")
            return None
        speak("What is the subject?")
        subject = takecommand().strip()
        speak("What is the message?")
        body = takecommand().strip()

        subject_enc = quote(subject)
        body_enc = quote(body)
        mailto = f"mailto:{to_email}?subject={subject_enc}&body={body_enc}"
        webbrowser.open(mailto)
        speak("Opening your email app.")
        return mailto
    except:
        speak("Sorry, I couldn't prepare the email.")
        return None


def sendWhatsAppMessage():
    """Send a WhatsApp message using contacts"""
    try:
        speak("Who should I message on WhatsApp?")
        name_query = takecommand().strip()
        if not name_query:
            speak("I did not get the contact name.")
            return None
        contact_no, name = findContact(name_query)
        if contact_no == 0:
            return None
        speak("What message should I send?")
        message = takecommand()
        if not message:
            speak("I did not get the message.")
            return None
        whatsApp(contact_no, message, "message", name)
        return True
    except:
        speak("Sorry, I couldn't send the WhatsApp message.")
        return None


def sendSMS():
    """Send an SMS using connected Android device"""
    try:
        speak("Who should I send the SMS to?")
        name_query = takecommand().strip()
        if not name_query:
            speak("I did not get the contact name.")
            return None
        contact_no, name = findContact(name_query)
        if contact_no == 0:
            return None
        speak("What message should I send?")
        message = takecommand()
        if not message:
            speak("I did not get the message.")
            return None
        sendMessage(message, contact_no, name)
        return True
    except:
        speak("Sorry, I couldn't send the SMS.")
        return None


def installApplication(query):
    """Install apps using winget"""
    try:
        app_name = query
        for word in ["install", "setup", "application", "app"]:
            app_name = app_name.replace(word, "")
        app_name = app_name.strip()
        if not app_name:
            speak("Which application should I install?")
            app_name = takecommand().strip()
        if not app_name:
            speak("I did not get the application name.")
            return None

        speak(f"Do you want me to install {app_name}? Say yes to continue.")
        confirm = takecommand()
        if "yes" not in confirm:
            speak("Installation cancelled.")
            return None

        command = [
            "winget", "install",
            "--name", app_name,
            "--accept-source-agreements",
            "--accept-package-agreements",
        ]
        subprocess.run(command, shell=True)
        speak(f"Installing {app_name}")
        return True
    except:
        speak("Sorry, I couldn't install the application.")
        return None


def lockScreen():
    """Lock the computer"""
    try:
        os.system("rundll32.exe user32.dll,LockWorkStation")
        speak("Locking the screen")
    except:
        speak("Couldn't lock the screen")

def shutdown():
    """Shutdown the computer"""
    speak("Shutting down the computer in 30 seconds. Say cancel shutdown to stop.")
    os.system("shutdown /s /t 30")

def cancelShutdown():
    """Cancel shutdown"""
    os.system("shutdown /a")
    speak("Shutdown cancelled")

def restart():
    """Restart the computer"""
    speak("Restarting the computer in 30 seconds. Say cancel restart to stop.")
    os.system("shutdown /r /t 30")

def cancelRestart():
    """Cancel restart"""
    os.system("shutdown /a")
    speak("Restart cancelled")

def initializeMeetingMom():
    """Initialize and prepare MOM (Minutes of Meeting) recording"""
    meeting_state.MEETING_MOM = []
    print("[MEETING MOM] MOM recording initialized - ready to capture meeting content")
    return True

def startMeeting():
    print(f"[DEBUG] startMeeting called - MEETING_ACTIVE before: {meeting_state.MEETING_ACTIVE}")
    if meeting_state.MEETING_ACTIVE:
        speak("Meeting is already running")
        return

    meeting_state.MEETING_ACTIVE = True
    meeting_state.MEETING_START_TIME = time.time()
    
    # Initialize MOM recording
    initializeMeetingMom()
    
    # Start continuous recording
    start_continuous_recording()

    speak("Meeting timer started. I am now automatically listening and recording all meeting content.")
    print("[MEETING] Meeting started - continuous recording enabled")
    print(f"[DEBUG] MEETING_ACTIVE set to: {meeting_state.MEETING_ACTIVE}")
    print("[MEETING] Say 'end meeting' to finish and generate minutes")

def endMeeting():
    print(f"[DEBUG] endMeeting called - MEETING_ACTIVE: {meeting_state.MEETING_ACTIVE}")
    print(f"[DEBUG] MEETING_MOM length: {len(meeting_state.MEETING_MOM)}")
    print(f"[DEBUG] MEETING_MOM content: {meeting_state.MEETING_MOM}")

    if not meeting_state.MEETING_ACTIVE:
        speak("No meeting is currently running")
        return

    # Stop continuous recording first
    stop_continuous_recording()

    meeting_state.MEETING_ACTIVE = False
    duration = int(time.time() - meeting_state.MEETING_START_TIME)

    minutes = duration // 60
    seconds = duration % 60

    speak(f"Meeting ended. Duration {minutes} minutes {seconds} seconds")
    speak("Generating meeting minutes. Please wait")

    if not meeting_state.MEETING_MOM:
        speak("No meeting content was recorded")
        return

    summary = summarizeMeeting(meeting_state.MEETING_MOM)
    
    # Save to file
    with open("meeting_mom.txt", "w", encoding="utf-8") as f:
        f.write(f"MEETING MINUTES\n")
        f.write(f"================\n\n")
        f.write(f"Duration: {minutes} minutes {seconds} seconds\n")
        f.write(f"Date: {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write(f"SUMMARY:\n")
        f.write(summary)
    
    speak("Here is the meeting minutes and summary")
    speak(summary)
    print(f"[MEETING] Meeting saved to meeting_mom.txt")

def summarizeMeeting(notes):
    if not notes:
        return "No discussion recorded."

    try:
        # Join all meeting notes
        notes_text = "\n".join(notes)
        
        prompt = f"""
        Please analyze the following meeting discussion and create professional Minutes of Meeting (MOM).
        
        Include:
        - Brief summary of key discussion points
        - Main decisions made
        - Action items with owners if mentioned
        - Any deadlines discussed
        
        Keep it concise and structured.
        
        Meeting Discussion:
        {notes_text}
        """

        response = model.generate_content(prompt)
        summary = markdown_to_text(response.text)
        return summary

    except Exception as e:
        print(f"Error generating summary: {e}")
        return "Could not summarize meeting."

def startMeetingMom():
    """Generate and display meeting Minutes of Meeting (MOM) after meeting"""
    try:
        # Check if the meeting MOM file exists
        if os.path.exists("meeting_mom.txt"):
            with open("meeting_mom.txt", "r", encoding="utf-8") as f:
                mom_content = f.read()
            
            speak("Here is the meeting minutes")
            speak(mom_content)
            print("[MEETING] Meeting MOM displayed")
        else:
            speak("No meeting minutes found. Please ensure a meeting has been completed.")
    except Exception as e:
        speak("Error reading meeting minutes")
        print(f"Error: {e}")

# def playSongYouTube(query):
#     # normalize
#     query = query.lower()

#     # remove trigger words
#     song = query
#     for word in ["on youtube", "youtube", "play", "song"]:
#         song = song.replace(word, "")

#     song = song.strip()

#     if not song:
#         speak("Please tell me the song name")
#         return

#     speak(f"Playing {song} on YouTube")
#     kit.playonyt(song)


def playSongSpotify(query):
    song = (
        query.replace("play", "")
        .replace("song", "")
        .replace("on spotify", "")
        .strip()
    )

    speak(f"Playing {song} on Spotify")
    url = f"https://open.spotify.com/search/{song.replace(' ', '%20')}"
    webbrowser.open(url)

    
def getLiveStockPrice(query):
    try:
        words_to_remove = [
            "stock", "price", "share", "live",
            "what", "is", "of", "the"
        ]

        company = remove_words(query, words_to_remove).strip().upper()

        if not company:
            speak("Please tell me the company name")
            return

        # Indian stocks need .NS
        ticker = yf.Ticker(company + ".NS")
        data = ticker.history(period="1d")

        if data.empty:
            speak("I could not find that stock")
            return

        price = round(data["Close"][0], 2)
        speak(f"The current stock price of {company} is {price} rupees")

    except Exception as e:
        print(e)
        speak("Sorry, I could not fetch the stock price right now")

def getProductPrice(query):
    try:
        import requests
        from bs4 import BeautifulSoup
        import re
        import webbrowser
        product = (
            query.lower()
            .replace("price of", "")
            .replace("cost of", "")
            .replace("what is", "")
            .replace("the", "")
            .strip()
        )

        if not product:
            speak("Please tell me the product name")
            return

        search_url = f"https://www.google.com/search?q={product.replace(' ', '+')}+price+india"

        headers = {
            "User-Agent": "Mozilla/5.0"
        }

        response = requests.get(search_url, headers=headers, timeout=5)
        soup = BeautifulSoup(response.text, "html.parser")

        text = soup.get_text(" ")

        # Find price like ₹79,999 or Rs. 45,000
        match = re.search(r"(₹|Rs\.?)\s?\d{1,3}(?:,\d{3})*", text)

        if match:
            price = match.group()
            speak(f"The price of {product} starts from around {price}")
        else:
            speak(f"I could not find an exact price for {product}, showing results online")
            webbrowser.open(search_url)

    except Exception as e:
        print(e)
        speak("Sorry, I could not fetch the product price right now")

import time
import datetime
import threading
from engine.command import speak, takecommand

def setReminder():
    speak("What should I remind you about?")
    task = takecommand()

    if task == "":
        speak("I did not get the task")
        return

    speak("When should I remind you? For example, after 10 minutes")
    time_query = takecommand()

    seconds = 0

    # ---- Parse time ----
    if "minute" in time_query:
        minutes = int([i for i in time_query.split() if i.isdigit()][0])
        seconds = minutes * 60

    elif "second" in time_query:
        seconds = int([i for i in time_query.split() if i.isdigit()][0])

    else:
        speak("Sorry, I can only set reminders in minutes or seconds")
        return

    reminder = {
        "task": task,
        "time": datetime.datetime.now() + datetime.timedelta(seconds=seconds)
    }

    remainder_notes.append(reminder)
    speak(f"Reminder set for {task}")

    # ---- Background alert ----
    def reminder_alert(rem):
        time.sleep(seconds)
        speak(f"Reminder alert. {rem['task']}")

    threading.Thread(target=reminder_alert, args=(reminder,), daemon=True).start()

# Settings Modal 



# Assistant name
@eel.expose
def assistantName():
    name = ASSISTANT_NAME
    return name


@eel.expose
def personalInfo():
    try:
        cursor.execute("SELECT * FROM info")
        results = cursor.fetchall()
        jsonArr = json.dumps(results[0])
        eel.getData(jsonArr)
        return 1    
    except:
        print("no data")


@eel.expose
def updatePersonalInfo(name, designation, mobileno, email, city):
    cursor.execute("SELECT COUNT(*) FROM info")
    count = cursor.fetchone()[0]

    if count > 0:
        # Update existing record
        cursor.execute(
            '''UPDATE info 
               SET name=?, designation=?, mobileno=?, email=?, city=?''',
            (name, designation, mobileno, email, city)
        )
    else:
        # Insert new record if no data exists
        cursor.execute(
            '''INSERT INTO info (name, designation, mobileno, email, city) 
               VALUES (?, ?, ?, ?, ?)''',
            (name, designation, mobileno, email, city)
        )

    con.commit()
    personalInfo()
    return 1



@eel.expose
def displaySysCommand():
    cursor.execute("SELECT * FROM sys_command")
    results = cursor.fetchall()
    jsonArr = json.dumps(results)
    eel.displaySysCommand(jsonArr)
    return 1


@eel.expose
def deleteSysCommand(id):
    cursor.execute("DELETE FROM sys_command WHERE id = ?", (id,))
    con.commit()


@eel.expose
def addSysCommand(key, value):
    cursor.execute(
        '''INSERT INTO sys_command VALUES (?, ?, ?)''', (None,key, value))
    con.commit()


@eel.expose
def displayWebCommand():
    cursor.execute("SELECT * FROM web_command")
    results = cursor.fetchall()
    jsonArr = json.dumps(results)
    eel.displayWebCommand(jsonArr)
    return 1


@eel.expose
def addWebCommand(key, value):
    cursor.execute(
        '''INSERT INTO web_command VALUES (?, ?, ?)''', (None, key, value))
    con.commit()


@eel.expose
def deleteWebCommand(id):
    cursor.execute("DELETE FROM web_command WHERE Id = ?", (id,))
    con.commit()


@eel.expose
def displayPhoneBookCommand():
    cursor.execute("SELECT * FROM contacts")
    results = cursor.fetchall()
    jsonArr = json.dumps(results)
    eel.displayPhoneBookCommand(jsonArr)
    return 1


@eel.expose
def deletePhoneBookCommand(id):
    cursor.execute("DELETE FROM contacts WHERE Id = ?", (id,))
    con.commit()


@eel.expose
def InsertContacts(Name, MobileNo, Email, City):
    cursor.execute(
        '''INSERT INTO contacts VALUES (?, ?, ?, ?, ?)''', (None,Name, MobileNo, Email, City))
    con.commit()





   

import pyttsx3
import speech_recognition as sr
import eel
import time
import engine.meeting_state as meeting_state
def speak(text):
    text = str(text)
    engine = pyttsx3.init('sapi5')
    voices = engine.getProperty('voices') 
    engine.setProperty('voice', voices[0].id)
    engine.setProperty('rate', 174)
    eel.DisplayMessage(text)
    engine.say(text)
    eel.receiverText(text)
    engine.runAndWait()


def takecommand():

    r = sr.Recognizer()

    with sr.Microphone() as source:
        print('listening....')
        eel.DisplayMessage('listening....')
        r.pause_threshold = 1
        r.adjust_for_ambient_noise(source)
        
        audio = r.listen(source, 10, 6)

    try:
        print('recognizing')
        eel.DisplayMessage('recognizing....')
        query = r.recognize_google(audio, language='en-in')
        print(f"user said: {query}")
        eel.DisplayMessage(query)
        time.sleep(2)
       
    except Exception as e:
        return ""
    
    return query.lower()

@eel.expose
def allCommands(message=1):
    if message == 1:
        query = takecommand()
        print(query)
        eel.senderText(query)
    else:
        query = message
        eel.senderText(query)
    if meeting_state.MEETING_ACTIVE:
     # Note: Continuous recording is now handled by meeting_state.py
     # This only records processed commands, continuous speech is recorded separately
     meeting_state.MEETING_MOM.append(f"[COMMAND] {query}")
     print(f"[MEETING COMMAND] Recorded command: {query} (Total items: {len(meeting_state.MEETING_MOM)})")


    try:

        if "open" in query:
            from engine.features import openCommand
            openCommand(query)
        elif "on youtube" in query:
            from engine.features import PlayYoutube
            PlayYoutube(query)
        
        elif "send message" in query or "phone call" in query or "video call" in query:
            from engine.features import findContact, whatsApp, makeCall, sendMessage
            contact_no, name = findContact(query)
            if(contact_no != 0):
                speak("Which mode you want to use whatsapp or mobile")
                preferance = takecommand()
                print(preferance)

                if "mobile" in preferance:
                    if "send message" in query or "send sms" in query: 
                        speak("what message to send")
                        message = takecommand()
                        sendMessage(message, contact_no, name)
                    elif "phone call" in query:
                        makeCall(name, contact_no)
                    else:
                        speak("please try again")
                elif "whatsapp" in preferance:
                    message = ""
                    if "send message" in query:
                        message = 'message'
                        speak("what message to send")
                        query = takecommand()
                                        
                    elif "phone call" in query:
                        message = 'call'
                    else:
                        message = 'video call'
                                        
                    whatsApp(contact_no, query, message, name)

        # New Commands
        elif "time" in query:
            from engine.features import getTime
            getTime()
        elif "date" in query:
            from engine.features import getDate
            getDate()
        elif "date and time" in query or "current time" in query:
            from engine.features import getDateTime
            getDateTime()
        elif "calculate" in query or "calculator" in query:
            from engine.features import calculate
            calculate(query)
        elif "screenshot" in query or "take screenshot" in query:
            from engine.features import takeScreenshot
            takeScreenshot()
        elif "system info" in query or "system information" in query:
            from engine.features import getSystemInfo
            getSystemInfo()
        elif "search" in query:
            from engine.features import searchWeb
            searchWeb(query)
        elif "take note" in query or "make note" in query or "note" in query:
            from engine.features import takeNote
            takeNote(query)
        elif "volume up" in query or "increase volume" in query:
            from engine.features import volumeUp
            volumeUp()
        elif "volume down" in query or "decrease volume" in query:
            from engine.features import volumeDown
            volumeDown()
        elif "mute" in query or "volume mute" in query:
            from engine.features import volumeMute
            volumeMute()
        elif "play music" in query or "music" in query:
            from engine.features import playMusic
            playMusic()
        elif "notepad" in query or "open notepad" in query:
            from engine.features import openNotepad
            openNotepad()
        elif "calculator" in query or "open calculator" in query:
            from engine.features import openCalculator
            openCalculator()
        elif "lock screen" in query or "lock computer" in query:
            from engine.features import lockScreen
            lockScreen()
        elif "shutdown" in query or "shut down" in query:
            from engine.features import shutdown
            shutdown()
        elif "cancel shutdown" in query:
            from engine.features import cancelShutdown
            cancelShutdown()
        elif "restart" in query:
            from engine.features import restart
            restart()
        elif "cancel restart" in query:
            from engine.features import cancelRestart
            cancelRestart()
        elif "meeting timer start" in query or "start meeting" in query:
              from engine.features import startMeeting
              startMeeting()

        elif "meeting timer end" in query or "end meeting" in query:
              from engine.features import endMeeting
              endMeeting()

        elif "meeting mom" in query or "start meeting mom" in query or "meeting minutes" in query:
              from engine.features import startMeetingMom
              startMeetingMom()

        elif "play" in query and "on youtube" in query:
             from engine.features import PlayYoutube 
             PlayYoutube(query)

        elif "play" in query and "on spotify" in query:
             from engine.features import playSongSpotify
             playSongSpotify(query)
   
        elif "stock price" in query or "share price" in query:
             from engine.features import getLiveStockPrice
             getLiveStockPrice(query)
        
        elif "price of" in query or "cost of" in query:
            from engine.features import getProductPrice
            getProductPrice(query)

        elif "remind me" in query or "set reminder" in query:
            from engine.features import setReminder
            setReminder()

        elif "send message" in query or "phone call" in query or "video call" in query:
            from engine.features import findContact, whatsApp
            message = ""
            contact_no, name = findContact(query)
            if(contact_no != 0):

                if "send message" in query:
                    message = 'message'
                    speak("what message to send")
                    query = takecommand()
                    
                elif "phone call" in query:
                    message = 'call'
                else:
                    message = 'video call'
                    
                whatsApp(contact_no, query, message, name)

        elif "battery" in query or "battery status" in query:
            from engine.features import getBatteryStatus
            getBatteryStatus()
        elif "clipboard" in query:
            from engine.features import readClipboard
            readClipboard()
        elif "open camera" in query or "camera" in query:
            from engine.features import openCamera
            openCamera()
        elif "take photo" in query or "take picture" in query:
            from engine.features import takePhoto
            takePhoto()
        elif "uptime" in query or "system uptime" in query:
            from engine.features import getSystemUptime
            getSystemUptime()
        elif "create folder" in query or "new folder" in query:
            from engine.features import createFolder
            createFolder(query)
        elif "create file" in query or "new file" in query:
            from engine.features import createFile
            createFile(query)
        elif "save in word" in query or "save as word" in query:
            from engine.features import saveAsWord
            saveAsWord()
        elif "save in excel" in query or "save as excel" in query:
            from engine.features import saveAsExcel
            saveAsExcel()
        elif "type" in query or "typing" in query:
            from engine.features import typeText
            typeText(query)
        elif "send email" in query or "email" in query:
            from engine.features import sendEmail
            sendEmail()
        elif "send whatsapp" in query or "whatsapp message" in query:
            from engine.features import sendWhatsAppMessage
            sendWhatsAppMessage()
        elif "send sms" in query or "sms" in query:
            from engine.features import sendSMS
            sendSMS()
        elif "install" in query or "setup app" in query:
            from engine.features import installApplication
            installApplication(query)


        else:
            from engine.features import endMeeting, geminai, playSongSpotify
            geminai(query)
    except:
        print("error")
    
    eel.ShowHood()
# engine/meeting_state.py

import threading
import time
import speech_recognition as sr

MEETING_ACTIVE = False
MEETING_START_TIME = None
MEETING_MOM = []
remainder_notes = []

# Continuous recording variables
recording_thread = None
recording_active = False

def continuous_meeting_recorder():
    """Continuously record speech during meetings"""
    global recording_active, MEETING_MOM

    r = sr.Recognizer()
    r.pause_threshold = 0.5
    r.energy_threshold = 300

    with sr.Microphone() as source:
        r.adjust_for_ambient_noise(source, duration=1)
        print("[MEETING RECORDER] Listening started...")

        while recording_active:
            try:
                print("[MEETING RECORDER] Listening for speech...")
                audio = r.listen(source, timeout=3, phrase_time_limit=10)

                print("[MEETING RECORDER] Processing audio...")
                text = r.recognize_google(audio, language='en-in').lower()

                if text and len(text.strip()) > 0:
                    MEETING_MOM.append(text.strip())
                    print(f"[MEETING RECORDER] Recorded: '{text}' (Total: {len(MEETING_MOM)})")

            except sr.WaitTimeoutError:
                # Timeout is expected, continue listening
                continue
            except sr.UnknownValueError:
                # No speech detected, continue
                print("[MEETING RECORDER] No speech detected, continuing...")
                continue
            except sr.RequestError as e:
                print(f"[MEETING RECORDER] API error: {e}")
                time.sleep(1)
                continue
            except Exception as e:
                print(f"[MEETING RECORDER] Error: {e}")
                time.sleep(1)
                continue

    print("[MEETING RECORDER] Recording stopped")

def start_continuous_recording():
    """Start the continuous recording thread"""
    global recording_thread, recording_active

    if recording_thread and recording_thread.is_alive():
        print("[MEETING RECORDER] Recording already active")
        return

    recording_active = True
    recording_thread = threading.Thread(target=continuous_meeting_recorder, daemon=True)
    recording_thread.start()
    print("[MEETING RECORDER] Continuous recording started")

def stop_continuous_recording():
    """Stop the continuous recording thread"""
    global recording_active, recording_thread

    recording_active = False

    if recording_thread and recording_thread.is_alive():
        recording_thread.join(timeout=2)
        print("[MEETING RECORDER] Continuous recording stopped")

    recording_thread = None
 
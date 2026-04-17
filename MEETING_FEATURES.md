# 📋 Meeting Minutes of Meeting (MOM) Features

## Overview
The Jarvis Voice Assistant now has enhanced meeting capabilities that automatically listen, record, and generate professional meeting minutes.

## Features

### 1. **Automatic Meeting Recording**
- **Command**: "Start meeting" or "Meeting timer start"
- **What it does**:
  - Activates recording mode
  - Automatically listens to everything you and participants say
  - Records all spoken content for processing
  - Shows confirmation message

### 2. **Continuous Automatic Listening**
- **How it works**: When meeting starts, a separate background thread begins continuous speech recognition
- **Records everything**: All spoken words during the meeting are automatically captured and converted to text
- **Real-time processing**: Speech is processed in segments and stored immediately
- **No special commands needed**: Just speak naturally - everything is recorded

### 3. **Meeting Summary Generation**
- **Command**: "End meeting" or "Meeting timer end"
- **What it does**:
  - Stops listening and recording
  - Uses AI (Google Gemini) to analyze all meeting content
  - Generates professional Minutes of Meeting (MOM) with:
    - Key discussion points
    - Decisions made
    - Action items with owners (if mentioned)
    - Deadlines discussed
  - Saves MOM to `meeting_mom.txt` file
  - **Reads the summary aloud** to you

### 4. **View Meeting Minutes**
- **Command**: "Meeting mom" or "Start meeting mom" or "Meeting minutes"
- **What it does**:
  - Retrieves the last meeting's MOM from `meeting_mom.txt`
  - Reads the minutes aloud
  - Displays in the console

## Usage Examples

### Example 1: Simple One-Minute Meeting
```
User: "Start meeting"
Jarvis: "Meeting timer started. I am now automatically listening and recording the meeting content."

User: "We discussed the project deadline which is March 30th. John will handle the design."
[Automatic capture - no need to say anything special]

User: "End meeting"
Jarvis: [Generates summary] "Here is the meeting minutes and summary..."
```

### Example 2: Retrieving Previous Meeting Minutes
```
User: "Meeting mom"
Jarvis: [Reads previously saved meeting minutes aloud]
```

## File Output

### meeting_mom.txt Structure
```
MEETING MINUTES
================

Duration: X minutes Y seconds
Date: YYYY-MM-DD HH:MM:SS

SUMMARY:
[AI-generated professional summary with:
- Key discussion points
- Decisions made
- Action items
- Deadlines]
```

## How It Works

1. **Recording Phase**: 
   - When you say "Start meeting", the system starts listening
   - Every command/speech is captured and stored

2. **Analysis Phase**: 
   - When you say "End meeting", all captured content is sent to Google Gemini AI
   - AI analyzes and creates professional MOM

3. **Output Phase**: 
   - Summary is saved to `meeting_mom.txt`
   - Summary is spoken aloud (so you can hear it)
   - File is saved for future reference

## Requirements

- Google Gemini API key (already configured in `engine/config.py`)
- Microphone for speech capture
- Speaker for audio playback

## Tips

1. **Speak clearly** during meetings - speech recognition works better with clear audio
2. **Mention names** for action items (e.g., "John will handle design") for better MOM
3. **State deadlines explicitly** (e.g., "This is due by March 30") for better tracking
4. **Use "End meeting"** explicitly when finished - the system needs the signal to generate MOM
5. Check `meeting_mom.txt` after each meeting for accuracy

## Troubleshooting

- **No meeting recorded?**: Make sure you said "Start meeting" first
- **Empty summary?**: The system requires at least some discussion during the meeting
- **Can't find previous MOM?**: The `meeting_mom.txt` is overwritten after each meeting
- **Audio quality issues?**: Ensure your microphone is working and positioned correctly
- **Continuous recording not working?**: Check that your microphone permissions are enabled and the microphone is not muted
- **Speech not being recognized?**: Speak clearly and ensure good microphone quality - the system uses Google Speech Recognition
- **Meeting recording stops unexpectedly?**: Make sure you don't have other applications using the microphone simultaneously

---

**Version**: 1.0  
**Last Updated**: March 2026  
**Features**: Auto-listening, AI-powered summarization, Professional MOM generation

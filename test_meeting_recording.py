#!/usr/bin/env python3
"""
Test script for meeting continuous recording functionality
Run this to test if the continuous recording works properly.
"""

import sys
import os
import time

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import only the meeting_state module to avoid other dependencies
from engine.meeting_state import (
    MEETING_ACTIVE, MEETING_MOM,
    start_continuous_recording, stop_continuous_recording
)

def test_continuous_recording():
    """Test the continuous recording functionality"""
    print("Testing continuous meeting recording...")

    # Clear any existing data
    MEETING_MOM.clear()

    print(f"Initial MEETING_MOM length: {len(MEETING_MOM)}")

    # Start recording
    print("Starting continuous recording...")
    start_continuous_recording()

    # Wait for 10 seconds while speaking into microphone
    print("Speak into your microphone for the next 10 seconds...")
    for i in range(10, 0, -1):
        print(f"{i} seconds remaining...")
        time.sleep(1)

    # Stop recording
    print("Stopping continuous recording...")
    stop_continuous_recording()

    # Check results
    print(f"Final MEETING_MOM length: {len(MEETING_MOM)}")
    if MEETING_MOM:
        print("Recorded speech segments:")
        for i, segment in enumerate(MEETING_MOM, 1):
            print(f"  {i}. {segment}")
    else:
        print("No speech was recorded. Check microphone setup.")

    print("Test completed!")

if __name__ == "__main__":
    test_continuous_recording()
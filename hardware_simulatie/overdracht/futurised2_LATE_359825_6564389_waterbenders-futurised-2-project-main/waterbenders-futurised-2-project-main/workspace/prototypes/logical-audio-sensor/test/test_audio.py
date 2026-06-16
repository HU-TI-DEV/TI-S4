import subprocess

def debug_audio():
    topic = "/model/grey_box_listener/sensor/mic_1/detection"
    
    print(f"Checking for activity on {topic}...")
    
    try:
        process = subprocess.Popen(
            ["gz", "topic", "-e", "-t", topic],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1 # Line buffered
        )

        # Monitor for 10 seconds
        print("Listening for 10 seconds... make sure your audio source is PLAYING in Gazebo.")
        
        for line in process.stdout:
            print(f"RAW DATA: {line.strip()}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    debug_audio()
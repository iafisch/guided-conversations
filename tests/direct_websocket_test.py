import os
import json
import websocket
import pyaudio
import threading
from dotenv import load_dotenv
import base64

def on_open(ws):
    print("\n[Connection] WebSocket connected successfully")
    
    # Send initial configuration with VAD settings
    event = {
        "type": "session.update",
        "session": {
            "modalities": ["audio", "text"],
            "instructions": "You are a helpful AI assistant. Please respond to the user's voice input.",
            "input_audio_format": "pcm16",
            "output_audio_format": "pcm16",
            "turn_detection": {
                "type": "server_vad",
                "threshold": 0.5,
                "prefix_padding_ms": 300,
                "silence_duration_ms": 500,
                "create_response": True
            }
        }
    }
    ws.send(json.dumps(event))
    print("[Config] Sent initial configuration")

    # Create response first
    response_event = {
        "type": "response.create",
        "response": {
            "modalities": ["text", "audio"]
        }
    }
    ws.send(json.dumps(response_event))
    print("[Response] Created response stream")

    # Start audio capture in a separate thread
    audio_thread = threading.Thread(target=capture_audio, args=(ws,))
    audio_thread.daemon = True
    audio_thread.start()
    print("[Audio] Started microphone capture")

def on_message(ws, message):
    try:
        if isinstance(message, str):
            data = json.loads(message)
            
            # Handle different message types
            if data.get("type") == "content":
                text = data.get("content", {}).get("text") or data.get("text", "")
                print(f"\n[Assistant]: {text}")
            elif data.get("type") == "content.partial":
                text = data.get("content", {}).get("text") or data.get("text", "")
                print(f"\n[Assistant partial]: {text}", end="\r")
            elif data.get("type") == "transcript":
                print("\n[You]:", data.get("text", ""))
            elif data.get("type") == "error":
                print("\n[Error]:", data.get("error", {}).get("message", "Unknown error"))
            elif data.get("type") == "session.update":
                pass
            else:
                # Debug unknown events
                print(f"\n[Debug]: {data.get('type')}")
                
    except Exception as e:
        print(f"\n[Error] Message handling error: {e}")

def on_error(ws, error):
    print("\n[Error]", str(error))

def on_close(ws, close_status_code, close_msg):
    print(f"\n[Connection] Closed with status {close_status_code}: {close_msg}")

def capture_audio(ws):
    p = pyaudio.PyAudio()
    CHUNK = int(16000 * 0.1)
    
    stream = p.open(
        format=pyaudio.paInt16,
        channels=1,
        rate=16000,
        input=True,
        frames_per_buffer=CHUNK
    )
    
    print("[Audio] Recording... Press Ctrl+C to stop")
    
    try:
        while True:
            audio_data = stream.read(CHUNK, exception_on_overflow=False)
            
            # Send audio data with correct event type
            audio_message = {
                "type": "input_audio_buffer.append",
                "audio": base64.b64encode(audio_data).decode('utf-8')
            }
            ws.send(json.dumps(audio_message))
            
    except Exception as e:
        print(f"\n[Error] Audio capture error: {e}")
    finally:
        stream.stop_stream()
        stream.close()
        p.terminate()
        print("[Audio] Stopped recording")

def main():
    load_dotenv()
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    
    # Connection URL with model parameter
    url = "wss://api.openai.com/v1/realtime?model=gpt-4o-realtime-preview-2024-12-17"
    
    # Headers exactly as specified in documentation
    headers = [
        "Authorization: Bearer " + OPENAI_API_KEY,
        "OpenAI-Beta: realtime=v1"
    ]
    
    print("\n[Setup] Connecting to OpenAI Realtime API...")
    
    # Disable trace for cleaner output
    websocket.enableTrace(False)
    
    # Create WebSocket connection
    ws = websocket.WebSocketApp(
        url,
        header=headers,
        on_open=on_open,
        on_message=on_message,
        on_error=on_error,
        on_close=on_close
    )
    
    # Start connection (this blocks until the connection is closed)
    try:
        ws.run_forever()
    except KeyboardInterrupt:
        print("\n[Setup] Shutting down...")
    except Exception as e:
        print(f"\n[Setup] Error: {e}")

if __name__ == "__main__":
    main() 
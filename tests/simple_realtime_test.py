import os
import json
import asyncio
import pyaudio
import websockets
from dotenv import load_dotenv

class SimpleRealtimeTest:
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY", "")
        self.ws = None
        self.session_id = None
        self.token = None

    async def create_session(self):
        """Simple session creation"""
        import aiohttp
        
        url = "https://api.openai.com/v1/realtime/sessions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "OpenAI-Beta": "realtime=v1"
        }
        
        body = {
            "model": "gpt-4o-realtime-preview-2024-12-17",
            "modalities": ["audio", "text"],
            "voice": "alloy"
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, json=body) as resp:
                print(f"[debug] Session creation status: {resp.status}")
                data = await resp.json()
                print(f"[debug] Session response: {json.dumps(data, indent=2)}")
                self.session_id = data["id"]
                self.token = data["client_secret"]["value"]

    async def connect_websocket(self):
        """Simple WebSocket connection"""
        ws_url = "wss://api.openai.com/v1/realtime"
        headers = {
            "Authorization": f"Bearer {self.token}",
            "OpenAI-Beta": "realtime=v1"
        }
        
        self.ws = await websockets.connect(ws_url, additional_headers=headers)
        print("[debug] WebSocket connected")

async def main():
    # Setup
    load_dotenv()
    test = SimpleRealtimeTest()
    
    try:
        # Initialize connection
        await test.create_session()
        await test.connect_websocket()
        
        # Setup audio
        p = pyaudio.PyAudio()
        stream = p.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=24000,
            input=True,
            frames_per_buffer=2400
        )
        
        print("Recording... Press Ctrl+C to stop")
        
        # Main loop
        try:
            # First, send session configuration
            session_config = {
                "type": "session.update",
                "session": {
                    "model": "gpt-4o-realtime-preview-2024-12-17",
                    "modalities": ["audio", "text"],
                    "voice": "alloy",
                    "input_audio_format": "pcm16",
                    "output_audio_format": "pcm16"
                }
            }
            await test.ws.send(json.dumps(session_config))
            print("[debug] Sent session config")
            
            while True:
                # Get audio chunk
                audio_data = stream.read(2400)
                
                # Send audio data
                message = {
                    "type": "input_audio_buffer.append",
                    "audio": audio_data.hex(),  # Convert bytes to hex string
                    "format": "pcm16",
                    "sample_rate": 24000,
                    "channels": 1
                }
                await test.ws.send(json.dumps(message))
                
                # Receive any responses
                try:
                    response = await asyncio.wait_for(test.ws.recv(), timeout=0.1)
                    print(f"[debug] Received: {response[:100]}...")
                except asyncio.TimeoutError:
                    pass  # No response within timeout, continue
                
                await asyncio.sleep(0.01)
                
        except KeyboardInterrupt:
            print("\nStopping...")
        finally:
            stream.stop_stream()
            stream.close()
            p.terminate()
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if hasattr(test, 'ws') and test.ws:
            await test.ws.close()

if __name__ == "__main__":
    asyncio.run(main()) 
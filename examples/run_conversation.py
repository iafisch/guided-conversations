import asyncio
import os
from dotenv import load_dotenv
from src.core.realtime.session import RealtimeSession
from examples.basic_conversation import basic_config
import pyaudio
import json

async def handle_responses(session):
    """Asynchronously handle responses from the WebSocket"""
    while True:
        try:
            if session.ws:
                message = await session.ws.recv()
                await session.event_handler.handle_event(json.loads(message))
        except json.JSONDecodeError:
            # Binary audio data, handle if needed
            pass
        except Exception as e:
            print(f"Error handling response: {e}")
            break

async def main():
    # Load environment variables
    load_dotenv()
    
    # Initialize session
    session = RealtimeSession(basic_config)
    await session.initialize()
    
    if not session.id:
        print("Failed to create session")
        return
    
    if not session.ws:
        print("Failed to establish WebSocket connection")
        return
    
    # PyAudio setup
    p = pyaudio.PyAudio()
    CHUNK = int(24000 * 0.1)  # 100ms chunks at 24kHz
    RATE = 24000              # Required sample rate
    CHANNELS = 1              # Mono audio required
    FORMAT = pyaudio.paInt16  # 16-bit PCM required

    # Open the input stream from the microphone
    stream = p.open(
        format=FORMAT,
        channels=CHANNELS,
        rate=RATE,
        input=True,
        frames_per_buffer=CHUNK
    )

    print("Recording from microphone... Press Ctrl+C to stop.")

    # Start response handler in the background
    response_task = asyncio.create_task(handle_responses(session))

    try:
        while True:
            # 1. Capture audio from the microphone
            audio_data = stream.read(CHUNK, exception_on_overflow=False)
            
            # 2. Process the audio chunk
            processed_chunk = await session.audio_processor.process_chunk(audio_data)
            
            # 3. Send the processed audio chunk directly as bytes
            if processed_chunk and session.ws:
                await session.ws.send_bytes(processed_chunk)

            await asyncio.sleep(0.01)

    except KeyboardInterrupt:
        print("\nEnding session...")

    except Exception as e:
        print(f"Error: {e}")

    finally:
        # Cancel response handler
        response_task.cancel()
        try:
            await response_task
        except asyncio.CancelledError:
            pass

        # Cleanup audio resources
        stream.stop_stream()
        stream.close()
        p.terminate()

        # Close WebSocket connection
        if session.ws:
            await session.ws.close()

if __name__ == "__main__":
    asyncio.run(main()) 
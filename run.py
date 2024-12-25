#!/usr/bin/env python3

import asyncio
import argparse
import pyaudio
import json
from pathlib import Path
from dotenv import load_dotenv

from src.core.realtime.session import RealtimeSession
from examples.language_assessment import language_assessment_config
from examples.restaurant_ordering import restaurant_ordering_config
from examples.financial_advisor import financial_advisor_config


# Map of available conversation configs
CONVERSATION_CONFIGS = {
    "language": language_assessment_config,
    "restaurant": restaurant_ordering_config,
    "financial": financial_advisor_config
}


async def handle_responses(session: RealtimeSession):
    """
    Handle incoming responses from the AI in a background task
    """
    try:
        while True:
            if session.ws:
                response = await session.ws.recv()
                if isinstance(response, str):
                    try:
                        data = json.loads(response)
                        await session.event_handler.handle_event(data)
                    except json.JSONDecodeError:
                        print(f"[error] Failed to parse response: {response}")
                else:
                    # Handle binary audio data
                    # You might want to play this through speakers
                    pass
            await asyncio.sleep(0.01)
    except Exception as e:
        print(f"[error] Response handler error: {e}")


async def run_conversation(config_name: str):
    """
    Run a conversation using the specified configuration
    """
    # Load environment variables
    load_dotenv()
    
    # Get the requested configuration
    config = CONVERSATION_CONFIGS.get(config_name)
    if not config:
        print(f"Error: Unknown configuration '{config_name}'")
        return
    
    # Initialize session
    print(f"Initializing {config.name}...")
    session = RealtimeSession(config)
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

    print(f"\nStarting {config.name}")
    print("Recording from microphone... Press Ctrl+C to stop.")

    # Start response handler in the background
    response_task = asyncio.create_task(handle_responses(session))

    try:
        while True:
            # 1. Capture audio from the microphone
            audio_data = stream.read(CHUNK, exception_on_overflow=False)
            
            # 2. Process the audio chunk
            processed_chunk = await session.audio_processor.process_chunk(audio_data)
            
            # 3. Send the processed audio chunk
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
        
        # Print final status
        status = session.observation_tracker.get_completion_status()
        print("\nSession Summary:")
        print(f"Duration: {status['duration_seconds']:.1f} seconds")
        print(f"Phases completed: {status['phases_completed']}")
        print(f"Total observations: {status['total_observations']}")


def main():
    parser = argparse.ArgumentParser(description="Run a guided conversation")
    parser.add_argument(
        "config",
        choices=list(CONVERSATION_CONFIGS.keys()),
        help="The conversation configuration to use"
    )
    args = parser.parse_args()
    
    asyncio.run(run_conversation(args.config))


if __name__ == "__main__":
    main() 
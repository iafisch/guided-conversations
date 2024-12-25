# Guided Conversation Framework

A framework for building multi-phase, AI-guided conversations powered by OpenAI’s Realtime API.  
This project provides:

• A declarative configuration system for conversation phases and success criteria  
• AI-driven conversation flow with real-time audio and text  
• Built-in progress tracking, phase management, and observations  
• Extensible tool system for smooth integration with the OpenAI Realtime API  

--------------------------------------------------------------------------------

## Features

1. **Declarative Conversation Structure**  
   Define reusable conversation phases with instructions, success criteria, required observations, and more.

2. **AI-Guided Flow**  
   The AI can guide users between phases, ensuring the conversation meets defined goals.

3. **Real-Time Audio**  
   Bi-directional audio streaming via WebSockets, enabling spoken conversations in real time.

4. **Progress Tracking**  
   Track observations, success criteria, and conversation completeness.

5. **Multi-Phase Management**  
   Jump between phases with clear rules and transitions.

6. **Extensible Tool System**  
   Easily add new actions or “tools” for function-calling scenarios.


--------------------------------------------------------------------------------

## Quickstart

1. **Clone the Repository**  
   » git clone https://github.com/your-organization/guided-conversations.git

2. **Install Dependencies**  
   » cd guided-conversations  
   » pip install -e .  
   or  
   » poetry install  
   (Adjust according to your environment.)

3. **Set up Environment Variables**  
   Make sure your OpenAI API key is configured properly, for example:  
   » export OPENAI_API_KEY="YOUR_OPENAI_API_KEY"

4. **Run the FastAPI Application**  
   » poetry run uvicorn src.api.main:app --reload  
   Access the application at http://127.0.0.1:8000

--------------------------------------------------------------------------------

## Usage

1. **Create a Conversation Session**  
   POST /conversations  
   Body: JSON representation of a ConversationConfig (refer to examples).

2. **Connect via WebSocket**  
   Once you have your session_id, connect to:  
   » /realtime/{session_id}  
   Send audio chunks (PCM16 at 24 kHz) in real time. The framework can process them and relay them to OpenAI’s Realtime API.

3. **Integrate Additional Tools or Logic**  
   • Customize conversation phases and success criteria.  
   • Extend the event handlers in “events.py” to store partial transcripts, handle function calls, or manipulate the conversation.  
   • Use the ObservationTracker to manage important notes or user data.

--------------------------------------------------------------------------------

## Configuration Examples

- [Language Assessment](examples/language_assessment.py)  
- [Restaurant Ordering](examples/restaurant_ordering.py)  
- [Financial Advisor](examples/financial_advisor.py)  

Each demonstrates a unique conversation goal, initial phase, and multi-phase flow.

--------------------------------------------------------------------------------

## Testing

• Run all tests with:  
  » pytest  

• Unit tests cover:  
  - Configuration validation  
  - Phase transitions  
  - Event handling  
  - Audio processing  

• Integration tests:  
  - Full conversation flow  
  - WebSocket interactions  
  - Audio streaming  

--------------------------------------------------------------------------------

## Deployment Considerations

1. **Production Environment**  
   - Use a robust server setup (e.g., behind Nginx or a load balancer).  
   - Configure TLS for secure WebSocket connections.

2. **Horizontal Scaling**  
   - Use Redis or another shared store for session data if multiple server instances handle WebSockets.

3. **Monitoring and Logging**  
   - Track conversation lengths, audio quality, errors, and success criteria to continuously refine user experience.

--------------------------------------------------------------------------------

## Security

• Token-based authentication can be added per the specification in “src/api/middleware/auth.py.”  
• Handle audio data carefully. If storing audio, ensure it is protected and meets compliance standards.  
• Validate user inputs to protect against injection attacks or malformed data.

--------------------------------------------------------------------------------

## Contributing

1. Fork the Repository  
2. Create a Feature Branch  
3. Commit your Changes  
4. Open a Pull Request  

Contributions are welcome! Feel free to submit issues, feature requests, or pull requests.

--------------------------------------------------------------------------------

## License

Include your open source license details here, for example:

[MIT License](LICENSE)

--------------------------------------------------------------------------------

## Contact

For questions or feedback, please open a GitHub issue or contact the maintainers at:
• you@example.com

--------------------------------------------------------------------------------

Happy building with the Guided Conversation Framework!

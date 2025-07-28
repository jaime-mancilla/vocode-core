from fastapi import FastAPI, Request
from fastapi.responses import PlainTextResponse
import os

from vocode.streaming.telephony.server.twilio import TwilioInboundCallServer
from vocode.streaming.models.transcriber import DeepgramTranscriberConfig
from vocode.streaming.models.synthesizer import ElevenLabsSynthesizerConfig
from vocode.streaming.models.agent import ChatGPTAgentConfig

app = FastAPI()

# Twilio + AI Call Handler
telephony_server = TwilioInboundCallServer(
    agent_config=ChatGPTAgentConfig(
        initial_message="Thanks for calling Horizon Road Rescue. How can I help you today?",
        prompt_preamble="You are a helpful, professional dispatcher for Horizon Road Rescue, a premium towing service in Nashville.",
        model=os.environ.get("LLM_MODEL", "gpt-3.5-turbo"),
    ),
    transcriber_config=DeepgramTranscriberConfig.from_telephone_input(),
    synthesizer_config=ElevenLabsSynthesizerConfig.from_telephone_output(
        voice_id=os.environ["VOICE_ID"]
    ),
    twilio_account_sid=os.environ["TWILIO_ACCOUNT_SID"],
    twilio_auth_token=os.environ["TWILIO_AUTH_TOKEN"],
    twilio_phone_number=os.environ["TWILIO_PHONE_NUMBER"],
)

@app.post("/voice", response_class=PlainTextResponse)
async def voice(request: Request):
    return await telephony_server.handle_call(request)

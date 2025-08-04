import asyncio
import hashlib
from typing import Optional

from elevenlabs import Voice, VoiceSettings
from elevenlabs.client import AsyncElevenLabs
from loguru import logger

from vocode.streaming.models.audio import AudioEncoding, SamplingRate
from vocode.streaming.models.message import BaseMessage
from vocode.streaming.models.synthesizer import ElevenLabsSynthesizerConfig
from vocode.streaming.synthesizer.base_synthesizer import BaseSynthesizer, SynthesisResult
from vocode.streaming.utils.create_task import asyncio_create_task

ELEVEN_LABS_BASE_URL = "https://api.elevenlabs.io/v1/"
STREAMED_CHUNK_SIZE = 16000 * 2 // 4  # 1/8 second of 16kHz audio with 16-bit samples

class ElevenLabsException(Exception):
    pass

class ElevenLabsSynthesizer(BaseSynthesizer[ElevenLabsSynthesizerConfig]):
    def __init__(self, synthesizer_config: ElevenLabsSynthesizerConfig):
        super().__init__(synthesizer_config)
        self.client = AsyncElevenLabs(api_key=self.synthesizer_config.api_key)

    def get_voice_identifier(self, message: BaseMessage) -> str:
        return self.synthesizer_config.voice_id or hashlib.sha256(
            message.sender.name.encode()
        ).hexdigest()

    async def create_speech_uncached(self, message: BaseMessage) -> SynthesisResult:
        voice_id = self.get_voice_identifier(message)
        audio = await self.client.text_to_speech(
            voice_id,
            message.text,
            voice=Voice(
                voice_id=voice_id,
                settings=VoiceSettings(
                    stability=self.synthesizer_config.stability,
                    similarity_boost=self.synthesizer_config.similarity_boost,
                    style=self.synthesizer_config.style,
                    use_speaker_boost=self.synthesizer_config.use_speaker_boost,
                )
            ),
            model_id=self.synthesizer_config.model_id,
        )
        return SynthesisResult(audio=audio, is_cached=False)

    async def get_chunks(
        self,
        message: BaseMessage,
        chunk_size: int,
        chunk_queue: asyncio.Queue[Optional[bytes]],
    ):
        voice_id = self.get_voice_identifier(message)

        try:
            async for chunk in self.client.text_to_speech_stream(
                voice_id,
                message.text,
                voice=Voice(
                    voice_id=voice_id,
                    settings=VoiceSettings(
                        stability=self.synthesizer_config.stability,
                        similarity_boost=self.synthesizer_config.similarity_boost,
                        style=self.synthesizer_config.style,
                        use_speaker_boost=self.synthesizer_config.use_speaker_boost,
                    ),
                ),
                model_id=self.synthesizer_config.model_id,
            ):
                await chunk_queue.put(chunk)

        except Exception as e:
            logger.exception("Streaming failed")
            raise ElevenLabsException(f"Failed to stream TTS audio: {str(e)}")

        await chunk_queue.put(None)

import os
from typing import TYPE_CHECKING, Iterable, List, Optional, Tuple

import aiohttp
import openai

if TYPE_CHECKING:
    from langchain.docstore.document import Document

DEFAULT_OPENAI_EMBEDDING_MODEL = "text-embedding-ada-002"


class VectorDB:
    def __init__(
        self,
        aiohttp_session: Optional[aiohttp.ClientSession] = None,
    ):
        if aiohttp_session:
            self.aiohttp_session = aiohttp_session
            self.should_close_session_on_tear_down = False
        else:
            self.aiohttp_session = aiohttp.ClientSession()
            self.should_close_session_on_tear_down = True

        self.engine = os.getenv("AZURE_OPENAI_TEXT_EMBEDDING_ENGINE")
        self.api_key = os.getenv("AZURE_OPENAI_API_KEY_EAST_US") if self.engine else os.getenv("OPENAI_API_KEY")
        openai.api_key = self.api_key
        if self.engine:
            openai.api_base = os.getenv("AZURE_OPENAI_API_BASE_EAST_US")
            openai.api_type = "azure"
            openai.api_version = os.getenv("AZURE_OPENAI_API_VERSION", "2023-05-15")

    def create_openai_embedding(
        self, text, model=DEFAULT_OPENAI_EMBEDDING_MODEL
    ) -> List[float]:
        response = openai.Embedding.create(
            input=text,
            model=self.engine if self.engine else model,
        )
        return response["data"][0]["embedding"]

    async def add_texts(
        self,
        texts: Iterable[str],
        metadatas: Optional[List[dict]] = None,
        ids: Optional[List[str]] = None,
        namespace: Optional[str] = None,
    ) -> List[str]:
        raise NotImplementedError

    async def similarity_search_with_score(
        self,
        query: str,
        filter: Optional[dict] = None,
        namespace: Optional[str] = None,
    ) -> List[Tuple["Document", float]]:
        raise NotImplementedError

    async def tear_down(self):
        if self.should_close_session_on_tear_down:
            await self.aiohttp_session.close()

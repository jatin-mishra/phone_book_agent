
from abc import ABC, abstractmethod
from message import MessageContext

class LLMProvider(ABC):

    @abstractmethod
    async def message(self, req: MessageContext):
        pass
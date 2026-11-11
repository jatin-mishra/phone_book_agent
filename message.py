from dataclasses import dataclass, field
from typing import Optional

@dataclass
class Message:
    content: str 
    id: Optional[str] = None
    type: Optional[str] = None 

@dataclass
class MessageContext:
    message: Message
    tools: list[dict] = field(default_factory=list)
    model: Optional[str] = None 
    max_tokens: Optional[int] = None 
    system_prompt: Optional[str] = None 
    structured_schema: Optional[dict] = None 


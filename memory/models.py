from dataclasses import dataclass
from typing import Optional

@dataclass
class ConversationModel:
    id: Optional[int]
    timestamp: str
    user_message: str
    assistant_reply: str
    provider: str

@dataclass
class PreferenceModel:
    id: Optional[int]
    key: str
    value: str

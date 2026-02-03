from dataclasses import dataclass
from typing import List, Literal

Role = Literal["system", "user", "assistant"]

@dataclass
class Message:
    role: Role
    content: str

class ChatMemory:
    def __init__(self, max_turns: int = 10):
        self.max_turns = max_turns
        self.messages: List[Message] = []

    def add(self, role: Role, content: str):
        self.messages.append(Message(role=role, content=content))
        # keep last N turns (user+assistant)
        if len(self.messages) > self.max_turns * 2 + 1:
            self.messages = self.messages[-(self.max_turns * 2 + 1):]

    def as_text(self) -> str:
        return "\n".join([f"{m.role.upper()}: {m.content}" for m in self.messages])

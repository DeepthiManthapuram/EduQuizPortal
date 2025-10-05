from dataclasses import dataclass
from typing import Optional
from datetime import datetime

@dataclass
class User:
    user_id: Optional[int]
    username: str
    email: str
    password: str
    role: str
    created_at: Optional[datetime] = None

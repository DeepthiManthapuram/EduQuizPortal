from dataclasses import dataclass
from typing import Optional

@dataclass
class Question:
    question_id: Optional[int]
    subject_id: int
    question_text: str
    option_a: str
    option_b: str
    option_c: str
    option_d: str
    correct_option: str
    created_by: Optional[int] = None

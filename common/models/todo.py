from rococo.models import VersionedModel
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

@dataclass
class Todo(VersionedModel):
    person_id: str = field(default='')
    title: str = field(default='')
    priority: int = field(default=0) # 0 = low, 1 = medium, 2 = high
    is_completed: bool = field(default=False)
    description: Optional[str] = field(default=None)
    completed_at: Optional[datetime] = field(default=None)
    due_date: Optional[datetime] = field(default=None)

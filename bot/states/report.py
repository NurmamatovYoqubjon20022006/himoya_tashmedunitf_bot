"""FSM holatlari — anonim murojaat oqimi."""
from __future__ import annotations

from aiogram.fsm.state import State, StatesGroup


class ReportSG(StatesGroup):
    """3 bosqichli murojaat oqimi."""
    incident_type = State()   # [1/3]
    description = State()      # [2/3]
    confirm = State()          # [3/3]


class StatusSG(StatesGroup):
    waiting_id = State()

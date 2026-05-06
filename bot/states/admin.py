"""Admin panel FSM."""
from __future__ import annotations

from aiogram.fsm.state import State, StatesGroup


class AdminSG(StatesGroup):
    waiting_note = State()
    waiting_search = State()
    waiting_broadcast = State()

"""Registratsiya FSM."""
from __future__ import annotations

from aiogram.fsm.state import State, StatesGroup


class RegistrationSG(StatesGroup):
    waiting_phone = State()
    waiting_full_name = State()
    waiting_user_type = State()
    waiting_faculty = State()
    waiting_course = State()
    waiting_direction = State()
    waiting_group = State()
    waiting_position = State()
    waiting_confirm = State()


class ProfileSG(StatesGroup):
    """Profilni tahrirlash."""
    editing_field = State()
    editing_value = State()

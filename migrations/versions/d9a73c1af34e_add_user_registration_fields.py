"""add user registration fields

Revision ID: d9a73c1af34e
Revises: a91724669a76
Create Date: 2026-05-06 10:30:37.626095

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'd9a73c1af34e'
down_revision: Union[str, Sequence[str], None] = 'a91724669a76'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Foydalanuvchi registratsiyasi uchun yangi maydonlarni qo'shish."""
    user_type_enum = sa.Enum(
        'STUDENT', 'MASTER', 'TEACHER', 'STAFF', 'OTHER',
        name='UserType',
    )
    faculty_enum = sa.Enum(
        'DAVOLASH_1', 'DAVOLASH_2', 'PEDIATRIYA', 'XALQARO',
        name='Faculty',
    )
    user_type_enum.create(op.get_bind(), checkfirst=True)
    faculty_enum.create(op.get_bind(), checkfirst=True)

    op.add_column('users', sa.Column('phone', sa.String(length=20), nullable=True))
    op.add_column('users', sa.Column('user_type', user_type_enum, nullable=True))
    op.add_column('users', sa.Column('faculty', faculty_enum, nullable=True))
    op.add_column('users', sa.Column('course', sa.Integer(), nullable=True))
    op.add_column('users', sa.Column('direction', sa.String(length=255), nullable=True))
    op.add_column('users', sa.Column('group_name', sa.String(length=64), nullable=True))
    op.add_column('users', sa.Column('position', sa.String(length=255), nullable=True))
    op.add_column(
        'users',
        sa.Column('is_registered', sa.Boolean(), nullable=False, server_default=sa.false()),
    )
    op.add_column('users', sa.Column('registered_at', sa.DateTime(timezone=True), nullable=True))

    op.create_index(op.f('ix_users_phone'), 'users', ['phone'], unique=True)


def downgrade() -> None:
    """Maydonlarni olib tashlash."""
    op.drop_index(op.f('ix_users_phone'), table_name='users')
    op.drop_column('users', 'registered_at')
    op.drop_column('users', 'is_registered')
    op.drop_column('users', 'position')
    op.drop_column('users', 'group_name')
    op.drop_column('users', 'direction')
    op.drop_column('users', 'course')
    op.drop_column('users', 'faculty')
    op.drop_column('users', 'user_type')
    op.drop_column('users', 'phone')

    sa.Enum(name='Faculty').drop(op.get_bind(), checkfirst=True)
    sa.Enum(name='UserType').drop(op.get_bind(), checkfirst=True)

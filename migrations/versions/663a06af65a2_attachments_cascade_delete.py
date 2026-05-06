"""attachments cascade delete

Revision ID: 663a06af65a2
Revises: d9a73c1af34e
Create Date: 2026-05-06 10:45:14.655995

"""
from typing import Sequence, Union

from alembic import op


revision: str = '663a06af65a2'
down_revision: Union[str, Sequence[str], None] = 'd9a73c1af34e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """attachments.report_id FK ni ON DELETE CASCADE bilan qayta yaratish."""
    op.drop_constraint('attachments_report_id_fkey', 'attachments', type_='foreignkey')
    op.create_foreign_key(
        'attachments_report_id_fkey',
        'attachments',
        'reports',
        ['report_id'],
        ['id'],
        ondelete='CASCADE',
    )


def downgrade() -> None:
    op.drop_constraint('attachments_report_id_fkey', 'attachments', type_='foreignkey')
    op.create_foreign_key(
        'attachments_report_id_fkey',
        'attachments',
        'reports',
        ['report_id'],
        ['id'],
    )

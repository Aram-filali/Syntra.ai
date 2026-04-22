"""merge_heads

Revision ID: e0b8b7fc0043
Revises: create_users_table, 869e4dc6a980
Create Date: 2026-01-21 23:26:31.452501

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e0b8b7fc0043'
down_revision: Union[str, Sequence[str], None] = ('create_users_table', '869e4dc6a980')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass

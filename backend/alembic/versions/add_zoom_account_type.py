"""Add zoom_account_type to User model

Revision ID: add_zoom_account_type
Revises: 
Create Date: 2026-04-18 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_zoom_account_type'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add zoom_account_type column to users table
    op.add_column('users', sa.Column('zoom_account_type', sa.String(), nullable=True, server_default='basic'))


def downgrade() -> None:
    # Remove zoom_account_type column from users table
    op.drop_column('users', 'zoom_account_type')

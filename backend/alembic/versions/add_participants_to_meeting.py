"""Add participants field to Meeting model

Revision ID: add_participants_to_meeting
Revises: 
Create Date: 2026-04-18 13:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_participants_to_meeting'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add participants column to meetings table
    op.add_column('meetings', sa.Column('participants', sa.JSON(), nullable=True, server_default='[]'))


def downgrade() -> None:
    # Remove participants column from meetings table
    op.drop_column('meetings', 'participants')

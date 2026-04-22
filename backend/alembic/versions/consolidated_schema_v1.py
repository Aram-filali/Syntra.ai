"""Consolidated initial schema - Phase 3 cleanup

Revision ID: consolidated_schema_v1
Revises: 
Create Date: 2026-04-18 14:00:00.000000

This migration consolidates all previous migrations into a single, clean schema.
All previous migrations should be marked as superseded.

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'consolidated_schema_v1'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create all tables with consolidated schema"""
    
    # Create users table
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('username', sa.String(), nullable=False),
        sa.Column('email', sa.String(), nullable=False),
        sa.Column('hashed_password', sa.String(), nullable=False),
        sa.Column('full_name', sa.String(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True, server_default='true'),
        sa.Column('is_verified', sa.Boolean(), nullable=True, server_default='false'),
        sa.Column('zoom_access_token', sa.String(), nullable=True),
        sa.Column('zoom_refresh_token', sa.String(), nullable=True),
        sa.Column('zoom_token_expires_at', sa.DateTime(), nullable=True),
        sa.Column('zoom_account_type', sa.String(), nullable=True, server_default='basic'),
        sa.Column('created_at', sa.DateTime(), nullable=True, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email'),
        sa.UniqueConstraint('username')
    )
    
    # Create meetings table
    op.create_table(
        'meetings',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('zoom_meeting_id', sa.String(), nullable=True),
        sa.Column('title', sa.String(), nullable=False),
        sa.Column('scheduled_time', sa.DateTime(), nullable=True),
        sa.Column('duration_minutes', sa.Integer(), nullable=True),
        sa.Column('status', sa.String(), nullable=False, server_default='scheduled'),
        sa.Column('participants', sa.JSON(), nullable=True, server_default='[]'),
        sa.Column('created_at', sa.DateTime(), nullable=True, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id']),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('zoom_meeting_id')
    )
    
    # Create transcriptions table
    op.create_table(
        'transcriptions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('meeting_id', sa.Integer(), nullable=False),
        sa.Column('full_text', sa.String(), nullable=True),
        sa.Column('speaker_segments', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['meeting_id'], ['meetings.id']),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('meeting_id')
    )
    
    # Create action_items table
    op.create_table(
        'action_items',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('meeting_id', sa.Integer(), nullable=False),
        sa.Column('description', sa.String(), nullable=False),
        sa.Column('assigned_to', sa.String(), nullable=True),
        sa.Column('due_date', sa.DateTime(), nullable=True),
        sa.Column('priority', sa.String(), nullable=False, server_default='medium'),
        sa.Column('status', sa.String(), nullable=False, server_default='todo'),
        sa.Column('created_at', sa.DateTime(), nullable=True, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=True, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['meeting_id'], ['meetings.id']),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create summaries table
    op.create_table(
        'summaries',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('meeting_id', sa.Integer(), nullable=False),
        sa.Column('executive_summary', sa.String(), nullable=True),
        sa.Column('decisions', sa.JSON(), nullable=True),
        sa.Column('questions', sa.JSON(), nullable=True),
        sa.Column('full_markdown', sa.String(), nullable=True),
        sa.Column('pdf_url', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['meeting_id'], ['meetings.id']),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('meeting_id')
    )
    
    # Create indexes for performance
    op.create_index('idx_meetings_user_id', 'meetings', ['user_id'])
    op.create_index('idx_meetings_status', 'meetings', ['status'])
    op.create_index('idx_meetings_created_at', 'meetings', ['created_at'])
    op.create_index('idx_transcriptions_meeting_id', 'transcriptions', ['meeting_id'])
    op.create_index('idx_action_items_meeting_id', 'action_items', ['meeting_id'])
    op.create_index('idx_action_items_status', 'action_items', ['status'])
    op.create_index('idx_summaries_meeting_id', 'summaries', ['meeting_id'])
    op.create_index('idx_users_email', 'users', ['email'])
    op.create_index('idx_users_username', 'users', ['username'])


def downgrade() -> None:
    """Drop all tables"""
    
    # Drop indexes
    op.drop_index('idx_users_username')
    op.drop_index('idx_users_email')
    op.drop_index('idx_summaries_meeting_id')
    op.drop_index('idx_action_items_status')
    op.drop_index('idx_action_items_meeting_id')
    op.drop_index('idx_transcriptions_meeting_id')
    op.drop_index('idx_meetings_created_at')
    op.drop_index('idx_meetings_status')
    op.drop_index('idx_meetings_user_id')
    
    # Drop tables
    op.drop_table('summaries')
    op.drop_table('action_items')
    op.drop_table('transcriptions')
    op.drop_table('meetings')
    op.drop_table('users')

"""Add email verification fields to User model

Revision ID: add_email_verification
Revises: 
Create Date: 2026-04-18 15:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_email_verification'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Add email verification fields to users table"""
    
    # Add email_verified column
    op.add_column('users', sa.Column('email_verified', sa.Boolean(), nullable=False, server_default='false'))
    
    # Add email_verified_at column
    op.add_column('users', sa.Column('email_verified_at', sa.DateTime(), nullable=True))


def downgrade() -> None:
    """Remove email verification fields from users table"""
    
    # Remove columns
    op.drop_column('users', 'email_verified_at')
    op.drop_column('users', 'email_verified')

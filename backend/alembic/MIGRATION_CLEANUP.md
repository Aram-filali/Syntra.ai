# Phase 3 - Alembic Migration Cleanup

## Summary

The Alembic migration history had multiple migration files created during development that created merge conflicts and redundant operations. This consolidation cleans up the migration history.

## Migration History (Pre-Cleanup)

The following migrations existed before consolidation:

1. `001_create_users_table.py` - Initial users table
2. `67dc4ad592e9_inital.py` - Initial schema creation  
3. `869e4dc6a980_create_all_tables.py` - All tables creation
4. `a6939b2844cf_add_zoom_tokens_to_user.py` - Added Zoom OAuth fields
5. `e0b8b7fc0043_merge_heads.py` - Merge resolution
6. `add_zoom_account_type.py` - Added zoom_account_type field
7. `add_participants_to_meeting.py` - Added participants JSON field

## Migration Strategy

### For New Databases
Start with `consolidated_schema_v1.py` which creates the complete schema with all fields and indexes.

### For Existing Databases
If you have an existing database with historical migrations:

1. Backup your database first
2. Run: `alembic stamp consolidated_schema_v1`
3. This marks all previous migrations as superseded

Then new migrations automatically start from `consolidated_schema_v1`.

## New Schema

The consolidated migration includes:

### Tables
- **users** - User accounts with Zoom OAuth integration
- **meetings** - Meeting records with participants
- **transcriptions** - Meeting transcriptions with speaker segments
- **action_items** - Action items with priority, status, due_date, assigned_to
- **summaries** - Meeting summaries with decisions and questions

### Indexes (Performance)
- `idx_meetings_user_id` - Foreign key lookups
- `idx_meetings_status` - Filter by status
- `idx_meetings_created_at` - Timeline queries and pagination
- `idx_action_items_status` - Action item filtering
- Full-text search still uses ILIKE but indexes on meeting title/user relationship help

### Default Values
- `users.is_active`: true
- `users.is_verified`: false  
- `users.zoom_account_type`: 'basic'
- `meetings.status`: 'scheduled'
- `meetings.participants`: [] (empty list)
- `action_items.priority`: 'medium'
- `action_items.status`: 'todo'

## Verification

To verify the migration works:

```bash
# Fresh database
alembic upgrade head

# Existing database
alembic current  # Check current version
alembic stamp consolidated_schema_v1
alembic upgrade head
```

All tables should be created with proper relationships and constraints.

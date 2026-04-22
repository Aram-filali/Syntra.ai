# Phase 3 - Database Optimization Guide

## Overview

This document outlines database optimizations implemented in Phase 3:
1. Strategic indexes for common queries
2. Lazy-loading relationship configuration
3. Query optimization patterns
4. Pagination strategy

## Indexes Created

### User Indexes
- `idx_users_email` - Fast email lookups for authentication
- `idx_users_username` - Fast username lookups

### Meeting Indexes
- `idx_meetings_user_id` - Filter meetings by user (foreign key)
- `idx_meetings_status` - Filter meetings by status (scheduled/in_progress/completed)
- `idx_meetings_created_at` - Sort and pagination by creation date

### Action Item Indexes
- `idx_action_items_meeting_id` - Fetch actions for a specific meeting
- `idx_action_items_status` - Filter actions by status (todo/in_progress/completed)

### Transcription Indexes
- `idx_transcriptions_meeting_id` - One-to-one lookup

### Summary Indexes
- `idx_summaries_meeting_id` - One-to-one lookup

## Query Optimization Patterns

### Pattern 1: Paginated Meeting List
```python
# Efficient: Uses index on user_id and created_at
meetings = db.query(Meeting)\
    .filter(Meeting.user_id == user_id)\
    .order_by(Meeting.created_at.desc())\
    .offset(skip)\
    .limit(limit)\
    .all()
```

### Pattern 2: Search with Full-Text
```python
# Uses ILIKE but benefits from index on user_id
results = db.query(Meeting)\
    .filter(Meeting.user_id == user_id)\
    .filter(Meeting.title.ilike(f"%{query}%"))\
    .all()
```

### Pattern 3: Action Items with Filtering
```python
# Uses indexes on meeting_id and status
actions = db.query(ActionItem)\
    .filter(ActionItem.meeting_id == meeting_id)\
    .filter(ActionItem.status == 'todo')\
    .all()
```

## Lazy-Loading Configuration

### Current ORM Relationships (SQLAlchemy)

**Meeting Model**
```python
user = relationship("User", back_populates="meetings")  # Lazy loading
transcription = relationship("Transcription", ..., uselist=False, cascade="all, delete-orphan")
action_items = relationship("ActionItem", ..., cascade="all, delete-orphan")
summary = relationship("Summary", ..., uselist=False, cascade="all, delete-orphan")
```

**Recommendation for API:**
```python
# For list endpoints - lazy load relations
meetings = db.query(Meeting).filter(...).all()

# For detail endpoints - eager load when needed
from sqlalchemy.orm import joinedload
meeting = db.query(Meeting)\
    .options(
        joinedload(Meeting.transcription),
        joinedload(Meeting.action_items),
        joinedload(Meeting.summary)
    )\
    .filter(Meeting.id == meeting_id)\
    .first()
```

## Pagination Implementation

### Backend (FastAPI)
All list endpoints should support pagination:

```python
@router.get("/meetings")
def get_meetings(
    skip: int = 0,
    limit: int = 20,  # Default page size
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    meetings = db.query(Meeting)\
        .filter(Meeting.user_id == current_user.id)\
        .order_by(Meeting.created_at.desc())\
        .offset(skip)\
        .limit(limit)\
        .all()
    
    total = db.query(Meeting)\
        .filter(Meeting.user_id == current_user.id)\
        .count()
    
    return {
        "items": meetings,
        "total": total,
        "skip": skip,
        "limit": limit
    }
```

### Frontend Implementation
```javascript
// Use offset-based pagination
const fetchMeetings = async (page = 0, pageSize = 20) => {
    const skip = page * pageSize;
    const response = await axios.get('/api/meetings', {
        params: { skip, limit: pageSize }
    });
    return response.data;
};

// Or cursor-based pagination (more efficient)
const fetchMoreMeetings = async (lastId) => {
    const response = await axios.get('/api/meetings', {
        params: { after_id: lastId, limit: 20 }
    });
    return response.data;
};
```

## Search Optimization

### Current Implementation
Full-text search uses ILIKE across multiple fields:
```python
query = query.filter(
    or_(
        Meeting.title.ilike(f"%{q}%"),
        Meeting.transcription.full_text.ilike(f"%{q}%"),
        Meeting.summary.executive_summary.ilike(f"%{q}%"),
        Meeting.action_items.description.ilike(f"%{q}%")
    )
)
```

### Recommendation for Future
Consider PostgreSQL Full-Text Search for better performance:
```python
# With PostgreSQL tsvector triggers
from sqlalchemy import func, cast, Text
query = query.filter(
    Meeting.search_vector.match(q)  # Uses GiST index
)
```

## Database Connection Pooling

Current settings in `base.py`:
- Pool size: 20 (default)
- Max overflow: 10
- Pool recycle: 3600 (1 hour)

For production, adjust based on:
- Number of concurrent users
- Average request duration
- Available database connections

```python
engine = create_engine(
    DATABASE_URL,
    pool_size=30,        # Increase for high load
    max_overflow=20,
    pool_recycle=3600,   # Recycle connections hourly
    echo=False           # Set True for query debugging
)
```

## Query Monitoring

To identify slow queries:

```python
# In development, enable SQL echo
engine = create_engine(DATABASE_URL, echo=True)

# In production, use logging
import logging
logging.basicConfig()
logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)
```

## Performance Benchmarks

Target metrics after optimization:

| Operation | Target Time |
|-----------|------------|
| Get user by email | < 10ms |
| List meetings (20 items) | < 50ms |
| Get meeting detail with all relations | < 100ms |
| Search meetings (full-text) | < 200ms |
| Create meeting | < 50ms |
| Update action item | < 20ms |

## Monitoring Queries

Enable slow query logging in PostgreSQL:
```sql
-- In postgresql.conf or dynamically:
SET log_min_duration_statement = 100;  -- Log queries over 100ms
```

Monitor with:
```bash
# Connect to database
psql -U postgres meeting_intelligence

# Check slow queries
SELECT query, calls, mean_time FROM pg_stat_statements
ORDER BY mean_time DESC
LIMIT 10;
```

## Future Improvements

1. **Caching Layer** - Redis for frequently accessed data
2. **Denormalization** - Cache meeting stats on the meetings table
3. **Full-Text Search** - PostgreSQL tsvector with GiST indexes
4. **Read Replicas** - For read-heavy workloads
5. **Query Result Streaming** - For large exports

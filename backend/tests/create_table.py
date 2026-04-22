# backend/create_tables.py
from app.models.base import engine, Base
from app.models.meeting import User, Meeting, Transcription, ActionItem, Summary

def create_tables():
    print("Suppression des anciennes tables...")
    Base.metadata.drop_all(bind=engine)
    
    print("Creation des nouvelles tables...")
    Base.metadata.create_all(bind=engine)
    
    print("Tables creees avec succes!")
    print("\nTables créées:")
    print("  - users")
    print("  - meetings")
    print("  - transcriptions")
    print("  - action_items")
    print("  - summaries")

if __name__ == "__main__":
    create_tables()
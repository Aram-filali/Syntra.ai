# backend/test_full_flow.py
import requests
import json
from tests.mock_data.transcriptions import MOCK_TRANSCRIPTION_1

BASE_URL = "http://127.0.0.1:8000"

def test_full_flow():
    print("="*70)
    print("🧪 TEST COMPLET API - MEETING INTELLIGENCE")
    print("="*70)
    
    # 1. Créer meeting
    print("\n1️⃣ Création meeting...")
    meeting_data = {
        "title": "Réunion Planning MVP",
        "scheduled_time": "2025-01-15T10:00:00",
        "duration_minutes": 30,
        "zoom_meeting_id": "test_123"
    }
    response = requests.post(f"{BASE_URL}/api/meetings", json=meeting_data)
    print(f"   Status: {response.status_code}")
    meeting = response.json()
    meeting_id = meeting["id"]
    print(f"   ✅ Meeting créé: ID={meeting_id}")
    
    # 2. Ajouter transcription
    print("\n2️⃣ Ajout transcription...")
    transcription_data = {
        "full_text": MOCK_TRANSCRIPTION_1
    }
    response = requests.post(
        f"{BASE_URL}/api/meetings/{meeting_id}/transcription",
        json=transcription_data
    )
    print(f"   Status: {response.status_code}")
    print(f"   ✅ Transcription ajoutée ({len(MOCK_TRANSCRIPTION_1)} caractères)")
    
    # 3. Analyser avec AI
    print("\n3️⃣ Analyse AI (peut prendre 20-30 sec)...")
    response = requests.post(f"{BASE_URL}/api/meetings/{meeting_id}/analyze")
    print(f"   Status: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"   ✅ Analyse terminée!")
        print(f"      - Actions extraites: {result['actions_count']}")
        print(f"      - Décisions extraites: {result['decisions_count']}")
        print(f"      - Questions extraites: {result['questions_count']}")
    else:
        print(f"   ❌ Erreur: {response.text}")
        return
    
    # 4. Récupérer actions
    print("\n4️⃣ Récupération des actions...")
    response = requests.get(f"{BASE_URL}/api/meetings/{meeting_id}/actions")
    actions = response.json()
    print(f"   ✅ {len(actions)} actions récupérées:")
    for idx, action in enumerate(actions, 1):
        print(f"      {idx}. {action['description']}")
        print(f"         → Assigné: {action['assigned_to']}")
        print(f"         → Deadline: {action['deadline']}")
        print(f"         → Priorité: {action['priority']}")
    
    # 5. Récupérer summary
    print("\n5️⃣ Récupération du compte-rendu...")
    response = requests.get(f"{BASE_URL}/api/meetings/{meeting_id}/summary")
    summary = response.json()
    print("   ✅ Compte-rendu récupéré")
    
    print("\n" + "="*70)
    print("📄 COMPTE-RENDU COMPLET")
    print("="*70)
    print(summary["full_markdown"])
    print("="*70)
    
    # 6. Liste tous les meetings
    print("\n6️⃣ Liste de tous les meetings...")
    response = requests.get(f"{BASE_URL}/api/meetings")
    meetings = response.json()
    print(f"   ✅ {len(meetings)} meeting(s) dans la base:")
    for m in meetings:
        print(f"      - [{m['id']}] {m['title']} ({m['status']})")
    
    print("\n" + "="*70)
    print("✅ TEST COMPLET RÉUSSI!")
    print("="*70)

if __name__ == "__main__":
    test_full_flow()
import asyncio
import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from app.agents.orchestrator import MeetingIntelligenceOrchestrator
from tests.mock_data.transcriptions import MOCK_TRANSCRIPTION_1

load_dotenv()

async def main():
    print("="*60)
    print("🤖 TEST AVEC VRAI LLM (OpenAI)")
    print("="*60)
    
    llm = ChatOpenAI(
        model="gpt-4o-mini",  # ou un modèle supporté par OpenRouter
        temperature=0,
        openai_api_base="https://openrouter.ai/api/v1",
        api_key=os.getenv("OPENROUTER_API_KEY")
    )

    
    orchestrator = MeetingIntelligenceOrchestrator(llm)
    
    print("\n📝 Transcription:")
    print("-"*60)
    print(MOCK_TRANSCRIPTION_1[:200] + "...\n")
    
    print("⏳ Analyse en cours (15-30 sec)...\n")
    
    result = await orchestrator.process_meeting(
        transcription=MOCK_TRANSCRIPTION_1,
        metadata={
            "title": "Réunion MVP Planning",
            "duration": 3
        }
    )
    
    # Afficher résultats
    print("\n" + "="*60)
    print("📌 ACTION ITEMS")
    print("="*60)
    for item in result["actions"]["items"]:
        print(f"\n✅ {item['action']}")
        print(f"   → Assigné: {item['assigned_to']}")
        print(f"   → Deadline: {item['deadline']}")
        print(f"   → Priorité: {item['priority']}")
    
    print("\n" + "="*60)
    print("💡 DÉCISIONS")
    print("="*60)
    for item in result["decisions"]["items"]:
        print(f"\n✅ {item['decision']}")
        print(f"   → Raison: {item['reasoning']}")
    
    print("\n" + "="*60)
    print("❓ QUESTIONS EN SUSPENS")
    print("="*60)
    for item in result["questions"]["items"]:
        print(f"\n❓ {item['question']}")
        print(f"   → Posée par: {item['asked_by']}")
    
    print("\n" + "="*60)
    print("📄 COMPTE-RENDU COMPLET")
    print("="*60)
    print(result["summary"]["full_markdown"])
    
    print("\n" + "="*60)
    print("✅ TERMINÉ!")
    print("="*60)

if __name__ == "__main__":
    asyncio.run(main())
import asyncio
from app.agents.action_agent import ActionItemsAgent
from app.agents.decision_agent import DecisionsAgent
from app.agents.question_agent import QuestionsAgent
from app.agents.summary_agent import SummaryAgent
from tests.fakes.fake_llm import FakeLLM
from tests.mock_data.llm_responses import (
    ACTION_ITEMS_RESPONSE,
    DECISIONS_RESPONSE,
    QUESTIONS_RESPONSE,
    SUMMARY_RESPONSE
)
from tests.mock_data.transcriptions import MOCK_TRANSCRIPTION_1

async def main():
    print("="*60)
    print("🧪 TEST AGENTS AVEC FAKE LLM")
    print("="*60)
    
    # Test Action Agent
    print("\n📌 ACTION ITEMS:")
    print("-"*60)
    action_agent = ActionItemsAgent(FakeLLM(ACTION_ITEMS_RESPONSE))
    actions = await action_agent.extract(MOCK_TRANSCRIPTION_1)
    for item in actions["items"]:
        print(f"  ✅ {item['action']}")
        print(f"     → Assigné: {item['assigned_to']}")
        print(f"     → Deadline: {item['deadline']}")
        print(f"     → Priorité: {item['priority']}\n")
    
    # Test Decision Agent
    print("\n💡 DÉCISIONS:")
    print("-"*60)
    decision_agent = DecisionsAgent(FakeLLM(DECISIONS_RESPONSE))
    decisions = await decision_agent.extract(MOCK_TRANSCRIPTION_1)
    for item in decisions["items"]:
        print(f"  ✅ {item['decision']}")
        print(f"     → Raison: {item['reasoning']}\n")
    
    # Test Question Agent
    print("\n❓ QUESTIONS EN SUSPENS:")
    print("-"*60)
    question_agent = QuestionsAgent(FakeLLM(QUESTIONS_RESPONSE))
    questions = await question_agent.extract(MOCK_TRANSCRIPTION_1)
    for item in questions["items"]:
        print(f"  ❓ {item['question']}")
        print(f"     → Posée par: {item['asked_by']}\n")
    
    print("="*60)
    print("✅ TOUS LES AGENTS FONCTIONNENT!")
    print("="*60)

if __name__ == "__main__":
    asyncio.run(main())
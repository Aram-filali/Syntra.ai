import pytest
from app.agents.orchestrator import MeetingIntelligenceOrchestrator
from app.agents.action_agent import ActionItemsAgent
from app.agents.decision_agent import DecisionsAgent
from app.agents.question_agent import QuestionsAgent

from tests.mock_data.transcriptions import MOCK_TRANSCRIPTION_1
from tests.fakes.fake_llm import FakeLLM
from tests.mock_data.llm_responses import (
    ACTION_ITEMS_RESPONSE,
    DECISIONS_RESPONSE,
    QUESTIONS_RESPONSE,
    SUMMARY_RESPONSE
)


@pytest.mark.asyncio
async def test_action_agent():
    llm = FakeLLM(ACTION_ITEMS_RESPONSE)
    agent = ActionItemsAgent(llm)

    result = await agent.extract(MOCK_TRANSCRIPTION_1)

    assert "items" in result
    assert len(result["items"]) == 3
    assert result["items"][0]["assigned_to"] == "Marc"


@pytest.mark.asyncio
async def test_decision_agent():
    llm = FakeLLM(DECISIONS_RESPONSE)
    agent = DecisionsAgent(llm)

    result = await agent.extract(MOCK_TRANSCRIPTION_1)

    assert len(result["items"]) == 1
    assert result["items"][0]["decision"] == "Utiliser PostgreSQL comme base de données"


@pytest.mark.asyncio
async def test_question_agent():
    llm = FakeLLM(QUESTIONS_RESPONSE)
    agent = QuestionsAgent(llm)

    result = await agent.extract(MOCK_TRANSCRIPTION_1)

    assert len(result["items"]) == 1
    assert result["items"][0]["asked_by"] == "Speaker 3"


@pytest.mark.asyncio
async def test_full_orchestrator():
    llm = FakeLLM([
        ACTION_ITEMS_RESPONSE,
        DECISIONS_RESPONSE,
        QUESTIONS_RESPONSE,
        SUMMARY_RESPONSE
    ])

    orchestrator = MeetingIntelligenceOrchestrator(llm)

    result = await orchestrator.process_meeting(
        transcription=MOCK_TRANSCRIPTION_1,
        metadata={
            "title": "Réunion MVP Planning",
            "duration": 3
        }
    )

    assert "actions" in result
    assert "decisions" in result
    assert "questions" in result
    assert "summary" in result

    assert len(result["actions"]["items"]) >= 3
    assert len(result["decisions"]["items"]) >= 1
    assert result["summary"]["full_markdown"]

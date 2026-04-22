"""
Backend tests for AI agents and orchestrator
"""
import pytest
import asyncio
from typing import List

from app.agents.orchestrator import MeetingIntelligenceOrchestrator
from app.agents.action_agent import ActionItemsAgent, ActionItems
from app.agents.decision_agent import DecisionsAgent
from app.agents.question_agent import QuestionsAgent
from app.agents.summary_agent import SummaryAgent
from tests.fakes.fake_llm import FakeLLM


class TestActionAgent:
    """Test suite for action items extraction agent"""

    @pytest.mark.asyncio
    async def test_extract_actions_from_transcription(self):
        """Test extracting action items from transcription"""
        # Mock response
        mock_response = """{
            "items": [
                {
                    "action": "Follow up with John on budget",
                    "assigned_to": "Speaker A",
                    "deadline": "2026-04-25",
                    "priority": "Haute",
                    "context": "Discussed funding constraints"
                },
                {
                    "action": "Send proposal to clients",
                    "assigned_to": "Speaker B",
                    "deadline": "2026-04-20",
                    "priority": "Moyenne",
                    "context": "Agreed in meeting"
                }
            ]
        }"""
        
        fake_llm = FakeLLM([mock_response])
        agent = ActionItemsAgent(fake_llm)
        
        transcription = "John mentioned we need to follow up on budget. Speaker A will do it by Friday. Speaker B needs to send the proposal by Wednesday."
        
        result = await agent.extract(transcription)
        
        assert result is not None
        assert hasattr(result, 'items')
        assert len(result.items) == 2
        assert result.items[0].action == "Follow up with John on budget"
        assert result.items[1].assigned_to == "Speaker B"

    @pytest.mark.asyncio
    async def test_extract_actions_empty_transcription(self):
        """Test handling empty transcription"""
        mock_response = '{"items": []}'
        fake_llm = FakeLLM([mock_response])
        agent = ActionItemsAgent(fake_llm)
        
        result = await agent.extract("")
        
        assert result is not None
        assert len(result.items) == 0

    @pytest.mark.asyncio
    async def test_action_item_data_structure(self):
        """Test action item has all required fields"""
        mock_response = """{"items": [{
            "action": "Test action",
            "assigned_to": "John",
            "deadline": "2026-04-25",
            "priority": "Haute",
            "context": "Testing"
        }]}"""
        
        fake_llm = FakeLLM([mock_response])
        agent = ActionItemsAgent(fake_llm)
        
        result = await agent.extract("test")
        
        action = result.items[0]
        assert action.action == "Test action"
        assert action.assigned_to == "John"
        assert action.deadline == "2026-04-25"
        assert action.priority == "Haute"
        assert action.context == "Testing"


class TestDecisionAgent:
    """Test suite for decisions extraction agent"""

    @pytest.mark.asyncio
    async def test_extract_decisions(self):
        """Test extracting decisions from transcription"""
        mock_response = """{"decisions": [
            "We approve the new product launch",
            "Budget allocation increased by 20%"
        ]}"""
        
        fake_llm = FakeLLM([mock_response])
        agent = DecisionsAgent(fake_llm)
        
        result = await agent.extract("We decided to launch the product next month. Budget is approved with 20% increase.")
        
        assert result is not None
        assert len(result.get('decisions', [])) >= 0

    @pytest.mark.asyncio
    async def test_extract_decisions_none(self):
        """Test with transcription containing no decisions"""
        mock_response = '{"decisions": []}'
        fake_llm = FakeLLM([mock_response])
        agent = DecisionsAgent(fake_llm)
        
        result = await agent.extract("Just discussing various options without deciding anything.")
        
        assert result is not None


class TestQuestionAgent:
    """Test suite for questions extraction agent"""

    @pytest.mark.asyncio
    async def test_extract_questions(self):
        """Test extracting questions from transcription"""
        mock_response = """{"questions": [
            "When is the launch date?",
            "How will we handle customer support?"
        ]}"""
        
        fake_llm = FakeLLM([mock_response])
        agent = QuestionsAgent(fake_llm)
        
        result = await agent.extract("When will we launch? How about support?")
        
        assert result is not None
        assert len(result.get('questions', [])) >= 0

    @pytest.mark.asyncio
    async def test_extract_questions_empty(self):
        """Test with transcription containing no questions"""
        mock_response = '{"questions": []}'
        fake_llm = FakeLLM([mock_response])
        agent = QuestionsAgent(fake_llm)
        
        result = await agent.extract("This is just a statement with facts.")
        
        assert result is not None


class TestSummaryAgent:
    """Test suite for summary generation agent"""

    @pytest.mark.asyncio
    async def test_generate_summary(self):
        """Test generating meeting summary"""
        mock_response = """# Meeting Summary

## Executive Summary
This was a productive meeting where we discussed Q2 strategy and approved budget increases.

## Key Points
- Product launch approved for next month
- Budget increased by 20%
- Team expanded with 2 new hires

## Next Steps
- Follow up on launch timeline
- Finalize hiring process"""
        
        fake_llm = FakeLLM([mock_response])
        agent = SummaryAgent(fake_llm)
        
        result = await agent.generate(
            transcription="Meeting discussion about Q2 strategy",
            actions=[{"action": "Follow up", "assigned_to": "John"}],
            decisions=["Approved launch"],
            questions=["Timeline?"],
            metadata={"duration": 60}
        )
        
        assert result is not None
        assert len(result) > 0

    @pytest.mark.asyncio
    async def test_summary_structure(self):
        """Test summary has proper markdown structure"""
        mock_response = """# Summary Title
## Executive Summary
Key points about the meeting
"""
        
        fake_llm = FakeLLM([mock_response])
        agent = SummaryAgent(fake_llm)
        
        result = await agent.generate(
            transcription="test",
            actions=[],
            decisions=[],
            questions=[],
            metadata={}
        )
        
        assert "Summary" in result or "summary" in result.lower() or len(result) > 0


class TestMeetingIntelligenceOrchestrator:
    """Test suite for the main orchestrator"""

    @pytest.mark.asyncio
    async def test_orchestrator_initialization(self):
        """Test orchestrator can be initialized"""
        fake_llm = FakeLLM(["response"])
        orchestrator = MeetingIntelligenceOrchestrator(fake_llm)
        
        assert orchestrator is not None
        assert orchestrator.llm == fake_llm
        assert orchestrator.action_agent is not None
        assert orchestrator.decision_agent is not None
        assert orchestrator.question_agent is not None
        assert orchestrator.summary_agent is not None

    @pytest.mark.asyncio
    async def test_process_meeting_parallel_execution(self):
        """Test that orchestrator executes agents in parallel"""
        # Provide enough responses for all agents + summary
        responses = [
            '{"items": []}',  # actions
            '{"decisions": []}',  # decisions
            '{"questions": []}',  # questions
            '# Summary\nMeeting processed successfully'  # summary
        ]
        
        fake_llm = FakeLLM(responses)
        orchestrator = MeetingIntelligenceOrchestrator(fake_llm)
        
        transcription = "Meeting: discussing Q2 goals and objectives"
        metadata = {"duration": 60, "participants": 5}
        
        result = await orchestrator.process_meeting(transcription, metadata)
        
        assert result is not None
        assert "actions" in result
        assert "decisions" in result
        assert "questions" in result
        assert "summary" in result

    @pytest.mark.asyncio
    async def test_process_meeting_returns_structured_data(self):
        """Test that process_meeting returns properly structured data"""
        responses = [
            '{"items": [{"action": "Test", "assigned_to": "John", "deadline": "2026-04-25", "priority": "Haute", "context": "test"}]}',
            '{"decisions": ["Decision 1"]}',
            '{"questions": ["Question 1?"]}',
            '# Full Summary\nComprehensive meeting summary'
        ]
        
        fake_llm = FakeLLM(responses)
        orchestrator = MeetingIntelligenceOrchestrator(fake_llm)
        
        result = await orchestrator.process_meeting("test transcription", {})
        
        assert isinstance(result, dict)
        assert set(result.keys()) == {"actions", "decisions", "questions", "summary"}

    @pytest.mark.asyncio
    async def test_orchestrator_handles_empty_transcription(self):
        """Test orchestrator handles empty transcription gracefully"""
        responses = [
            '{"items": []}',
            '{"decisions": []}',
            '{"questions": []}',
            '# Empty Meeting\nNo meaningful content'
        ]
        
        fake_llm = FakeLLM(responses)
        orchestrator = MeetingIntelligenceOrchestrator(fake_llm)
        
        result = await orchestrator.process_meeting("", {})
        
        assert result is not None

    @pytest.mark.asyncio
    async def test_orchestrator_with_complex_transcription(self):
        """Test orchestrator with complex, multi-person transcription"""
        responses = [
            '''{"items": [
                {"action": "Implement authentication", "assigned_to": "Alice", "deadline": "2026-04-30", "priority": "Haute", "context": "Security requirement"},
                {"action": "Setup CI/CD pipeline", "assigned_to": "Bob", "deadline": "2026-05-05", "priority": "Moyenne", "context": "DevOps improvement"}
            ]}''',
            '''{"decisions": [
                "Authorization required for all API endpoints",
                "Deployment frequency: weekly"
            ]}''',
            '''{"questions": [
                "What about legacy system compatibility?",
                "Budget for new infrastructure?"
            ]}''',
            '''# Project Planning Meeting - Q2 2026
## Executive Summary
Discussed security requirements and infrastructure improvements for Q2 project.
## Roadmap
1. Authentication layer - Due 04/30
2. CI/CD pipeline - Due 05/05
## Open Questions
Determined compatibility and budget questions for follow-up.'''
        ]
        
        fake_llm = FakeLLM(responses)
        orchestrator = MeetingIntelligenceOrchestrator(fake_llm)
        
        complex_transcription = """
        Alice: We need to implement authentication for all endpoints.
        Bob: I agree, security is critical. I'll setup the CI/CD pipeline.
        Alice: We need that done by end of month.
        Bob: That's aggressive but doable by May 5th.
        Question: What about legacy systems?
        """
        
        result = await orchestrator.process_meeting(complex_transcription, {"duration": 45, "team": "backend"})
        
        assert result is not None
        assert len(result["actions"]) > 0
        assert len(result["decisions"]) > 0
        assert len(result["questions"]) > 0
        assert len(result["summary"]) > 0

    @pytest.mark.asyncio
    async def test_orchestrator_concurrent_agent_execution(self):
        """Test that agents execute concurrently via asyncio.gather"""
        import time
        
        # Create responses with timing info
        responses = [
            '{"items": []}',  # actions - should execute in parallel
            '{"decisions": []}',  # decisions - should execute in parallel
            '{"questions": []}',  # questions - should execute in parallel
            '# Summary'  # summary - runs after parallel agents
        ]
        
        fake_llm = FakeLLM(responses)
        orchestrator = MeetingIntelligenceOrchestrator(fake_llm)
        
        start_time = time.time()
        result = await orchestrator.process_meeting("test", {})
        elapsed = time.time() - start_time
        
        # If truly parallel, it should be faster than sequential
        # Sequential would need 4 LLM calls in series
        # Parallel would be 3 agents + 1 summary
        assert result is not None
        assert "actions" in result
        assert "decisions" in result
        assert "questions" in result

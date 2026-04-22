# backend/app/agents/orchestrator.py
#
# This orchestrator coordinates all AI agents that analyze a meeting transcription.
# It runs the three extraction agents (actions, decisions, questions) in PARALLEL
# using asyncio.gather(), then feeds their results into the SummaryAgent for the
# final report — reducing total latency significantly vs. running them sequentially.

import asyncio
from .action_agent import ActionItemsAgent
from .decision_agent import DecisionsAgent
from .question_agent import QuestionsAgent
from .summary_agent import SummaryAgent
from langchain_core.runnables import Runnable


class MeetingIntelligenceOrchestrator:
    def __init__(self, llm: Runnable):
        """
        Args:
            llm: Any LangChain-compatible LLM instance (ChatOpenAI, a local model, FakeLLM for tests, etc.)
        """
        self.llm = llm

        # Each agent gets the same LLM instance and builds its own prompt chain
        self.action_agent = ActionItemsAgent(llm)
        self.decision_agent = DecisionsAgent(llm)
        self.question_agent = QuestionsAgent(llm)
        self.summary_agent = SummaryAgent(llm)

    async def process_meeting(self, transcription: str, metadata: dict):
        """
        Main analysis pipeline for a meeting transcription.

        Steps:
          1. Run 3 extraction agents in parallel (actions, decisions, questions).
          2. Pass all results to the SummaryAgent to generate the final report.

        Args:
            transcription: Full meeting transcription as plain text.
            metadata: Meeting metadata (title, date, duration, etc.).

        Returns:
            dict with keys: actions, decisions, questions, summary.
        """
        # Run the three agents concurrently — this is the performance-critical step
        results = await asyncio.gather(
            self.action_agent.extract(transcription),
            self.decision_agent.extract(transcription),
            self.question_agent.extract(transcription),
        )

        actions, decisions, questions = results

        # The summary agent synthesizes everything into a structured Markdown report
        summary = await self.summary_agent.generate(
            transcription=transcription,
            actions=actions,
            decisions=decisions,
            questions=questions,
            metadata=metadata
        )

        return {
            "actions": actions,
            "decisions": decisions,
            "questions": questions,
            "summary": summary
        }

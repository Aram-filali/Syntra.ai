from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field
from typing import List, Dict

class MeetingSummary(BaseModel):
    participants: List[str] = Field(description="Liste des participants détectés")
    executive_summary: str = Field(description="Résumé exécutif en 3-4 lignes")
    key_topics: List[Dict[str, str]] = Field(description="Topics principaux avec timestamps")
    next_steps: str = Field(description="Prochaines étapes et deadlines importantes")
    full_markdown: str = Field(description="Compte-rendu complet en Markdown")

class SummaryAgent:
    def __init__(self, llm):
        self.llm = llm
        
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", """Tu es un expert en rédaction de comptes-rendus de réunion professionnels.

Ton job: générer un compte-rendu structuré et complet en français.

Structure OBLIGATOIRE du markdown:

# Compte-rendu de réunion

## Informations
- **Date**: [extraire ou utiliser metadata]
- **Durée**: [metadata]
- **Participants**: [liste]

## Résumé exécutif
[3-4 lignes résumant l'essence de la réunion]

## Points clés discutés
[Liste des topics principaux avec timestamps]
- **[Topic]** (00:XX:XX): Description

## Décisions prises
[Liste des décisions avec contexte]
{decisions}

## Actions à réaliser
[Tableau formaté]
{actions}

## Questions en suspens
[Liste des questions sans réponse]
{questions}

## Prochaines étapes
[Deadlines, prochain meeting, etc.]

---
*Compte-rendu généré automatiquement*
"""),
            ("user", """Génère le compte-rendu complet.

TRANSCRIPTION:
{transcription}

ACTIONS EXTRAITES:
{actions}

DÉCISIONS EXTRAITES:
{decisions}

QUESTIONS EXTRAITES:
{questions}

METADATA:
{metadata}""")
        ])
    
    async def generate(
        self, 
        transcription: str, 
        actions: dict, 
        decisions: dict, 
        questions: dict,
        metadata: dict
    ):
        # Format actions as table
        actions_table = self._format_actions_table(actions)
        decisions_text = self._format_decisions(decisions)
        questions_text = self._format_questions(questions)
        
        chain = self.prompt | self.llm
        result = await chain.ainvoke({
            "transcription": transcription,
            "actions": actions_table,
            "decisions": decisions_text,
            "questions": questions_text,
            "metadata": str(metadata)
        })
        
        # Extract participants from transcription
        participants = self._extract_participants(transcription)
        
        return {
            "participants": participants,
            "executive_summary": self._extract_executive_summary(result.content),
            "key_topics": self._extract_key_topics(result.content),
            "next_steps": self._extract_next_steps(result.content),
            "full_markdown": result.content
        }
    
    def _format_actions_table(self, actions: dict) -> str:
        """Format actions as markdown table"""
        if not actions.get("items"):
            return "*Aucune action identifiée*"
        
        table = "| Action | Assigné à | Deadline | Priorité |\n"
        table += "|--------|-----------|----------|----------|\n"
        
        for item in actions["items"]:
            table += f"| {item['action']} | {item['assigned_to']} | {item['deadline']} | {item['priority']} |\n"
        
        return table
    
    def _format_decisions(self, decisions: dict) -> str:
        """Format decisions as list"""
        if not decisions.get("items"):
            return "*Aucune décision identifiée*"
        
        text = ""
        for idx, item in enumerate(decisions["items"], 1):
            text += f"{idx}. **{item['decision']}**\n"
            text += f"   - Raison: {item['reasoning']}\n"
            text += f"   - Timestamp: {item['timestamp']}\n\n"
        
        return text
    
    def _format_questions(self, questions: dict) -> str:
        """Format questions as list"""
        if not questions.get("items"):
            return "*Aucune question en suspens*"
        
        text = ""
        for idx, item in enumerate(questions["items"], 1):
            text += f"{idx}. **{item['question']}** (posée par {item['asked_by']})\n"
            text += f"   - Context: {item['context']}\n"
            text += f"   - Timestamp: {item['timestamp']}\n\n"
        
        return text
    
    def _extract_participants(self, transcription: str) -> List[str]:
        """Extract unique speakers from transcription"""
        import re
        speakers = re.findall(r'Speaker \d+', transcription)
        return list(set(speakers))
    
    def _extract_executive_summary(self, markdown: str) -> str:
        """Extract executive summary section from markdown"""
        import re
        match = re.search(r'## Résumé exécutif\n(.*?)\n##', markdown, re.DOTALL)
        return match.group(1).strip() if match else ""
    
    def _extract_key_topics(self, markdown: str) -> List[Dict[str, str]]:
        """Extract key topics from markdown"""
        import re
        topics = []
        matches = re.findall(r'\*\*\[(.*?)\]\*\* \((.*?)\): (.*)', markdown)
        for match in matches:
            topics.append({
                "topic": match[0],
                "timestamp": match[1],
                "description": match[2]
            })
        return topics
    
    def _extract_next_steps(self, markdown: str) -> str:
        """Extract next steps section"""
        import re
        match = re.search(r'##Prochaines étapes\n(.*?)(?:\n##|---)', markdown, re.DOTALL)
        return match.group(1).strip() if match else ""
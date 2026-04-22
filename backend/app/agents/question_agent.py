from langchain_core.prompts import ChatPromptTemplate
from langchain.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field
from typing import List

class UnansweredQuestion(BaseModel):
    question: str = Field(description="La question posée")
    asked_by: str = Field(description="Qui a posé la question (Speaker X)")
    context: str = Field(description="Contexte/sujet de la question")
    timestamp: str = Field(description="Timestamp dans transcription")

class Questions(BaseModel):
    items: List[UnansweredQuestion]

class QuestionsAgent:
    def __init__(self, llm):
        self.llm = llm
        self.parser = PydanticOutputParser(pydantic_object=Questions)
        
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", """Tu es un expert en identification de questions restées sans réponse.

Ton job: identifier les questions SANS RÉPONSE CLAIRE.

Critères:
- Question posée explicitement ("Est-ce que...", "Comment...", "Pourquoi...")
- Pas de réponse dans les 2 minutes suivantes
- Marquée "à revoir", "on en reparle", "je ne sais pas"
- Réponse évasive ou incomplète

NE PAS inclure:
- Questions rhétoriques
- Questions avec réponse claire
- Questions triviales ("Comment ça va?")

{format_instructions}"""),
            ("user", "Transcription:\n\n{transcription}")
        ])
    
    async def extract(self, transcription: str):
        chain = self.prompt | self.llm | self.parser
        result = await chain.ainvoke({
            "transcription": transcription,
            "format_instructions": self.parser.get_format_instructions()
        })
        return result.model_dump()
from langchain_core.prompts import ChatPromptTemplate
from langchain.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field
from typing import List

class Decision(BaseModel):
    decision: str = Field(description="La décision prise")
    reasoning: str = Field(description="Raison/contexte de la décision")
    timestamp: str = Field(description="Timestamp dans transcription")

class Decisions(BaseModel):
    items: List[Decision]

class DecisionsAgent:
    def __init__(self, llm):
        self.llm = llm
        self.parser = PydanticOutputParser(pydantic_object=Decisions)
        
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", """Tu es un expert en identification de décisions prises durant des réunions.

Ton job: identifier toutes les DÉCISIONS EXPLICITES.

Critères décision:
- Consensus atteint ("OK on fait ça", "D'accord", "Allons-y avec X")
- Choix entre options A vs B
- Validation d'une proposition
- Rejet d'une option ("Non, on ne fait pas ça")

NE PAS confondre avec:
- Simple discussion
- Questions
- Propositions non validées

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
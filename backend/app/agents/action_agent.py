from langchain_core.prompts import ChatPromptTemplate
from langchain.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field
from typing import List

class ActionItem(BaseModel):
    action: str = Field(description="Description de l'action")
    assigned_to: str = Field(description="Personne assignée (Speaker X ou nom)")
    deadline: str = Field(description="Deadline mentionnée ou 'Non spécifié'")
    priority: str = Field(description="Haute/Moyenne/Basse")
    context: str = Field(description="Context de pourquoi cette action")

class ActionItems(BaseModel):
    items: List[ActionItem]

class ActionItemsAgent:
    def __init__(self, llm):
        self.llm = llm
        self.parser = PydanticOutputParser(pydantic_object=ActionItems)
        
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", """Tu es un expert en extraction d'action items depuis des transcriptions de réunions.

Ton job: identifier TOUTES les tâches mentionnées, même implicites.

Critères action item:
- Quelqu'un dit "je vais faire X"
- "Il faut qu'on fasse Y"
- "Peux-tu gérer Z?"
- Assignation explicite ou implicite

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

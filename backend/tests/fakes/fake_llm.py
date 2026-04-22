from langchain_core.runnables import Runnable
from langchain_core.messages import AIMessage

class FakeLLM(Runnable):
    def __init__(self, responses):
        if isinstance(responses, str):
            self.responses = [responses]
        else:
            self.responses = responses

        self.index = 0

    def _next_response(self):
        if self.index >= len(self.responses):
            raise RuntimeError("FakeLLM: plus de réponses disponibles")
        response = self.responses[self.index]
        self.index += 1
        return response

    def invoke(self, input, config=None):
        return AIMessage(content=self._next_response())

    async def ainvoke(self, input, config=None):
        return AIMessage(content=self._next_response())

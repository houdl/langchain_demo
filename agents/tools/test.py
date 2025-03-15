from langchain.tools import BaseTool
from pydantic import BaseModel, Field
from typing import Type


class TestInput(BaseModel):
    query: str = Field(description="The input query to the tool")

class TestTool(BaseTool):
    name: str = "TestTool"
    description: str = "A tool that if input test tool."
    args_schema: Type[BaseModel] = TestInput

    def _run(self, query: str) -> str:
        result = f"TestTool executed when input: {query}"
        return result

    async def _arun(self, query: str) -> str:
        """Use the tool asynchronously."""
        result = f"TestTool executed when input: {query}"
        return result

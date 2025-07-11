from llama_index.core.tools.types import BaseTool
from pydantic import BaseModel

class QueryInput(BaseModel):
    query: str

class MyTool(BaseTool):
    args_schema = QueryInput
    def __call__(self, query: str) -> str:
        return query


if __name__ == '__main__':
    pass
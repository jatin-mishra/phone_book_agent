
from .tool import Tool, GetPersonsPhoneNumber


class ToolRepository:

    def __init__(self):
        phone_number_tool = GetPersonsPhoneNumber()
        self.tool = {
            phone_number_tool.get_name() : phone_number_tool
        }

    def _does_tool_exist(self, name) -> bool:
        return name in self.tool

    def get_schema(self, name) -> dict:
        if not self._does_tool_exist(name):
            raise RuntimeError(f"Unknown tool: {name}")
        return self.tool.get(name).get_schema()

    # pipeline to be generalized
    def get_instances(self, execution_pipeline: list[str]) -> list[Tool]:
        if any(not self._does_tool_exist(tool_name) for tool_name in execution_pipeline):
            raise RuntimeError("Unknown tools")
        return [self.tool[name] for name in execution_pipeline]
        




    
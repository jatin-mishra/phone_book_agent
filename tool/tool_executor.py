from tool.tool import Tool
from tool.tool_repo import ToolRepository


class ToolExecutor:

    def __init__(self, log_enabled):
        self.tool_repo = ToolRepository()
        self.executor_logging = log_enabled

    def log(self, mssg):
        if self.executor_logging:
            print()
            print(f"INFO: {mssg}")
            print()


    async def execute(self, tools: list[dict]) -> list[dict]:
        response = []
        tool_instances = { 
            tool_instance.get_name() : tool_instance 
            for tool_instance in self.tool_repo.get_instances([ tool_block["name"] for tool_block in tools ])
        }
        for tool_block in tools:
            name, input = tool_block["name"], tool_block["input"]
            output = await tool_instances.get(name).execute(input)
            self.log(f"tool: {name}, input: {input}, output: {output}")
            if "error" in output: 
                response.append(
                    {
                        "content" : f"Failed to execute, here is error {str(output)}, retry after fixing.",
                        "tool_use_id" : tool_block["id"],
                        "type" : "tool_result"
                    }
                )
            else:
                response.append(
                    {
                        "content" : str(output),
                        "tool_use_id" : tool_block["id"],
                        "type" : "tool_result"
                    }
                )
        return response
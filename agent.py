import asyncio
from provider.anthropic_provider import AnthropicProvider
from tool.tool_repo import ToolRepository
from tool.tool_executor import ToolExecutor
from message import MessageContext, Message
import json

class Agent:

    def __init__(self):
        self.model = "haiku_model"
        self.max_attempts = 10
        self.debug_enabled = True
        self.tool_executor = ToolExecutor(self.debug_enabled)
        self.tool_repo = ToolRepository()
        self.registered_tools = ["get_phone_number"]
        self.system_prompt = """
        You are helpful assistant who helps people find phone number of people.
        People might not put accurate numbers, hence make sure to do fuzzy matching.
        unless match score with name is more than 80%, don't assume name is same else if >80% then assume same.
        """
        self.output_config_schema = {
            "type": "object",
            "properties": {
                "type": {
                    "type": "string",
                    "description" : "if model needs to ask some question then user_input else if model found the answer then answer | understand if model is still trying to find and want to get direction from user then its user_input, else if model found the answer or has tried more than 3 times based on user direction, then just answer",
                    "enum": ["user_input", "answer"]
                },
                "content": {
                    "type": "string",
                    "description" : "if model needs to asking some question then question content else if model is answering then answer content"
                }
            },
            "required": ["type", "content"],
            "additionalProperties": False
        }

    def log(self, message: str):
        if self.debug_enabled:
            print()
            print("INFO: " + message)
            print()
        

    async def run(self):
        provider = AnthropicProvider()
        user_query = "Give me mobile number of Jatin"
        # user_query = input("User : ")
        print(user_query)
        was_tool_result_asked = False 
        was_user_input_asked = True
        tool_results = []

        attempts = 0
        while True:

            if attempts > self.max_attempts:
                return

            attempts += 1

            if was_user_input_asked:
                provider.add_user_query_in_context(user_query)
                was_user_input_asked = False

            elif was_tool_result_asked and tool_results:
                provider.add_tool_result_in_context(tool_results=tool_results)
                was_tool_result_asked = False

            self.log("Calling...")

            response = await provider.message(message_context=MessageContext(
                model=self.model,
                tools=[ self.tool_repo.get_schema(name) for name in self.registered_tools ],
                system_prompt=self.system_prompt,
                message=Message(
                    type="text",
                    content=user_query
                ) if was_user_input_asked else None,
                structured_schema={
                    "type" : "json_schema",
                    "schema" : self.output_config_schema
                }
            ))

            self.log("received response ... ")
            self.log(f"{str(response)}")

            if provider.is_tool_call(response):
                self.log("calling tool... ")
                was_tool_result_asked = True
                tools_pipeline = provider.extract_tool_use_block(response)
                tool_results = await self.tool_executor.execute(tools_pipeline)
                self.log(f"tool results: {tool_results}")

            elif provider.is_completed(response) and self._is_input_required(self._parse_as_json(provider.extract_query_block(response))):
                self.log("might require input... ")
                was_user_input_asked = True
                query = self._extract_content_from_structured_output(self._parse_as_json(provider.extract_query_block(response)))
                print()
                print(f"LLM : {query}")
                print()
                user_query = input("User : ")

            else: 
                self.log("answered ... ")
                block = self._parse_as_json(provider.extract_query_block(response))
                print()
                print(f"LLM: {self._extract_content_from_structured_output(block)}")
                print()
                while True:
                    print("Agent: do you have any more query on this? 1. Yes, 2. No")
                    query = input("User : ")
                    if query not in ("1", "2"):
                        print("Pick 1/2")
                        print()
                    elif query == "1":
                        print()
                        was_user_input_asked = True
                        user_query = input("User: ")
                        break
                    else:
                        print()
                        print("Bye!")
                        return 

    def _parse_as_json(self, content):
        return json.loads(content)

    def _is_input_required(self, block):
        self.log(f"block: {block}")
        return block["type"] == "user_input"

    def _has_llm_answered(self, block):
        self.log(f"block: {block}")
        return block["type"] == "answer"

    def _extract_content_from_structured_output(self, block):
        self.log(f"block: {block}")
        return block["content"]

agent = Agent()
if __name__ == "__main__":
    asyncio.run(agent.run())



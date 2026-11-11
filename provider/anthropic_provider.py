from .llm_provider import LLMProvider
from message import Message, MessageContext
from anthropic import AsyncAnthropic
import os

class AnthropicProvider(LLMProvider):

    def __init__(self):
        self.client = AsyncAnthropic(
            api_key=os.environ.get("ANTHROPIC_AGENT_API_KEY")
        )
        self.default_model = os.environ.get("haiku_model")
        self.max_tokens = 2048
        self.context = []

    def add_user_query_in_context(self, content: str):
        self.context.append({
            "role" : "user",
            "content" : f"answer this: {content}"
        })

    async def message(self, message_context: MessageContext):
        
        if not message_context.system_prompt:
            response = await self.client.messages.create(
                model = os.environ.get(message_context.model) if message_context.model else os.environ.get(self.default_model),
                system = message_context.system_prompt,
                max_tokens = message_context.max_tokens or self.max_tokens,
                messages = self.context,
                tools = message_context.tools if message_context.tools else [],
                output_config = {
                    "format" : message_context.structured_schema
                } if message_context.structured_schema else None
            )
        else:
            response = await self.client.messages.create(
                model = os.environ.get(message_context.model) if message_context.model else os.environ.get(self.default_model),
                max_tokens = message_context.max_tokens or self.max_tokens,
                messages = self.context,
                tools = message_context.tools if message_context.tools else [],
                output_config = {
                    "format" : message_context.structured_schema
                } if message_context.structured_schema else None
            )
        self.context.append({
            "role" : "assistant",
            "content" : response.content
        })
        return response

    def is_tool_call(self, response) -> bool:
        return response.stop_reason == "tool_use"

    def is_completed(self, response) -> bool:
        return response.stop_reason == "end_turn"

    def extract_tool_use_block(self, response):
        if not self.is_tool_call(response=response):
            raise RuntimeError("No tool use block")
        tool_use_blocks = []
        for block in response.content:
            if block.type == "tool_use":
                tool_use_blocks.append({
                    "name" : block.name,
                    "input" : block.input,
                    "id" : block.id
                })
        return tool_use_blocks

    def add_tool_result_in_context(self, tool_results):
        self.context.append({
            "role" : "user",
            "content" : tool_results
        })

    def extract_query_block(self, response):
        for block in response.content:
            if block.type == "text":
                return block.text
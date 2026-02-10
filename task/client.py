import json
from typing import Any

import requests

from task.models.message import Message
from task.models.role import Role
from task.tools.base import BaseTool


class DialClient:

    def __init__(
            self,
            endpoint: str,
            deployment_name: str,
            api_key: str,
            tools: list[BaseTool] | None = None
    ):
        if not api_key:
            raise ValueError("API key is required")

        self.__endpoint = f"{endpoint}/openai/deployments/{deployment_name}/chat/completions"
        self.__api_key = api_key
        self.__tools_dict = {}
        self.__tools = []

        if tools:
            for tool in tools:
                self.__tools_dict[tool.name] = tool
                self.__tools.append(tool.schema)

        print(f"DIAL Endpoint: {self.__endpoint}")
        if self.__tools:
            print("Available tools:")
            for tool in self.__tools:
                print(f"  - {tool['function']['name']}")


    def get_completion(self, messages: list[Message], print_request: bool = True) -> Message:
        headers = {
            "api-key": self.__api_key,
            "Content-Type": "application/json"
        }

        request_data = {
            "messages": [msg.to_dict() for msg in messages],
            "tools": self.__tools
        }

        if print_request:
            print("\n" + "="*50)
            print("REQUEST MESSAGES:")
            for msg in messages:
                print(f"  [{msg.role.value}]: {msg.content[:100]}...")
            print("="*50)

        response = requests.post(
            url=self.__endpoint,
            headers=headers,
            json=request_data
        )

        if response.status_code == 200:
            response_json = response.json()
            choices = response_json.get("choices", [])

            if choices:
                choice = choices[0]
                if print_request:
                    print(f"Choice: {choice}")

                message_data = choice.get("message", {})
                content = message_data.get("content", "")
                tool_calls = message_data.get("tool_calls", None)

                ai_response = Message(
                    role=Role.AI,
                    content=content,
                    tool_calls=tool_calls
                )

                finish_reason = choice.get("finish_reason", "")

                if finish_reason == "tool_calls" and tool_calls:
                    messages.append(ai_response)
                    tool_messages = self._process_tool_calls(tool_calls)
                    messages.extend(tool_messages)
                    return self.get_completion(messages, print_request)
                else:
                    return ai_response

        raise Exception(f"API Error: {response.status_code} {response.text}")


    def _process_tool_calls(self, tool_calls: list[dict[str, Any]]) -> list[Message]:
        """Process tool calls and add results to messages."""
        tool_messages = []
        for tool_call in tool_calls:
            tool_call_id = tool_call.get("id")
            function = tool_call.get("function", {})
            function_name = function.get("name")
            arguments = json.loads(function.get("arguments", "{}"))

            tool_execution_result = self._call_tool(function_name, arguments)

            tool_messages.append(Message(
                role=Role.TOOL,
                name=function_name,
                tool_call_id=tool_call_id,
                content=tool_execution_result
            ))

            print(f"FUNCTION '{function_name}'\n{tool_execution_result}\n{'-'*50}")

        return tool_messages

    def _call_tool(self, function_name: str, arguments: dict[str, Any]) -> str:
        if function_name in self.__tools_dict:
            tool = self.__tools_dict[function_name]
            return tool.execute(arguments)
        else:
            return f"Unknown function: {function_name}"

import os

from task.client import DialClient
from task.models.conversation import Conversation
from task.models.message import Message
from task.models.role import Role
from task.prompts import SYSTEM_PROMPT
from task.tools.users.create_user_tool import CreateUserTool
from task.tools.users.delete_user_tool import DeleteUserTool
from task.tools.users.get_user_by_id_tool import GetUserByIdTool
from task.tools.users.search_users_tool import SearchUsersTool
from task.tools.users.update_user_tool import UpdateUserTool
from task.tools.users.user_client import UserClient
from task.tools.web_search import WebSearchTool

DIAL_ENDPOINT = "https://ai-proxy.lab.epam.com"
API_KEY = os.getenv('DIAL_API_KEY')

def main():
    user_client = UserClient()

    tools = [
        WebSearchTool(API_KEY, DIAL_ENDPOINT),
        GetUserByIdTool(user_client),
        SearchUsersTool(user_client),
        CreateUserTool(user_client),
        UpdateUserTool(user_client),
        DeleteUserTool(user_client)
    ]

    dial_client = DialClient(
        endpoint=DIAL_ENDPOINT,
        deployment_name="gpt-4o",
        api_key=API_KEY,
        tools=tools
    )

    conversation = Conversation()
    conversation.add_message(Message(role=Role.SYSTEM, content=SYSTEM_PROMPT))

    print("Welcome to User Management Agent!")
    print("Type 'exit' to quit\n")

    while True:
        user_input = input("> ").strip()

        if user_input.lower() == "exit":
            print("Goodbye!")
            break

        if not user_input:
            continue

        conversation.add_message(Message(role=Role.USER, content=user_input))

        response = dial_client.get_completion(conversation.get_messages(), print_request=False)
        print(f"\nAssistant: {response.content}\n")

        conversation.add_message(response)


main()

#TODO:
# Request sample:
# Add Andrej Karpathy as a new user
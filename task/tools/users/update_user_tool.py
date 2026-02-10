from typing import Any

from task.tools.users.base import BaseUserServiceTool
from task.tools.users.models.user_info import UserUpdate


class UpdateUserTool(BaseUserServiceTool):

    @property
    def name(self) -> str:
        return "update_user"

    @property
    def description(self) -> str:
        return "Update user information"

    @property
    def input_schema(self) -> dict[str, Any]:
        update_schema = UserUpdate.model_json_schema()
        return {
            "type": "object",
            "properties": {
                "id": {
                    "type": "number",
                    "description": "User ID that should be updated"
                },
                "new_info": {
                    "type": "object",
                    "description": "New user information",
                    "properties": update_schema.get("properties", {}),
                    "required": update_schema.get("required", [])
                }
            },
            "required": ["id", "new_info"]
        }

    def execute(self, arguments: dict[str, Any]) -> str:
        try:
            user_id = int(arguments["id"])
            new_info = UserUpdate.model_validate(arguments["new_info"])
            return self._user_client.update_user(user_id, new_info)
        except Exception as e:
            return f"Error while creating a new user: {str(e)}"

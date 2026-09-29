ALLOWED_TOOLS = {
    "search_repository",
    "read_file",
    "retrieve_code",
    "search_code",
}

BLOCKED_TOOLS = {
    "delete_file",
    "modify_file",
    "execute_shell",
    "execute_command",
    "read_environment",
    "read_secrets",
    "git_push",
    "git_reset",
}


def check_tool(tool_name: str):
    """
    Check whether an agent is allowed to execute a tool.
    """

    if tool_name in ALLOWED_TOOLS:
        return {
            "allowed": True,
            "requires_confirmation": False,
            "reason": "Read-only repository operation"
        }

    if tool_name in BLOCKED_TOOLS:
        return {
            "allowed": False,
            "requires_confirmation": True,
            "reason": "Potentially destructive or sensitive operation"
        }

    return {
        "allowed": False,
        "requires_confirmation": False,
        "reason": "Unknown tool is not permitted"
    }
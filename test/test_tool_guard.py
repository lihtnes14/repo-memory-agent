from backend.guardrails.tool_guard import check_tool


tools = [
    "search_repository",
    "read_file",
    "retrieve_code",
    "search_code",
    "delete_file",
    "modify_file",
    "execute_shell",
    "read_environment",
    "git_push",
    "unknown_tool",
]


for tool in tools:

    result = check_tool(tool)

    print("\n" + "=" * 70)
    print("TOOL")
    print(tool)

    print("\nRESULT")
    print(result)
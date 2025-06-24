import asyncio
import nest_asyncio
from llama_index.llms.ollama import Ollama
from llama_index.core import Settings
from llama_index.tools.mcp import BasicMCPClient, McpToolSpec
from llama_index.core.agent.workflow import FunctionAgent, ToolCallResult, ToolCall
from llama_index.core.workflow import Context

async def main():
    nest_asyncio.apply()

    # Setup a local LLM
    print("🦙 Initializing Ollama LLM...")
    llm = Ollama(model="llama3.2", request_timeout=120.0)
    Settings.llm = llm

    # Initialize the MCP client
    print("🔗 Connecting to PostgreSQL MCP server...")
    mcp_client = BasicMCPClient("http://127.0.0.1:8000/sse")
    mcp_tool_spec = McpToolSpec(client=mcp_client)

    # Get the list of tools
    try:
        tools = await mcp_tool_spec.to_tool_list_async()
        print(f"✅ Found {len(tools)} tools:")
        for tool in tools:
            print(f"  📋 {tool.metadata.name}: {tool.metadata.description[:100]}...")
    except Exception as e:
        print(f"❌ Could not connect to MCP server: {e}")
        print("🔧 Please start the PostgreSQL server first: uv run server.py --server_type=sse")
        return    # Define the system prompt
    SYSTEM_PROMPT = """\
You are an AI assistant that works with a PostgreSQL database.

Your task is to understand user requests, and use the available tools to perform database operations.
When a user asks for an action (e.g., adding, reading, or querying data), you must select the appropriate tool, call it with the necessary parameters, and report the result to the user.

IMPORTANT RULES:
1. When user asks to add multiple people (e.g., "add 3 people", "add 5 random Turkish people"), you MUST call the `add_person` tool multiple times - once for each person.
2. Generate diverse, realistic names, ages, and professions for each person.
3. For Turkish names, use authentic Turkish first and last names.
4. DO NOT output JSON. Always call the tool and report the result as plain text.
5. Complete ALL requested operations before responding.

Example Flow:
User: "Add 3 random Turkish people"
You: (Call `add_person` tool 3 times with different Turkish names, ages, and professions)
You: "Successfully added 3 Turkish people to the database."

Available Tools: `add_data`, `add_person`, `read_data`, `get_table_info`.

Database Schema (`people` table):
- id: SERIAL PRIMARY KEY
- name: VARCHAR(255)
- age: INTEGER
- profession: VARCHAR(255)
- created_at: TIMESTAMP
"""

    # Helper function to get the agent
    async def get_agent(tools: McpToolSpec):
        tools_list = await tools.to_tool_list_async()
        agent = FunctionAgent(
            name="PostgreSQL Agent",
            description="An AI assistant that works with a PostgreSQL database.",
            tools=tools_list,
            llm=Settings.llm,
            system_prompt=SYSTEM_PROMPT,
        )
        return agent

    # Helper function to handle user messages
    async def handle_user_message(
        message_content: str,
        agent: FunctionAgent,
        agent_context: Context,
        verbose: bool = True,
    ):
        handler = agent.run(message_content, ctx=agent_context)
        async for event in handler.stream_events():
            if verbose and isinstance(event, ToolCall):
                print(f"🔧 Calling tool: {event.tool_name}")
                if event.tool_kwargs:
                    for key, value in event.tool_kwargs.items():
                        if len(str(value)) > 100:
                            print(f"   {key}: {str(value)[:100]}...")
                        else:
                            print(f"   {key}: {value}")
            elif verbose and isinstance(event, ToolCallResult):
                print(f"✅ Tool result: {event.tool_name}")

        response = await handler
        return str(response)

    # Initialize the agent
    print("🤖 Creating AI Agent...")
    agent = await get_agent(mcp_tool_spec)

    # Create the agent context
    agent_context = Context(agent)

    # Sample commands for user reference
    print("\n" + "="*60)
    print("🚀 PostgreSQL MCP Client Ready!")
    print("="*60)
    print("📝 Example Commands:")
    print("  • 'show data' - List all records")
    print("  • 'get table info' - Show table structure")
    print("  • 'add John Doe, 28 years old, software engineer' - Add a new record")
    print("  • 'show people older than 30' - Filtering")
    print("  • 'how many people are there?' - Count")
    print("  • 'exit' - Quit")
    print("="*60)

    # Run the agent!
    while True:
        try:
            user_input = input("\n💬 Your message: ")
            if user_input.lower() in ['exit', 'quit']:
                print("👋 Goodbye!")
                break
            
            print(f"\n🧠 Processing: {user_input}")
            print("-" * 40)
            
            response = await handle_user_message(user_input, agent, agent_context, verbose=True)
            
            print("-" * 40)
            print(f"🤖 Response: {response}")
            
        except (KeyboardInterrupt, EOFError):
            print("\n👋 Exiting...")
            break
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(main()) 
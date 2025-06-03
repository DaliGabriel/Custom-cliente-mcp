import asyncio
from typing import Optional
from contextlib import AsyncExitStack
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from dotenv import load_dotenv
from google import genai
from google.genai import types
import os
import sys


load_dotenv()

class MCPClient:
    def __init__(self):
        self.session: Optional[ClientSession] = None
        self.exit_stack = AsyncExitStack()
        self.client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))
        self.tools = None

    async def connect_to_server(self, server_script_path: str):
        """Connect to an MCP server and initialize tools"""
        is_python = server_script_path.endswith('.py')
        is_js = server_script_path.endswith('.js')
        if not (is_python or is_js):
            raise ValueError("Server script must be a .py or .js file")

        command = "python" if is_python else "node"
        server_params = StdioServerParameters(
            command=command,
            args=[server_script_path],
            env=None
        )

        stdio_transport = await self.exit_stack.enter_async_context(stdio_client(server_params))
        self.stdio, self.write = stdio_transport
        self.session = await self.exit_stack.enter_async_context(ClientSession(self.stdio, self.write))
        await self.session.initialize()

        # Initialize tools from server
        await self.initialize_tools()

    async def initialize_tools(self):
        """Initialize tools from the MCP server"""
        try:
            response = await self.session.list_tools()
            if not response or not hasattr(response, 'tools') or not response.tools:
                print("Warning: No tools found from the server")
                self.tools = types.Tool(function_declarations=[])
                return
                
            function_declarations = []
            
            for tool in response.tools:
                if not tool:
                    print("Warning: Received None tool in tools list")
                    continue
                    
                try:
                    function_declarations.append({
                        "name": getattr(tool, 'name', 'unnamed_tool'),
                        "description": getattr(tool, 'description', ''),
                        "parameters": getattr(tool, 'inputSchema', {})
                    })
                except Exception as e:
                    print(f"Error processing tool: {e}")
            
            if not function_declarations:
                print("Warning: No valid tools found after processing")
            
            self.tools = types.Tool(function_declarations=function_declarations)
            print(f"Initialized {len(function_declarations)} tools")
            
        except Exception as e:
            print(f"Error initializing tools: {e}")
            self.tools = types.Tool(function_declarations=[])

    async def process_query(self, query: str) -> str:
        """Process a query using Gemini and available tools"""
        try:
            if not self.tools:
                return "Error: No tools available. Please check server connection."
                
            print(f"Available tools: {self.tools}")
            
            config = types.GenerateContentConfig(tools=[self.tools])
            
            response = self.client.models.generate_content(
                model="gemini-2.0-flash",
                contents=query,
                config=config,
            )
            print(f"Response received: {response}")

            # Check for function call in response
            if not hasattr(response, 'candidates') or not response.candidates:
                return "No valid response candidates found in the API response"
                
            candidate = response.candidates[0]
            if not hasattr(candidate, 'content') or not candidate.content:
                return "No content in the response candidate"
                
            parts = getattr(candidate.content, 'parts', [])
            if not parts:
                return response.text if hasattr(response, 'text') else "No text content in response"
                
            first_part = parts[0]
            if not hasattr(first_part, 'function_call') or not first_part.function_call:
                return response.text if hasattr(response, 'text') else "No function call in response"
            
            function_call = first_part.function_call
            if not function_call or not hasattr(function_call, 'name') or not hasattr(function_call, 'args'):
                return "Invalid function call format in response"
                
            tool_name = function_call.name
            tool_args = function_call.args
            
            if not tool_name:
                return "No tool name specified in function call"
                
            print(f"Attempting to call tool: {tool_name} with args: {tool_args}")
            
            # Call the tool
            result = await self.session.call_tool(tool_name, tool_args)
            return f"Tool {tool_name} called with args {tool_args}\nResult: {result}"

        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            return f"Error processing query: {str(e)}\n\nDebug info:\n{error_details}"

    async def chat_loop(self):
        """Run an interactive chat loop"""
        print("\nMCP Client Started!")
        print("Type your queries or 'quit' to exit.")

        while True:
            try:
                query = input("\nQuery: ").strip()
                if query.lower() == 'quit':
                    break

                response = await self.process_query(query)
                print("\nResponse:", response)

            except Exception as e:
                print(f"\nError: {str(e)}")

    async def cleanup(self):
        """Clean up resources"""
        await self.exit_stack.aclose()

async def main():
    if len(sys.argv) < 2:
        print("Usage: python client.py <path_to_server_script>")
        sys.exit(1)

    client = MCPClient()
    try:
        await client.connect_to_server(sys.argv[1])
        await client.chat_loop()
    finally:
        await client.cleanup()

if __name__ == "__main__":
    asyncio.run(main())
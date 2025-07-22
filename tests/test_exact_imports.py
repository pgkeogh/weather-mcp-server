# Create test_exact_imports.py
try:
    from mcp.server import Server
    from mcp.types import Tool, TextContent
    print("✅ All imports successful!")
    print(f"Server class: {Server}")
    print(f"Tool class: {Tool}")
    print(f"TextContent class: {TextContent}")
except ImportError as e:
    print(f"❌ Import failed: {e}")
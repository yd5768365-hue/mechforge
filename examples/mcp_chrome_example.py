"""
MechForge + Chrome DevTools MCP 使用示例

此示例展示如何在 MechForge 中集成 Chrome DevTools MCP 服务器，
用于网页截图、JavaScript 执行等功能。
"""
import asyncio
import json
from mechforge_core.mcp.client import MCPClient, MCPClientManager


async def chrome_mcp_demo():
    """Chrome DevTools MCP 演示"""

    # 创建 MCP 客户端
    client = MCPClient(
        command="npx",
        args=["chrome-devtools-mcp@latest", "--headless", "--slim"],
    )

    # 启动客户端
    print("[1] 启动 Chrome DevTools MCP 服务器...")
    if not client.start():
        print("[ERROR] 启动失败")
        return

    print(f"[OK] 已连接，可用工具: {[t.name for t in client.tools]}")

    try:
        # 示例 1: 导航到网页
        print("\n[2] 导航到示例网页...")
        result = client.call_tool("navigate", {
            "url": "https://example.com"
        })
        print(f"[OK] 导航结果: {result}")

        # 示例 2: 执行 JavaScript
        print("\n[3] 执行 JavaScript...")
        result = client.call_tool("evaluate", {
            "script": "document.title"
        })
        print(f"[OK] 页面标题: {result}")

        # 示例 3: 截图
        print("\n[4] 截取网页截图...")
        result = client.call_tool("screenshot", {
            "filename": "screenshot.png"
        })
        print(f"[OK] 截图结果: {result}")

    except Exception as e:
        print(f"[ERROR] {e}")

    finally:
        # 关闭客户端
        print("\n[5] 关闭连接...")
        client.stop()
        print("[OK] 已关闭")


def use_with_manager():
    """使用 MCPClientManager 管理多个 MCP 服务器"""
    manager = MCPClientManager()

    # 添加 Chrome DevTools MCP
    chrome_client = MCPClient(
        command="npx",
        args=["chrome-devtools-mcp@latest", "--headless", "--slim"],
    )

    if manager.add_client("chrome", chrome_client):
        print("[OK] Chrome DevTools MCP 已添加")

        # 获取所有可用工具
        all_tools = manager.get_all_tools()
        print(f"\n所有可用工具 ({len(all_tools)} 个):")
        for tool in all_tools:
            print(f"  - {tool.name}: {tool.description}")

        # 调用工具
        try:
            result = manager.call_tool("navigate", {"url": "https://github.com"})
            print(f"\n[OK] 导航结果: {result}")
        except Exception as e:
            print(f"[ERROR] {e}")

    # 清理
    manager.clear()


if __name__ == "__main__":
    print("=" * 60)
    print("MechForge + Chrome DevTools MCP 示例")
    print("=" * 60)

    # 运行演示
    # asyncio.run(chrome_mcp_demo())

    # 或使用管理器
    use_with_manager()

"""
测试 Chrome DevTools MCP 服务器连接
"""
import subprocess
import json
import sys

def test_chrome_mcp():
    """测试 Chrome DevTools MCP 服务器"""
    print("[TEST] 测试 Chrome DevTools MCP 服务器...")
    print("-" * 50)

    # 启动 MCP 服务器进程
    cmd = "npx chrome-devtools-mcp@latest --headless --slim"

    try:
        process = subprocess.Popen(
            cmd,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
            shell=True,
        )

        # 发送初始化请求
        init_request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "mechforge-test", "version": "0.5.0"},
            },
        }

        print("[SEND] 发送初始化请求...")
        process.stdin.write(json.dumps(init_request) + "\n")
        process.stdin.flush()

        # 读取响应
        response_line = process.stdout.readline()
        if not response_line:
            print("[ERROR] 无响应")
            process.terminate()
            return False

        response = json.loads(response_line)
        print(f"[RECV] 收到响应: {json.dumps(response, indent=2, ensure_ascii=False)}")

        if "result" in response:
            print("[OK] MCP 服务器初始化成功!")
            server_info = response["result"].get("serverInfo", {})
            print(f"   服务器: {server_info.get('name', 'unknown')}")
            print(f"   版本: {server_info.get('version', 'unknown')}")
        else:
            print(f"[FAIL] 初始化失败: {response.get('error', '未知错误')}")
            process.terminate()
            return False

        # 获取工具列表
        print("\n[SEND] 请求工具列表...")
        tools_request = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/list",
            "params": {},
        }
        process.stdin.write(json.dumps(tools_request) + "\n")
        process.stdin.flush()

        tools_response_line = process.stdout.readline()
        if tools_response_line:
            tools_response = json.loads(tools_response_line)
            if "result" in tools_response:
                tools = tools_response["result"].get("tools", [])
                print(f"[OK] 发现 {len(tools)} 个工具:")
                for tool in tools:
                    print(f"   - {tool['name']}: {tool.get('description', '无描述')}")
            else:
                print(f"[WARN] 获取工具列表失败: {tools_response.get('error')}")

        # 关闭进程
        process.terminate()
        process.wait(timeout=5)
        print("\n[OK] Chrome DevTools MCP 服务器测试通过!")
        return True

    except subprocess.TimeoutExpired:
        print("[ERROR] 进程超时")
        process.kill()
        return False
    except json.JSONDecodeError as e:
        print(f"[ERROR] JSON 解析失败 - {e}")
        return False
    except Exception as e:
        print(f"[ERROR] {e}")
        return False

if __name__ == "__main__":
    success = test_chrome_mcp()
    sys.exit(0 if success else 1)

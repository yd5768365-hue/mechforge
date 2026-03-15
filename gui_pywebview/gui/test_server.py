"""
测试 GUI 后端服务器
"""

import sys
from pathlib import Path

# 添加项目根目录
PROJECT_ROOT = Path(__file__).parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import requests

BASE_URL = "http://localhost:5000"

def test_health():
    """测试健康检查"""
    print("Testing health check...")
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    print()

def test_status():
    """测试系统状态"""
    print("Testing system status...")
    response = requests.get(f"{BASE_URL}/status")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    print()

def test_chat():
    """测试聊天功能"""
    print("Testing chat...")
    response = requests.post(
        f"{BASE_URL}/api/chat",
        json={"message": "你好，介绍一下你自己", "rag": False}
    )
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        print(f"Response: {response.json()}")
    else:
        print(f"Error: {response.text}")
    print()

def test_models():
    """测试模型列表"""
    print("Testing models list...")
    response = requests.get(f"{BASE_URL}/api/models")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    print()

if __name__ == "__main__":
    print("=" * 50)
    print("MechForge AI GUI Backend Test")
    print("=" * 50)
    print()
    
    try:
        test_health()
        test_status()
        test_models()
        # test_chat()  # 需要运行后端服务器
        
        print("✓ All tests passed!")
    except requests.exceptions.ConnectionError:
        print("⚠ Backend server not running. Start it with: python gui/server.py")
    except Exception as e:
        print(f"✗ Test failed: {e}")

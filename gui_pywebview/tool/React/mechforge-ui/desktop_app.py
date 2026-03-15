#!/usr/bin/env python3
"""
MechForge AI Desktop Application
使用Python webview打包React应用为桌面.exe
"""

import os
import sys
import webview
import threading
import http.server
import socketserver

# 配置
PORT = 8765
TITLE = "MechForge AI"
WIDTH = 1200
HEIGHT = 800

class MyHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=os.path.join(os.path.dirname(__file__), 'build'), **kwargs)
    
    def log_message(self, format, *args):
        # 静默日志
        pass

def start_server():
    """启动本地HTTP服务器"""
    with socketserver.TCPServer(("", PORT), MyHTTPRequestHandler) as httpd:
        print(f"Server started at http://localhost:{PORT}")
        httpd.serve_forever()

def create_window():
    """创建桌面窗口"""
    # 启动HTTP服务器（在后台线程）
    server_thread = threading.Thread(target=start_server, daemon=True)
    server_thread.start()
    
    # 创建窗口
    window = webview.create_window(
        title=TITLE,
        url=f"http://localhost:{PORT}",
        width=WIDTH,
        height=HEIGHT,
        min_size=(900, 600),
        resizable=True,
        fullscreen=False,
        text_select=True,
        confirm_close=True,
    )
    
    # 启动应用
    webview.start(
        debug=False,
        http_server=False,
        gui='edgechromium' if sys.platform == 'win32' else 'gtk'
    )

if __name__ == '__main__':
    # 检查build目录是否存在
    build_dir = os.path.join(os.path.dirname(__file__), 'build')
    if not os.path.exists(build_dir):
        print("Error: build directory not found!")
        print("Please run 'npm run build' first to build the React app.")
        sys.exit(1)
    
    create_window()

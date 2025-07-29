#!/usr/bin/env python3
"""
Quick deployment script for local network sharing
Run this script to start your Panel dashboard on your local network
"""

import subprocess
import socket
import sys
import os

def get_local_ip():
    """Get the local IP address of the machine"""
    try:
        # Connect to a remote address to determine local IP
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        return local_ip
    except Exception:
        return "127.0.0.1"

def main():
    print("🚀 Panel Air Quality Dashboard - Local Deployment")
    print("=" * 50)
    
    # Check if the dashboard file exists
    if not os.path.exists("panel_air_quality_dashboard.py"):
        print("❌ Error: panel_air_quality_dashboard.py not found!")
        print("Make sure you're in the correct directory.")
        sys.exit(1)
    
    # Check if the database exists
    if not os.path.exists("air_quality.sqlite"):
        print("❌ Error: air_quality.sqlite not found!")
        print("Make sure your database file is in the current directory.")
        sys.exit(1)
    
    local_ip = get_local_ip()
    port = 5006
    
    print(f"📍 Local IP Address: {local_ip}")
    print(f"🌐 Dashboard will be available at: http://{local_ip}:{port}/panel_air_quality_dashboard")
    print(f"🔗 Local access: http://localhost:{port}/panel_air_quality_dashboard")
    print("\n📋 Instructions for sharing:")
    print("1. Share the URL above with others on your network")
    print("2. They can access the dashboard from any device on the same WiFi/network")
    print("3. Press Ctrl+C to stop the server")
    print("\n" + "=" * 50)
    
    try:
        # Start the Panel server
        cmd = [
            "panel", "serve", 
            "panel_air_quality_dashboard.py",
            "--address", "0.0.0.0",
            "--port", str(port),
            "--allow-websocket-origin=*"
        ]
        
        print("🚀 Starting Panel server...")
        subprocess.run(cmd)
        
    except KeyboardInterrupt:
        print("\n\n🛑 Server stopped by user")
    except FileNotFoundError:
        print("❌ Error: 'panel' command not found!")
        print("Please install Panel: pip install panel")
    except Exception as e:
        print(f"❌ Error starting server: {e}")

if __name__ == "__main__":
    main() 
#!/usr/bin/env python3
"""
Script to push dashboard files to existing GitHub repository
Repository: https://github.com/rishika84/panel_air_quality_dashboard.git
"""

import os
import subprocess
import sys

def check_git():
    """Check if git is installed"""
    try:
        subprocess.run(["git", "--version"], check=True, capture_output=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False

def check_files():
    """Check if required files exist"""
    required_files = [
        "panel_air_quality_dashboard.py",
        "air_quality.sqlite", 
        "requirements.txt",
        "render.yaml"
    ]
    
    missing_files = []
    for file in required_files:
        if not os.path.exists(file):
            missing_files.append(file)
    
    return missing_files

def setup_repository():
    """Set up git repository and push to existing repo"""
    repo_url = "https://github.com/rishika84/panel_air_quality_dashboard.git"
    
    try:
        print("🔧 Setting up Git repository...")
        
        # Initialize git
        subprocess.run(["git", "init"], check=True)
        print("✅ Git initialized")
        
        # Add remote
        subprocess.run(["git", "remote", "add", "origin", repo_url], check=True)
        print("✅ Remote added")
        
        # Add all files
        subprocess.run(["git", "add", "."], check=True)
        print("✅ Files added to git")
        
        # Commit
        subprocess.run(["git", "commit", "-m", "Initial dashboard deployment"], check=True)
        print("✅ Files committed")
        
        # Set main branch
        subprocess.run(["git", "branch", "-M", "main"], check=True)
        print("✅ Set main branch")
        
        # Push
        subprocess.run(["git", "push", "-u", "origin", "main"], check=True)
        print("✅ Files pushed to GitHub")
        
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Git error: {e}")
        return False

def render_deployment_instructions():
    """Provide Render deployment instructions"""
    print("\n" + "="*60)
    print("🚀 RENDER.COM DEPLOYMENT INSTRUCTIONS")
    print("="*60)
    
    print("\n1️⃣ GO TO RENDER.COM:")
    print("   • Open: https://render.com")
    print("   • Sign up with your GitHub account email")
    
    print("\n2️⃣ CREATE WEB SERVICE:")
    print("   • Click 'New +' → 'Web Service'")
    print("   • Choose 'Build and deploy from a Git repository'")
    print("   • Connect your GitHub account")
    print("   • Select repository: 'rishika84/panel_air_quality_dashboard'")
    
    print("\n3️⃣ CONFIGURE SERVICE:")
    print("   • Name: 'air-quality-dashboard'")
    print("   • Environment: 'Python 3'")
    print("   • Build Command: 'pip install -r requirements.txt'")
    print("   • Start Command: 'panel serve panel_air_quality_dashboard.py --address 0.0.0.0 --port $PORT --allow-websocket-origin=*'")
    print("   • Plan: Free")
    
    print("\n4️⃣ DEPLOY:")
    print("   • Click 'Create Web Service'")
    print("   • Wait for build to complete")
    print("   • Your dashboard will be available at the provided URL")

def main():
    print("🚀 Panel Air Quality Dashboard - Push to Existing Repository")
    print("="*60)
    print("Repository: https://github.com/rishika84/panel_air_quality_dashboard.git")
    print("="*60)
    
    # Check git installation
    if not check_git():
        print("❌ Git is not installed. Please install Git first:")
        print("   • Windows: https://git-scm.com/download/win")
        print("   • Mac: brew install git")
        print("   • Linux: sudo apt-get install git")
        sys.exit(1)
    
    print("✅ Git is installed")
    
    # Check required files
    missing_files = check_files()
    if missing_files:
        print(f"❌ Missing required files: {', '.join(missing_files)}")
        print("Make sure all files are in the current directory")
        sys.exit(1)
    
    print("✅ All required files found")
    
    # Setup and push to repository
    if setup_repository():
        print("\n🎉 Files pushed to repository successfully!")
        print("📁 Repository: https://github.com/rishika84/panel_air_quality_dashboard")
        
        # Provide Render instructions
        render_deployment_instructions()
        
        print("\n" + "="*60)
        print("🎯 NEXT STEPS:")
        print("1. Follow the Render.com instructions above")
        print("2. Your dashboard will be deployed automatically")
        print("3. Share the provided URL with others")
        print("="*60)
        
        # Ask if user wants to open Render.com
        open_render = input("\n🌐 Open Render.com in browser? (y/n): ").lower()
        if open_render == 'y':
            import webbrowser
            webbrowser.open("https://render.com")
    
    else:
        print("❌ Failed to push to repository. Please check your Git credentials.")
        print("💡 Make sure you're logged into Git with the correct account:")
        print("   git config --global user.name 'Your Name'")
        print("   git config --global user.email 'your-email@example.com'")

if __name__ == "__main__":
    main() 
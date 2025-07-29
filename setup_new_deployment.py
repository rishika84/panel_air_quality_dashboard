#!/usr/bin/env python3
"""
Setup script for deploying to Render.com with a new GitHub account
This script helps you create a new repository and prepare for deployment
"""

import os
import subprocess
import sys
import webbrowser

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

def create_new_repo_instructions():
    """Provide instructions for creating a new GitHub repository"""
    print("\n" + "="*60)
    print("📋 STEP-BY-STEP INSTRUCTIONS FOR NEW GITHUB ACCOUNT")
    print("="*60)
    
    print("\n1️⃣ CREATE NEW GITHUB ACCOUNT:")
    print("   • Go to: https://github.com/signup")
    print("   • Use a different email address")
    print("   • Choose a username (e.g., 'air-quality-dashboard')")
    print("   • Complete the signup process")
    
    print("\n2️⃣ CREATE NEW REPOSITORY:")
    print("   • Login to your new GitHub account")
    print("   • Click the '+' icon → 'New repository'")
    print("   • Repository name: 'air-quality-dashboard'")
    print("   • Make it PRIVATE (recommended)")
    print("   • Don't initialize with README (we'll push our files)")
    print("   • Click 'Create repository'")
    
    print("\n3️⃣ GET REPOSITORY URL:")
    print("   • Copy the repository URL (looks like: https://github.com/YOUR_USERNAME/air-quality-dashboard.git)")
    
    return input("\n📝 Enter the repository URL: ").strip()

def setup_git_repo(repo_url):
    """Set up git repository and push files"""
    try:
        print("\n🔧 Setting up Git repository...")
        
        # Initialize git
        subprocess.run(["git", "init"], check=True)
        print("✅ Git initialized")
        
        # Add all files
        subprocess.run(["git", "add", "."], check=True)
        print("✅ Files added to git")
        
        # Commit
        subprocess.run(["git", "commit", "-m", "Initial dashboard deployment"], check=True)
        print("✅ Files committed")
        
        # Set main branch
        subprocess.run(["git", "branch", "-M", "main"], check=True)
        print("✅ Set main branch")
        
        # Add remote
        subprocess.run(["git", "remote", "add", "origin", repo_url], check=True)
        print("✅ Remote added")
        
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
    print("   • Sign up with the same email as your new GitHub account")
    
    print("\n2️⃣ CREATE WEB SERVICE:")
    print("   • Click 'New +' → 'Web Service'")
    print("   • Choose 'Build and deploy from a Git repository'")
    print("   • Connect your GitHub account")
    print("   • Select your 'air-quality-dashboard' repository")
    
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
    print("🚀 Panel Air Quality Dashboard - Render Deployment Setup")
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
    
    # Get repository URL
    repo_url = create_new_repo_instructions()
    
    if not repo_url:
        print("❌ No repository URL provided")
        sys.exit(1)
    
    # Setup git repository
    if setup_git_repo(repo_url):
        print("\n🎉 Repository setup completed successfully!")
        
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
            webbrowser.open("https://render.com")
    
    else:
        print("❌ Failed to setup repository. Please try again.")

if __name__ == "__main__":
    main() 
#!/usr/bin/env python3
"""
Setup script for the Enhanced Attio Skill
"""

import os
import sys
from pathlib import Path


def check_prerequisites():
    """Check if prerequisites are met"""
    print("Checking prerequisites...")
    
    # Check Python version
    if sys.version_info < (3, 7):
        print("❌ Python 3.7 or higher is required")
        return False
    
    print("✅ Python version is sufficient")
    return True


def install_dependencies():
    """Install required dependencies"""
    print("Installing dependencies...")
    
    try:
        import subprocess
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'])
        print("✅ Dependencies installed successfully")
        return True
    except Exception as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False


def create_env_file():
    """Create a sample .env file if it doesn't exist"""
    env_file = Path('.env')
    
    if not env_file.exists():
        print("Creating sample .env file...")
        env_content = """# Attio API Configuration
ATTIO_API_KEY=your_api_key_here
ATTIO_WORKSPACE_ID=your_workspace_id_here
"""
        env_file.write_text(env_content)
        print("✅ Created sample .env file")
        print("💡 Remember to add your actual credentials to the .env file")
    else:
        print("✅ .env file already exists")


def verify_credentials():
    """Verify that credentials are set"""
    api_key = os.getenv('ATTIO_API_KEY')
    workspace_id = os.getenv('ATTIO_WORKSPACE_ID')
    
    if not api_key or api_key == 'your_api_key_here':
        print("⚠️  ATTIO_API_KEY is not set or is using the placeholder value")
        print("   Please set your actual API key in the .env file and source it")
    else:
        print("✅ ATTIO_API_KEY is set")
    
    if not workspace_id or workspace_id == 'your_workspace_id_here':
        print("⚠️  ATTIO_WORKSPACE_ID is not set or is using the placeholder value")
        print("   Please set your actual workspace ID in the .env file and source it")
    else:
        print("✅ ATTIO_WORKSPACE_ID is set")
    
    return bool(api_key and workspace_id and 
                api_key != 'your_api_key_here' and 
                workspace_id != 'your_workspace_id_here')


def main():
    """Main setup function"""
    print("🚀 Setting up Enhanced Attio Skill...")
    print()
    
    # Check prerequisites
    if not check_prerequisites():
        return False
    
    print()
    
    # Install dependencies
    if not install_dependencies():
        return False
    
    print()
    
    # Create env file
    create_env_file()
    
    print()
    
    # Verify credentials
    creds_ok = verify_credentials()
    
    print()
    
    if creds_ok:
        print("✅ Enhanced Attio Skill setup completed successfully!")
        print()
        print("📋 Next steps:")
        print("   1. Review the README.md for usage instructions")
        print("   2. Run the example scripts in the examples/ directory")
        print("   3. Customize the configuration as needed")
    else:
        print("⚠️  Setup completed with warnings. Please configure your credentials.")
        print("   Run: source .env (or set the environment variables manually)")
    
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
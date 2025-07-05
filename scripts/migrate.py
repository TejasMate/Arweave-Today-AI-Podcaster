#!/usr/bin/env python3
"""
Migration script for transitioning from old to new project structure.

This script helps users migrate from the monolithic podcast_generator.py
to the new modular structure.
"""

import os
import shutil
from pathlib import Path


def migrate_project():
    """
    Migrate project from old structure to new modular structure.
    """
    print("🔄 Starting project structure migration...")
    
    # Check if we're in the right directory
    if not os.path.exists("src/podcast_generator.py"):
        print("❌ Migration script must be run from project root")
        print("❌ Old src/podcast_generator.py not found")
        return False
    
    if os.path.exists("arweave_podcaster"):
        print("✅ New structure already exists, migration not needed")
        return True
    
    try:
        # Create backup of old structure
        backup_dir = "backup_old_structure"
        if not os.path.exists(backup_dir):
            print("📦 Creating backup of old structure...")
            os.makedirs(backup_dir)
            shutil.copytree("src", os.path.join(backup_dir, "src"))
            print(f"✅ Backup created at {backup_dir}/")
        
        # The new structure files should already be created by the restructuring
        if not os.path.exists("arweave_podcaster"):
            print("❌ New structure not found. Please ensure the restructuring was completed.")
            return False
        
        # Update .gitignore if it exists
        update_gitignore()
        
        # Create migration completion marker
        with open(".migration_completed", "w") as f:
            f.write("Migration from monolithic to modular structure completed\n")
        
        print("\n" + "="*60)
        print("✅ MIGRATION COMPLETED SUCCESSFULLY!")
        print("="*60)
        print("📁 Old structure backed up to: backup_old_structure/")
        print("🎯 New structure ready at: arweave_podcaster/")
        print("🚀 Run with: python main.py")
        print("📚 See docs/ for updated documentation")
        print("="*60)
        
        return True
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        return False


def update_gitignore():
    """Update .gitignore with new patterns."""
    gitignore_path = ".gitignore"
    new_patterns = [
        "",
        "# Migration backup",
        "backup_old_structure/",
        ".migration_completed",
        "",
        "# Python package",
        "build/",
        "dist/",
        "*.egg-info/",
        "",
        "# Development",
        ".mypy_cache/",
        ".pytest_cache/",
        ".coverage",
        "htmlcov/",
    ]
    
    if os.path.exists(gitignore_path):
        with open(gitignore_path, "r") as f:
            content = f.read()
        
        # Check if migration patterns already exist
        if "backup_old_structure/" not in content:
            with open(gitignore_path, "a") as f:
                f.write("\n".join(new_patterns))
            print("📝 Updated .gitignore with new patterns")
    else:
        with open(gitignore_path, "w") as f:
            f.write("\n".join([
                "# Environment",
                ".env",
                "venv/",
                "__pycache__/",
                "*.pyc",
                "",
                "# Output files",
                "output/",
                "*.wav",
                "*.mp3",
            ] + new_patterns))
        print("📝 Created .gitignore with recommended patterns")


def show_usage_examples():
    """Show examples of how to use the new structure."""
    print("\n" + "="*60)
    print("📚 USAGE EXAMPLES")
    print("="*60)
    
    print("\n1. 🎯 Command Line Usage:")
    print("   python main.py")
    print("   # OR")
    print("   python -m arweave_podcaster.core.podcast_generator")
    
    print("\n2. 📦 Python Package Usage:")
    print("   from arweave_podcaster import PodcastGenerator")
    print("   generator = PodcastGenerator('/path/to/project')")
    print("   success = generator.generate_podcast('auto')")
    
    print("\n3. 🔧 Service Usage:")
    print("   from arweave_podcaster.services import GeminiService")
    print("   service = GeminiService('your-api-key')")
    print("   enhanced = service.generate_podcast_script(content, date)")
    
    print("\n4. 🛠️ Development Installation:")
    print("   pip install -e .")
    print("   pip install -e .[dev]  # Include dev dependencies")
    
    print("\n5. 🧪 Running Tests:")
    print("   pytest")
    print("   pytest --cov=arweave_podcaster")
    
    print("\n📖 See docs/ directory for complete documentation")
    print("="*60)


if __name__ == "__main__":
    print("🏗️  ARWEAVE PODCASTER - PROJECT MIGRATION")
    print("="*60)
    print("This script will migrate your project to the new modular structure")
    print("Your old files will be safely backed up")
    print()
    
    response = input("Continue with migration? [Y/n]: ").strip().lower()
    if response in ['', 'y', 'yes']:
        success = migrate_project()
        if success:
            show_usage_examples()
    else:
        print("🛑 Migration cancelled")

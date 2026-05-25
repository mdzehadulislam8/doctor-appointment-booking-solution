#!/usr/bin/env python
"""
DrSeba Healthcare Platform - Migrate from SQLite to MySQL
This script facilitates migration from SQLite to MySQL

Usage: python migrate_to_mysql.py
"""

import os
import sys
import django
from django.core.management import call_command

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'drseba.settings')

def migrate_to_mysql():
    """
    Guide user through migrating from SQLite to MySQL
    """
    print("="*70)
    print("DrSeba Healthcare Platform - SQLite to MySQL Migration")
    print("="*70)
    print()
    
    print("⚠️  IMPORTANT: Before proceeding, ensure:")
    print("   1. MySQL server is installed and running")
    print("   2. You have the MySQL root password")
    print("   3. You want to replace the current database")
    print()
    
    proceed = input("Do you want to migrate to MySQL? (yes/no): ").strip().lower()
    if proceed != 'yes':
        print("Migration cancelled.")
        return False
    
    print()
    print("Step 1: Setting up MySQL database and user...")
    print("   This will create the database and user if they don't exist")
    
    # Import here to avoid issues if script is run without Django setup
    try:
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        from setup_mysql import create_mysql_database
        
        # Note: create_mysql_database() in interactive mode would ask for password
        print()
        print("   Running MySQL setup script...")
        print("   (You may be prompted for MySQL root password)")
        print()
        
        # Try to create database
        success = create_mysql_database()
        if not success:
            print()
            print("❌ MySQL setup failed. Please:")
            print("   1. Set up MySQL root password")
            print("   2. Run: python setup_mysql.py")
            print("   3. Then update .env with MySQL configuration")
            return False
            
    except ImportError:
        print("❌ Could not import setup_mysql.py")
        return False
    
    print()
    print("Step 2: Updating .env file...")
    
    # Update .env file
    env_file = '.env'
    if os.path.exists(env_file):
        with open(env_file, 'r') as f:
            content = f.read()
        
        # Replace SQLite with MySQL config
        content = content.replace(
            'DB_ENGINE=django.db.backends.sqlite3',
            'DB_ENGINE=django.db.backends.mysql'
        )
        
        # Uncomment MySQL settings if commented
        content = content.replace('# DB_NAME=drseba_healthcare', 'DB_NAME=drseba_healthcare')
        content = content.replace('# DB_USER=drseba_user', 'DB_USER=drseba_user')
        content = content.replace('# DB_PASSWORD=DrsebaPwd123!@#', 'DB_PASSWORD=DrsebaPwd123!@#')
        content = content.replace('# DB_HOST=localhost', 'DB_HOST=localhost')
        content = content.replace('# DB_PORT=3306', 'DB_PORT=3306')
        
        with open(env_file, 'w') as f:
            f.write(content)
        
        print("   ✅ .env file updated")
    else:
        print("   ⚠️  .env file not found. Create it with MySQL configuration.")
        return False
    
    print()
    print("Step 3: Setting up Django...")
    django.setup()
    
    print()
    print("Step 4: Running migrations...")
    try:
        call_command('migrate', verbosity=1)
        print("   ✅ Migrations completed")
    except Exception as e:
        print(f"   ❌ Migration failed: {e}")
        return False
    
    print()
    print("Step 5: Loading demo data...")
    try:
        # Import model setup
        from django.db import connection
        cursor = connection.cursor()
        
        # Check if appointments table has data
        cursor.execute("SELECT COUNT(*) FROM appointments_appointment")
        count = cursor.fetchone()[0]
        
        if count == 0:
            print("   Loading sample data...")
            import setup_demo_data
            print("   ✅ Demo data loaded")
        else:
            print(f"   ℹ️  Database already has {count} appointments")
            
    except Exception as e:
        print(f"   ⚠️  Could not load demo data: {e}")
    
    print()
    print("="*70)
    print("✅ MIGRATION COMPLETED SUCCESSFULLY!")
    print("="*70)
    print()
    print("Your application is now using MySQL!")
    print()
    print("Next steps:")
    print("1. Start the server: python manage.py runserver")
    print("2. Access admin panel: http://127.0.0.1:8000/admin/")
    print("3. Access application: http://127.0.0.1:8000/")
    print()
    print("Database Details:")
    print("   Database Name: drseba_healthcare")
    print("   User: drseba_user")
    print("   Host: localhost:3306")
    print()
    
    return True

if __name__ == '__main__':
    try:
        success = migrate_to_mysql()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n❌ Migration cancelled by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error during migration: {e}")
        sys.exit(1)

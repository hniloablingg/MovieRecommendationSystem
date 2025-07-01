#!/usr/bin/env python3
"""
CSV-Based Movie Recommendation System Setup
No database required - works entirely with CSV files
"""

import subprocess
import sys
import os
import time
from pathlib import Path

def print_banner():
    print("""
🎬 =========================================== 🎬
    MOVIE RECOMMENDATION SYSTEM SETUP
    (CSV-Only - No Database Required)
🎬 =========================================== 🎬
    """)

def check_python_version():
    """Kiểm tra phiên bản Python"""
    print("🔍 Checking Python version...")
    if sys.version_info < (3, 7):
        print("❌ Python 3.7+ is required!")
        sys.exit(1)
    print(f"✅ Python {sys.version.split()[0]} - OK")

def install_requirements():
    """Cài đặt dependencies"""
    print("\n📦 Installing dependencies...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Dependencies installed successfully!")
    except subprocess.CalledProcessError:
        print("❌ Failed to install dependencies!")
        sys.exit(1)

def check_csv_data():
    """Kiểm tra CSV data files"""
    print("\n📊 Checking CSV data files...")
    required_files = [
        "model/data/movies.csv",
        "model/data/users.csv", 
        "model/data/ratings.csv",
        "model/data/tags.csv"
    ]
    
    missing_files = []
    for file_path in required_files:
        if not os.path.exists(file_path):
            missing_files.append(file_path)
    
    if missing_files:
        print("❌ Missing CSV files:")
        for file in missing_files:
            print(f"   - {file}")
        return False
    else:
        print("✅ All CSV data files found!")
        return True

def train_model():
    """Train collaborative filtering model"""
    print("\n🤖 Training recommendation model...")
    try:
        os.chdir("model")
        subprocess.check_call([sys.executable, "train.py"])
        os.chdir("..")
        
        # Check if model file was created
        if os.path.exists("model/cf_model.pkl"):
            print("✅ Model trained successfully!")
            return True
        else:
            print("❌ Model file not found!")
            return False
    except Exception as e:
        print(f"❌ Model training failed: {e}")
        os.chdir("..")
        return False

def start_backend():
    """Start CSV-based Flask backend server"""
    print("\n🚀 Starting CSV-based backend server...")
    try:
        print("✅ Backend starting at http://127.0.0.1:5000")
        print("💡 Press Ctrl+C to stop the server")
        print("🌐 Open frontend/index.html in browser for UI")
        print("-" * 50)
        
        # Start CSV backend server
        subprocess.run([sys.executable, "csv_backend.py"])
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
    except Exception as e:
        print(f"❌ Failed to start backend: {e}")

def open_frontend():
    """Open frontend in browser"""
    frontend_path = Path("frontend/index.html").resolve()
    if frontend_path.exists():
        print(f"\n🌐 Frontend available at: file://{frontend_path}")
        try:
            import webbrowser
            webbrowser.open(f"file://{frontend_path}")
        except:
            pass
    else:
        print("❌ Frontend file not found!")

def show_api_examples():
    """Show API usage examples"""
    print("""
📚 API EXAMPLES FOR POSTMAN:

1️⃣ RATE A MOVIE:
POST http://127.0.0.1:5000/ratings/rate
{
  "userId": "1",
  "movieId": "444", 
  "rating": "5.0"
}

2️⃣ GET RECOMMENDATIONS:
GET http://127.0.0.1:5000/recommendations/1

3️⃣ ADD COMMENT:
POST http://127.0.0.1:5000/comments/add
{
  "userId": 1,
  "movieId": 444,
  "content": "Great movie!"
}

4️⃣ SHARE MOVIE:
POST http://127.0.0.1:5000/shares/share
{
  "userId": 1,
  "movieId": 444,
  "platform": "facebook"
}

5️⃣ GET ALL MOVIES:
GET http://127.0.0.1:5000/movies/

6️⃣ GET MOVIE COMMENTS:
GET http://127.0.0.1:5000/comments/movie/444

7️⃣ GET POPULAR SHARED MOVIES:
GET http://127.0.0.1:5000/shares/popular

8️⃣ HEALTH CHECK:
GET http://127.0.0.1:5000/health
""")

def main():
    """Main setup function"""
    print_banner()
    
    # Step 1: Check Python version
    check_python_version()
    
    # Step 2: Install dependencies
    install_requirements()
    
    # Step 3: Check CSV data files
    csv_ok = check_csv_data()
    if not csv_ok:
        print("❌ Please ensure all CSV files are present!")
        sys.exit(1)
    
    # Step 4: Train model
    model_ok = train_model()
    
    if not model_ok:
        print("\n⚠️  Model training failed, but you can still test APIs")
        print("🔧 Try running manually: cd model && python train.py")
    
    # Step 5: Show information
    show_api_examples()
    
    # Step 6: Ask user what to do next
    print("\n" + "="*60)
    print("🎯 SETUP COMPLETE! What would you like to do?")
    print("1. Start CSV Backend Server (recommended)")
    print("2. Open Frontend in Browser") 
    print("3. Show API Examples")
    print("4. Exit")
    
    while True:
        choice = input("\nEnter your choice (1-4): ").strip()
        
        if choice == "1":
            start_backend()
            break
        elif choice == "2":
            open_frontend()
            break
        elif choice == "3":
            show_api_examples()
        elif choice == "4":
            print("👋 Goodbye!")
            break
        else:
            print("❌ Invalid choice! Please enter 1-4")

if __name__ == "__main__":
    main() 
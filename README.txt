PERSONALITY TEST PORTAL - QUICK START

What this app does
- Student portal with 60 questions
- Immediate personality result after submission
- Admin login and dashboard
- Stores every submission in SQLite database
- Export all submissions to CSV

Default admin login
- Username: admin
- Password: admin123

How to run on Windows
1. Open Command Prompt in the project folder.
2. Create virtual environment:
   python -m venv venv
3. Activate it:
   venv\Scripts\activate
4. Install packages:
   pip install -r requirements.txt
5. Run the app:
   python app.py
6. Open browser:
   http://127.0.0.1:5000

Student portal
- http://127.0.0.1:5000/

Admin portal
- http://127.0.0.1:5000/admin/login

If python is not recognized
- Try: py app.py
- Or install Python and check "Add Python to PATH"

To change admin password
- Replace the default password logic in app.py with your own environment variable or new hash.
- You can also ask ChatGPT to update this project for secure multi-admin login.

Suggested next upgrade
- Host on Render / PythonAnywhere / VPS
- Add Excel export with filters
- Add charts by course / department / batch
- Add student duplicate-check by email or student ID
- Add password reset and role-based admin users

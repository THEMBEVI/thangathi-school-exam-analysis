THANGATHI SCHOOL

Run locally:
1. Install Python 3.11+.
2. pip install -r requirements.txt
3. Set ADMIN_PASSWORD and SECRET_KEY.
4. python app.py
5. Open http://127.0.0.1:5000

Default login if no environment variables are set:
Username: admin
Password: ChangeMe123!

For internet access, deploy to a Python/HTTPS host and set:
ADMIN_USERNAME
ADMIN_PASSWORD
SECRET_KEY

This starter version uses SQLite. For a larger multi-user school system, PostgreSQL is recommended.

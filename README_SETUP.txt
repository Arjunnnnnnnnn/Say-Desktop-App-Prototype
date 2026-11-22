SAY DESKTOP - SETUP

1. Put these files in your desktop folder:
   main.py
   database.py
   authentication.py
   email_verification.py
   themes.py

2. Your project structure can look like:
   Say/
     desktop/
       main.py
       database.py
       authentication.py
       email_verification.py
       themes.py

3. Install Python 3.10+ and make sure Tkinter is installed.
   Tkinter and SQLite are included with most standard Python installations.

4. Configure email in VS Code PowerShell before running.
   Use a dedicated Gmail account for development, enable Google's
   two-step verification, and create an App Password if your Google
   account supports it.

   $env:SAY_EMAIL_ADDRESS="your-development-address@gmail.com"
   $env:SAY_EMAIL_APP_PASSWORD="your-google-app-password"

   Do not put these credentials in source code or upload them to GitHub.
   These environment variables apply only to the current terminal session.

5. From the desktop folder, run:
   python main.py

DATABASE NOTE
The SQLite file is created at the project root as say_local.db.
The verification code database is created in the desktop folder.

FEATURE SCOPE
- Unique case-insensitive Say IDs enforced by SQLite UNIQUE constraint.
- Local user search by Say ID.
- Local chat request send/accept/decline.
- Local accepted-conversation records.
- Light and dark themes.
- Gmail SMTP verification when credentials are configured.

IMPORTANT LIMITATIONS
This is a local desktop prototype. Separate computers do not yet communicate.
It does not yet send chat messages, synchronize accounts online, or implement
end-to-end encryption. Those require a secure backend and a reviewed E2EE
design before any public launch. Do not use real users' data for this prototype.

VIDEO GAME LIBRARY - EXECUTION INSTRUCTIONS

This application uses a client-server architecture and requires two separate terminals (or command prompts) to run simultaneously.

PREREQUISITES:
1. Ensure the Python environment (.venv) is activated in both terminals.
2. Ensure you are executing the commands from the root directory of the project (the VideoGameLibrary folder).

STEP 1: START THE BACKEND SERVER (Terminal 1)
This terminal must remain open and running.

    python3 backend/server.py

STEP 2: START THE FRONTEND GUI (Terminal 2)
After the server shows "Running on http://127.0.0.1:5000", run the client in the second terminal.

    python3 frontend/gui_app.py

The graphical application window will then open and be populated with data
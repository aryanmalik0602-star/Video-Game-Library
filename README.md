# Video Game Library Project

A client-server application for managing and searching your video game library with a graphical interface.

## 🌐 Live Website

View the project website here: **[Video Game Library](https://yourusername.github.io/VideoGameLibrary/)**

*(Replace `yourusername` with your actual GitHub username)*

## 📋 Project Structure

```
VideoGameLibrary/
├── index.html              # Main website landing page
├── project_summary.html    # Project summary page
├── backend/
│   ├── __init__.py
│   └── server.py          # Flask backend server
├── frontend/
│   ├── __init__.py
│   └── gui_app.py         # GUI application
├── data/
│   ├── library_data.json
│   └── video_games.csv
└── tests/
    └── test_project.py
```

## 🚀 Getting Started

### Prerequisites
- Python 3.x
- Virtual environment (.venv)

### Running the Application

This application uses a **client-server architecture** and requires two separate terminals.

#### Terminal 1: Start the Backend Server
```bash
python3 backend/server.py
```

#### Terminal 2: Start the Frontend GUI
After the server shows "Running on http://127.0.0.1:5000", run:
```bash
python3 frontend/gui_app.py
```

The graphical application window will then open with data populated from your library.

### API Usage

Search the database from CLI:
```bash
curl http://127.0.0.1:5000/media/search/Batman | python3 -m json.tool
```

## 📚 Features

- Browse your video game collection
- Search games by title
- View game details
- Manage your library

## 🔧 GitHub Pages Setup

To make your website visible on GitHub:

1. **Go to your repository settings** on GitHub
2. **Navigate to "Pages"** (in the left sidebar)
3. **Select branch**: Choose `main` (or your default branch)
4. **Select folder**: Choose `/root` (the root of the repository)
5. **Save** - GitHub will build and deploy your site

Your site will be available at: `https://<your-username>.github.io/VideoGameLibrary/`

## 📝 License

This project is open source.

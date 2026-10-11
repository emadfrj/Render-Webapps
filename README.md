# Daymark task app

A small, dependency-free web app with a Python standard-library backend and a CSV file for storage.

## Run it

From this folder, run:

```bash
python server.py
```

Then open <http://127.0.0.1:8000> in your browser. Tasks and completion state are saved in `tasks.csv`.

## Files

- `server.py` — serves the page and provides the task API.
- `tasks.csv` — starter data and persistent storage.
- `static/index.html` — page structure.
- `static/styles.css` — responsive styling.
- `static/app.js` — browser interactions.

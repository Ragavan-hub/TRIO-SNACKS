# Quick Start Guide

## Step 1: Install Python Dependencies

Open PowerShell or Command Prompt in this directory and run:

```bash
pip install -r requirements.txt
```

**Note:** If you get permission errors, use:
```bash
pip install --user -r requirements.txt
```

## Step 2: Run the Application

Simply run:
```bash
python app.py
```

Or double-click `run.bat` (Windows) if available.

## Step 3: Access the Application

Open your web browser and go to:
```
http://localhost:5000
```

## Step 4: Login

Use these default credentials:

- **Admin Login:**
  - Username: `admin`
  - Password: `admin123`

- **Cashier Login:**
  - Username: `cashier`
  - Password: `cashier123`

## Troubleshooting

### If Python is not found:
- Make sure Python 3.7+ is installed
- Check: `python --version` or `python3 --version`
- Download from: https://www.python.org/downloads/

### If pip is not found:
- Try: `python -m pip install -r requirements.txt`
- Or: `python3 -m pip install -r requirements.txt`

### If port 5000 is already in use:
- Edit `app.py` and change the last line to:
  ```python
  app.run(debug=True, port=5001)
  ```

### Database will be created automatically
- The database file (`database.db`)) will be created automatically on first run
- No manual database setup needed!


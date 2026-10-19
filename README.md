# ClassAct — Python + Streamlit + SQLite

A Streamlit web app for student records and grading, using SQLite to persist data.

## Requirements
- Python 3.10 or newer
- pip

## Run on Windows
1. Extract this ZIP file.
2. Open Command Prompt or PowerShell in the extracted `ClassAct_Streamlit` folder.
3. Install packages:
   ```bash
   py -m pip install -r requirements.txt
   ```
4. Start the app:
   ```bash
   py -m streamlit run app.py
   ```
5. Streamlit will open a local browser tab. If it does not, visit http://localhost:8501.

On macOS/Linux, use `python3 -m pip install -r requirements.txt` and `python3 -m streamlit run app.py`.

## Database
- SQLite database is created automatically as `classact.db` next to `app.py`.
- Student details, subjects, grade bands, and grades persist between sessions.
- Sample records are inserted only when the database has no students.
- Reports can be exported to CSV.

## Notes
- This is a local single-user starter project; it does not include authentication, cloud hosting, multi-user permissions, or automatic backups.
- The starter grading bands were interpreted from the supplied screenshot. Verify official grade boundaries with your school before relying on them.

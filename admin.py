from flask import Flask, request, redirect, url_for, render_template
import sqlite3
import os
import uuid


DB_PATH = "files.db"
FILES_DIR = ""
ALLOWED_EXTENSIONS = None  

app = Flask(__name__, template_folder='html')

def allowed_file(filename):
    if ALLOWED_EXTENSIONS is None:
        return True
    return '.' in filename and filename.rsplit('.',1)[1].lower() in ALLOWED_EXTENSIONS

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS files (
                    uuid TEXT PRIMARY KEY,
                    filename TEXT NOT NULL,
                    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )""")
    conn.commit()
    conn.close()

def add_file_mapping(filename):
    file_uuid = str(uuid.uuid4())
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("INSERT INTO files (uuid, filename) VALUES (?, ?)", (file_uuid, filename))
    conn.commit()
    conn.close()
    return file_uuid

def delete_file(uuid_val):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT filename FROM files WHERE uuid=?", (uuid_val,))
    row = c.fetchone()
    if row:
        filepath = os.path.join(FILES_DIR, row[0])
        if os.path.exists(filepath):
            os.remove(filepath)
        c.execute("DELETE FROM files WHERE uuid=?", (uuid_val,))
        conn.commit()
    conn.close()

def list_files():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT uuid, filename, uploaded_at FROM files ORDER BY uploaded_at DESC")
    rows = c.fetchall()
    conn.close()
    return rows

@app.route("/", methods=["GET"])
def index():
    files = list_files()
    return render_template("index.html", files=files)

@app.route("/upload", methods=["POST"])
def upload():
    if 'file' not in request.files:
        return "No file part", 400
    file = request.files['file']
    if file.filename == '':
        return "No selected file", 400
    if not ALLOWED_EXTENSIONS or '.' in file.filename:
        filepath = os.path.join(FILES_DIR, file.filename)
        file.save(filepath)
        add_file_mapping(file.filename)
    return redirect(url_for('index'))

@app.route("/delete", methods=["POST"])
def delete():
    uuid_val = request.form.get("uuid")
    if uuid_val:
        delete_file(uuid_val)
    return redirect(url_for('index'))

if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5001)

from flask import Flask, send_from_directory, abort
import sqlite3
import os

DB_PATH = "files.db"   
FILES_DIR = ""         

app = Flask(__name__)

def get_filename(uuid):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT filename FROM files WHERE uuid = ?", (uuid,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return row[0]
    return None

@app.route("/files/<uuid>")
def download_file(uuid):
    print("requested uuid " + uuid)
    filename = get_filename(uuid)
    if not filename:
        abort(404)
    print("found file " + filename)
    return send_from_directory(FILES_DIR, filename, as_attachment=True)
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

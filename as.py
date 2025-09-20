from flask import Flask, render_template, request, send_from_directory, redirect, url_for
import os
from werkzeug.utils import secure_filename
from tqdm import tqdm
import zipfile
import shutil

UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 1024 * 1024 * 1024  # 1GB limit

# Homepage: List files/folders and upload form
@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        # Handle file upload
        uploaded_files = request.files.getlist("file")
        for f in uploaded_files:
            filename = secure_filename(f.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            f.save(filepath)
            # If ZIP, extract folder
            if zipfile.is_zipfile(filepath):
                with zipfile.ZipFile(filepath, 'r') as zip_ref:
                    zip_ref.extractall(os.path.join(app.config['UPLOAD_FOLDER'], filename+"_folder"))
                os.remove(filepath)
        return redirect(url_for('index'))

    # List files/folders
    items = os.listdir(app.config['UPLOAD_FOLDER'])
    return render_template("index.html", items=items)

# Download files or folders
@app.route("/download/<name>")
def download(name):
    path = os.path.join(app.config['UPLOAD_FOLDER'], name)
    if os.path.isdir(path):
        # Zip folder before sending
        zip_path = path + ".zip"
        shutil.make_archive(path, 'zip', path)
        path = zip_path
        name = os.path.basename(zip_path)

    filesize = os.path.getsize(path)
    chunk_size = 1024
    # Server-side progress
    with open(path, "rb") as f, tqdm(total=filesize, unit="B", unit_scale=True, desc=f"Sending {name}") as pbar:
        while f.read(chunk_size):
            pbar.update(chunk_size)

    return send_from_directory(app.config['UPLOAD_FOLDER'], os.path.basename(path), as_attachment=True)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)

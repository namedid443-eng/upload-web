from flask import Flask, render_template, request, redirect, send_from_directory, url_for, abort
from werkzeug.utils import secure_filename
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

ALLOWED_EXT = set(["mp4","webm","ogg","png","jpg","jpeg","gif","pdf","txt","xlsx","xls","csv"])

def allowed(filename):
    if "." not in filename:
        return False
    ext = filename.rsplit(".",1)[1].lower()
    return ext in ALLOWED_EXT

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["MAX_CONTENT_LENGTH"] = 1024 * 1024 * 1024  # 1GB max for uploads on Render (adjust if needed)

@app.route("/", methods=["GET","POST"])
def index():
    message = ""
    if request.method == "POST":
        if "file" not in request.files:
            message = "No file part in request."
        else:
            f = request.files["file"]
            if f.filename == "":
                message = "No selected file."
            else:
                filename = secure_filename(f.filename)
                if not allowed(filename):
                    message = "File type not allowed."
                else:
                    save_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
                    f.save(save_path)
                    message = "Upload successful."
                    return redirect(url_for("index"))
    files = sorted(os.listdir(app.config["UPLOAD_FOLDER"]))
    # Build file info list with type
    file_infos = []
    for fn in files:
        path = os.path.join(app.config["UPLOAD_FOLDER"], fn)
        is_video = fn.rsplit(".",1)[1].lower() in ("mp4","webm","ogg")
        file_infos.append({"name":fn, "is_video":is_video})
    return render_template("index.html", files=file_infos, message=message)

@app.route("/uploads/<path:filename>")
def uploaded_file(filename):
    safe = secure_filename(filename)
    full = os.path.join(app.config["UPLOAD_FOLDER"], safe)
    if not os.path.exists(full):
        abort(404)
    return send_from_directory(app.config["UPLOAD_FOLDER"], safe, as_attachment=True)

@app.route("/play/<path:filename>")
def play_file(filename):
    safe = secure_filename(filename)
    full = os.path.join(app.config["UPLOAD_FOLDER"], safe)
    if not os.path.exists(full):
        abort(404)
    # serve inline (not attachment) so the browser can play it
    return send_from_directory(app.config["UPLOAD_FOLDER"], safe, as_attachment=False)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

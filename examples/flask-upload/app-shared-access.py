import atexit
from flask import Flask, request, redirect, url_for, render_template_string, send_file
import cshelve
import io
from werkzeug.utils import secure_filename
import sys


app = Flask(__name__)

# Note: A single instance of CShelve can be shared among multiple users of the application,
# allowing concurrent access to the same database for storing and retrieving files.
if len(sys.argv) > 1:
    db = cshelve.open(sys.argv[1])  # Open the CShelve database using the provided path.
else:
    # By default, use the development database.
    db = cshelve.open("dev.ini")  # Open the default CShelve database.

# Ensure the database is closed properly when the application exits.
def close_db():
    try:
        db.close()
    except Exception:
        pass


atexit.register(close_db)

HTML = """
<!doctype html>
<title>CShelve Flask Image Upload</title>
<h1>Upload new Image</h1>
<form method=post enctype=multipart/form-data>
  <input type=file name=file>
  <input type=submit value=Upload>
</form>
<h2>Uploaded Images</h2>
<ul>
  {% for key in images %}
    <li>
      <a href="{{ url_for('get_image', key=key) }}" target="_blank">{{ key }}</a>
      <img src="{{ url_for('get_image', key=key) }}" height="100"/>
    </li>
  {% endfor %}
</ul>
"""


@app.route("/", methods=["GET", "POST"])
def upload_file():
    if request.method == "POST":
        file = request.files.get("file")
        if file and file.filename:
            filename = secure_filename(file.filename)
            data = file.read()
            mimetype = file.content_type
            # Save the file's mimetype and data with the filename as the key.
            db[filename] = mimetype, data
        return redirect(url_for("upload_file"))
    # Retrieve the list of uploaded files from the CShelve database.
    images = list(db.keys())
    return render_template_string(HTML, images=images)


@app.route("/image/<key>")
def get_image(key):
    # Retrieve the file data from the CShelve database using the key.
    data = db.get(key)
    if not data:
        return "Image not found", 404
    mimetype, data = data
    # Serve the file data as an image.
    return send_file(io.BytesIO(data), mimetype=mimetype)


if __name__ == "__main__":
    app.run(debug=True)

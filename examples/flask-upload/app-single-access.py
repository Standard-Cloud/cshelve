from flask import Flask, request, redirect, url_for, render_template_string, send_file
import cshelve  # CShelve is used to store and retrieve uploaded files in a cloud-compatible dictionary-like storage.
import io
from werkzeug.utils import secure_filename
import sys


app = Flask(__name__)


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
            # Store the uploaded file in the CShelve database.
            with cshelve.open(app.config["DB_PATH"]) as db:
                # Save the file's mimetype and data with the filename as the key.
                db[filename] = mimetype, data
        return redirect(url_for("upload_file"))
    # Retrieve the list of uploaded files from the CShelve database.
    with cshelve.open(app.config["DB_PATH"]) as db:
        images = list(db.keys())
    return render_template_string(HTML, images=images)


@app.route("/image/<key>")
def get_image(key):
    # Retrieve the file data from the CShelve database using the key.
    with cshelve.open(app.config["DB_PATH"]) as db:
        data = db.get(key)
        if not data:
            return "Image not found", 404
        mimetype, data = data
        # Serve the file data as an image.
        return send_file(io.BytesIO(data), mimetype=mimetype)


if __name__ == "__main__":
    # Set DB_PATH in Flask config
    if len(sys.argv) > 1:
        # Use the database path provided as a command-line argument.
        app.config["DB_PATH"] = sys.argv[1]
    else:
        # By default, use the development database.
        app.config["DB_PATH"] = "dev.ini"

    app.run(debug=True)

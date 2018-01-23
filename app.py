from flask import Flask, request, redirect, url_for, render_template
import os
import json
import glob
import sys
from uuid import uuid4
import carlookup

app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/upload", methods=["POST"])
def upload():
    """Handle the upload of a file."""
    form = request.form

    # Create a unique "session ID" for this particular batch of uploads.
    upload_key = str(uuid4())

    # Is the upload using Ajax, or a direct POST by the form?
    is_ajax = False
    if form.get("__ajax", None) == "true":
        is_ajax = True

    # Target folder for these uploads.
    target = "static/uploads/{}".format(upload_key)
    try:
        os.mkdir(target)
    except  Exception as e:
        print("LOL", e)
        if is_ajax:
            return ajax_response(False, "Couldn't create upload directory: {}".format(target))
        else:
            return "Couldn't create upload directory: {}".format(target)

    print("=== Form Data ===")
    for key, value in list(form.items()):
        print(key, "=>", value)

    for upload in request.files.getlist("car"):
        filename = upload.filename.rsplit("/")[0]
        destination = "/".join([target, filename])
        print("accept incoming file:", filename)
        print("save it to:", destination)
        upload.save(destination)

    for upload in request.files.getlist("file"):
        filename = upload.filename.rsplit("/")[0]
        destination = "/".join([target, filename])
        print("accept incoming file:", filename)
        print("save it to:", destination)
        upload.save(destination)


    if is_ajax:
        return ajax_response(True, upload_key)
    else:
        return redirect(url_for("upload_complete", uuid=upload_key))


@app.route("/files/<uuid>")
def upload_complete(uuid):
    """The location we send them to at the end of the upload."""

    # Get their files.
    root = "static/uploads/{}".format(uuid)
    if not os.path.isdir(root):
        return "Error: UUID not found!"

    files = []
    jsonfile = None
    carfile = None
    car_results = None
    json_results = None
    for file in glob.glob("{}/*.*".format(root)):
        fname = file.split(os.sep)[-1]
        ext = os.path.splitext(fname)[1]
        files.append(fname)

        if ext == "json":
            jsonfile = fname
        elif ext in [".jpg", ".jpeg", ".bmp", ".gif", ".png", ".svg", ".psd", ".raw"]:
            carfile = fname

    if carfile is not None or jsonfile is not None:
        car_results = carlookup.search("http://d1arsn5g9mfrlq.cloudfront.net/sites/default/files/resize/remote/b16f3f72fbbe9aac21e8723dd85d2a32-720x471.jpg")
        timeline = ""


    return render_template("files.html",
        uuid=uuid,
        car_results = car_results,
        timeline = json_results
    )


def ajax_response(status, msg):
    status_code = "ok" if status else "error"
    return json.dumps(dict(
        status=status_code,
        msg=msg,
    ))

if __name__ == '__main__':
    flask_options = dict(
        host='0.0.0.0',
        debug=True,
        port=8000,
        threaded=True,
    )

    app.run(**flask_options)

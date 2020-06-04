import os
from surveyapp import dropzone, mongo
from flask import Flask, render_template, url_for, request, Blueprint
from flask_login import login_required


graphs = Blueprint("graphs", __name__)

@graphs.route('/import', methods=['GET', 'POST'])
# login required decorator prevents people accessing the page when not logged in
@login_required
def import_file():
    if request.method == "POST":
        f = request.files.get('file')
        f.save(os.path.join('app/uploads', f.filename))
    return render_template("import.html", title = "Import file")

import os
import secrets
from surveyapp import mongo
from flask import Flask, current_app
from flask_login import current_user
from bson.objectid import ObjectId
# For converting image base 64 data URI
import urllib.parse

# Saves a graph image file to the server. Called after user saves a graph (which automatically
# uploads an image of their graph so that it can be displayed on a card)
def save_image(data, graph_id):
    graph = mongo.db.graphs.find_one({"_id": ObjectId(graph_id)})
    if graph:
        delete_image(graph["image"])
    response = urllib.request.urlopen(data)
    # generate a random hex for the filename
    random_hex = secrets.token_hex(8)
    file_name = random_hex + ".png"
    file = os.path.join(current_app.root_path, "static/images/graphimages", file_name)
    with open(file, 'wb') as image_to_write:
        image_to_write.write(response.file.read())
    return file_name

def delete_image(name):
    image = os.path.join(current_app.root_path, "static/images/graphimages", name)
    os.remove(image)

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

#
# # Saves new graph, else if already exists it updates the existing one
# def save_graph(title, survey_id, graph_id, x_variable, y_variable, y_aggregation):
#     graph = mongo.db.graphs.find_one({"_id":ObjectId(graph_id)})
#     if not graph:
#         mongo.db.graphs.insert_one({\
#         "title" : title,\
#         "user" : current_user._id,\
#         "column" : column,\
#         "surveyId": survey_id})
#     else:
#         mongo.db.graphs.update_one({"_id": ObjectId(graph_id)}, {"$set": {"title": title}})

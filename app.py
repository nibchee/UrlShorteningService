from flask import Flask, render_template, request, jsonify, redirect
from pymongo import MongoClient
from random import choice
import string
from pymongo.server_api import ServerApi

uri = "mongodb+srv://nirbhaybansal28:lNRSyGCesgCI8Nk0@cluster0.vtmadwq.mongodb.net/?retryWrites=true&appName=Cluster0"
client = MongoClient(uri, server_api=ServerApi("1"))

#Code to Confirm Connectivity with Mongo DB
try:
    client.admin.command("ping")
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)

db = client.dsparta

app = Flask(__name__)
#######################################################################################################################

#Algorithm to Generate Short Url 
def generate_short_id(num_of_chars: int):
    return "".join(
        choice(string.ascii_letters + string.digits) for _ in range(num_of_chars)
    )

#Home Page 
@app.route("/", methods=["GET"])
def home():
    return render_template("index.html")

#API  to fetch all Urls
@app.route("/urls", methods=["GET"])
def getUrls():
    print("Calling getUrls() Function")
    urls = list(db.urls.find())
    print(urls)
    final_urls = []
    for url in urls:
        obj = {
            "name": url["name"],
            "shortUrl": url["shortUrl"],
            "shortId": url["short_id"],
        }
        final_urls.append(obj)
    return jsonify({"urls": final_urls});

#API to Create short Url & save in Database
@app.route("/createShortUrl", methods=["POST"])
def createShortUrl():
    print("Calling create Short Url Function")
    url = request.form["url"]
    name = request.form["webSiteName"]
    print("WebSite Name " + name + "Long url is " + url)
    short_id = generate_short_id(8)
    short_url = "http://127.0.0.1:5000/" + short_id
    urlObject = {
        "original_url": url,
        "shortUrl": short_url,
        "short_id": short_id,
        "name": name,
    }
    db.urls.insert_one(urlObject)
    print(short_url)
    return jsonify({"short_url": short_url, "msg": "Sucessfully Created!"})

#API to hit shortUrl & redirect to Original Url
@app.route("/<short_id>")
def redirect_url(short_id):
    print("Short Id is " + short_id)
    if short_id == "favicon.ico":
        return render_template("index.html")
    urls = db.urls.find({"short_id": short_id})
    url = ""
    for link in urls:
        url = link
        break
    print(url["original_url"])
    return redirect(url["original_url"])

#API to delete Url
@app.route("/deleteUrl", methods=["POST"])
def delete_Url():
    print("Delete Url Function")
    shortId = request.form["shortId"]
    print("Url with short Id " + shortId + " going to delete")
    db.urls.delete_one({"short_id": shortId})
    return jsonify({"msg": "Sucessfully Deleted!"})

#API to Update Url
@app.route("/updateUrl", methods=["POST"])
def update_Url():
    print("Update Url Function")
    shortId = request.form["shortId"]
    short_url = "http://127.0.0.1:5000/" + shortId
    name = request.form["webSiteName"]
    url = request.form["url"]
    db.urls.update_one(
        {"short_id": shortId}, {"$set": {"original_url": url, "name": name}}
    )
    print("Url with short Id " + shortId + " going to Update")
    return jsonify({"short_url": short_url, "msg": "Sucessfully Updated!"})

#API to Fetch Original Url with shortId is input
@app.route("/getOriginalUrl", methods=["POST"])
def getOriginalUrl():
    print("Get Original Url Function")
    short_id = request.form["shortId"]
    print("Short Id is " + short_id)
    urls = db.urls.find({"short_id": short_id})
    url = ""
    for link in urls:
        url = link
        break
    print(url["original_url"])
    return jsonify({"originalUrl": url["original_url"]})


if __name__ == "__main__":
    app.run("0.0.0.0", port=5000, debug=True)

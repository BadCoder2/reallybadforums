from flask import Flask, request, redirect
from markupsafe import escape
import random, time, json, os
#from https://github.com/KnugiHK/flask-hcaptcha
from flask_hcaptcha import hCaptcha

app = Flask(__name__)
hcaptcha = hCaptcha(app)

def readFile(fileName):
    with open("pages/" + fileName, "r") as f:
        return f.read()
def fixInput(inpt):
    return inpt.replace(r'\n', r'<br>').replace(r'\b', r'<b>').replace(r'\e', r'</b>')

@app.route("/")
def hello_world():
    return readFile("home.html")

@app.errorhandler(404)
def page_not_found(error):
    rslt = readFile("404.html")
    return rslt, 404

@app.route("/create")
def createPage():
    return readFile("create.html")
@app.route("/formatting")
def formatg():
    return readFile("formatguide.html")

@app.route("/hoffmanmemestuff")
def SQuest1():
    return readFile("hofmemstu.html")
@app.route("/amogus")
def SQuest2():
    return readFile("amogus.html")
@app.route("/__nothing__")
def SQuest3():
    return readFile("nothingtoseehere.html")


@app.route("/make_forum_post", methods = ["POST"])
def make_post():
    if not hcaptcha.verify():
        return "Verification Failure"
    inpt = str(escape(request.form["thing"]))
    if len(inpt) > 3000:
        return "INPUT TOO LARGE- IGNORED"
    with open("takenStuff.json", 'r') as fil:
        contents = fil.read()
        takenPagesJSON = json.loads(contents)
        takenPages = takenPagesJSON["takenPages"]
    curTime = str(time.time())
    random.seed(curTime)
    while True:
        num = str(random.randint(1124,391413))
        if int(num) in takenPages:
            continue
        else:
            break
    takenPages.append(num)
    takenPagesJSON["takenPages"] = takenPages
    postLocate = ("pages/posts/" + num + ".html")
    with open("takenStuff.json", 'w') as fil:
        json.dump(takenPagesJSON, fil, sort_keys=True, indent=4)
    newInpt = fixInput(inpt)
    with open(postLocate, "w") as post:
        post.write("<body>"+newInpt+"</body>")
    output = str(newInpt) + "<br><b>ID: " + num + "</b>"
    return output

@app.route("/view_post", methods = ["POST"])
def view_post():
    iD = request.form["thing2"]
    try:
        int(iD)
    except:
        return "INVALID ID"
    return redirect('forum/'+iD)

@app.route("/view_rand_post", methods = ["POST"])
def view_rand_post():
    random.seed = time.time()
    with open("takenStuff.json", 'r') as fil:
        contents = fil.read()
        takenPagesJSON = json.loads(contents)
        availablePages = takenPagesJSON["takenPages"]
    selection = random.choice(availablePages)
    return redirect('forum/'+selection)

@app.route("/forum/<int:formID>")
def show_post(formID):
    try:
        with open("pages/posts/" + str(formID) + ".html", "r") as f:
            post = f.read()
        return post
    except:
        return page_not_found("sussy baka")

@app.route("/moderation")
def moderate():
    try:
        modToken = request.cookies.get("MOD_TOKEN")
    except:
        return "NO MODERATION COOKIE FOUND"
    if modToken != os.getenv("MOD_SECRET"):
        with open("logs.txt", "a") as log:
            log.write(time.strftime('%l:%M,%b %d')+" WARN: ATTEMPTED MOD ACCESS WITH COOKIE "+modToken)
        return "INCORRECT COOKIE-LOGGED"
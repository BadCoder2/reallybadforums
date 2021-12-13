from flask import Flask, request, redirect, make_response
from markupsafe import escape
import random, json, os, requests, datetime
#yes yes i know, importing too much. i wonder if i could do something like:
#from os import environ
#possibly in the future

app = Flask(__name__)

def readFile(fileName):
    with open("pages/" + fileName, "r") as f:
        return f.read()
def fixInput(inpt):
    return inpt.replace(r'\n', r'<br>').replace(r'\b', r'<b>').replace(r'\e', r'</b>')
def checkCaptcha(res):
    url = 'https://hcaptcha.com/siteverify'
    sKey = os.environ['SKEY']
    obj = {'secret':sKey,'response':res}
    x = requests.post(url,data=obj)
    xJson = x.json()
    result = str(xJson['success'])
    if not result or result.lower() == "false":
        print("FAILED - ERROR CODE:")
        print(xJson["error-codes"])
    print("CAPTCHA RESULT: " + result)
    return result

@app.route("/")
def home():
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

@app.route('/favicon.ico')
def favicon():
    return app.send_static_file('favicon.ico')
@app.route("/make_forum_post", methods = ["POST"])
def make_post():
    cRslt = checkCaptcha(request.form['h-captcha-response'])
    if not cRslt or str(cRslt).lower() == "false":
        return "Invalid hCaptcha response returned <br>If this wasn't caused by you, it has been logged and will be addressed"
    inpt = str(escape(request.form["thing"]))
    if len(inpt) > 3000:
        return "INPUT TOO LARGE- IGNORED"
    with open("takenStuff.json", 'r') as fil:
        contents = fil.read()
        takenPagesJSON = json.loads(contents)
        takenPages = takenPagesJSON["takenPages"]
    while True:
        num = str(random.randint(1124,391413))
        if int(num) in takenPages:
            print("woah! we got a dupe in the randint!! das cool")
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
        brugh = int(iD)
    except:
        return "INVALID ID"
    return redirect('forum/'+str(brugh))

@app.route("/view_rand_post", methods = ["POST"])
def view_rand_post():
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

@app.route("/set-cookie")
def setLCprep():
    return readFile("setCookie.html")
@app.route("/set-cookie-post", methods = ["POST"])
def setLC():
    cTSn = request.form["cookieName"]
    cTSc = request.form["cookieContent"]
    resp = make_response("Cookie Set")
    expire_date = datetime.datetime.now()
    expire_date = expire_date + datetime.timedelta(days=180)
    resp.set_cookie(cTSn, cTSc, expire_date)
    return resp
@app.route("/moderation")
def moderate():
    try:
        modToken = request.cookies.get("MOD_TOKEN")
    except:
        return readFile("404.html")
    if modToken is None:
        return readFile("404.html")
    elif modToken != os.environ['MOD_SECRET']:
        print("\033[93mWARN: ATTEMPTED MOD ACCESS WITH COOKIE "+modToken+"\033[0m")
        return "Incorrect cookie."
    elif modToken == os.environ['MOD_SECRET']:
        return readFile("mods.html")
    else:
        print("how did we get here")
        return readFile("404.html")
@app.route("/moderation/mod-del", methods = ["POST"])
def deletePost():
    #this takes a LOT of the code from make_post(), so don't forget to keep the code pieces synced if possible 
    mS = os.environ['why']
    if request.form["pswd"] != mS:
        return "Bad Mod Password"
    delID = request.form["delID"]
    print("Deleting ID "+delID)
    with open("takenStuff.json", 'r') as fil:
        takenPagesJSON = json.load(fil)
        takenPages = takenPagesJSON["takenPages"]
    if delID in takenPages:
        #fix takenPages, because search for a random post is reliant on it
        takenPages.remove(delID)
        takenPagesJSON["takenPages"] = takenPages
        with open("takenStuff.json", 'w') as fil:
            json.dump(takenPagesJSON, fil, sort_keys=True, indent=4)
        #now actually delete the file from replit
        #i know this code sucks but honestly idc bc this should filter any stray spaces right? idk
        os.remove(f"pages/posts/{str(delID)}.html")
        print("Deleted successfully.")
        return f"Successfully deleted post ID {delID}."
    else:
        return f"ID {delID} NOT FOUND"

if __name__ == "__main__":
    app.run(ssl_context='adhoc')
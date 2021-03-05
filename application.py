import os

from cs50 import SQL
from flask import Flask, flash, jsonify, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash
import datetime

from helpers import login_required, apology, unpunctuate

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///linkit.db")

# Make sure API key is set
if not os.environ.get("API_KEY"):
    raise RuntimeError("API_KEY not set")


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = :username",
                          username=request.form.get("username")) #!!

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]
        session["succeeded"] = "false"
        session["deletionid"] = "none"

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Ensure password confirmation was submitted
        elif not request.form.get("confirmation"):
            return apology("password does not match", 403)

        # Ensure password is same as confirmation
        elif request.form.get("password") != request.form.get("confirmation"):
            return apology("passwords do not match", 403)

        username = request.form.get("username")

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = :username",
                          username=username)

        # Ensure username is not already taken
        if len(rows) != 0:
            return apology("that username is already taken", 406)

        # Hash the password
        hashedpw = generate_password_hash(request.form.get("password"))

        # Insert user into user table
        db.execute("INSERT INTO users (username, hash) VALUES (?, ?);",
                   username, hashedpw)

        # Insert user into friends table
        user_id = db.execute("SELECT id FROM users WHERE username=?;", username)
        db.execute("INSERT INTO friends (user_id, username) VALUES (?, ?);", user_id[0]["id"], username)

        return redirect("/login")

    else:
        return render_template("register.html")


@app.route("/logout")
@login_required
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/")
def index():
    latestposts = db.execute("SELECT id, user_id, link, description, date, tags FROM posts ORDER BY id DESC LIMIT 10;")

    # Increment views on those posts
    viewids = []
    for row in latestposts:
        if session:
            if row["user_id"] != session["user_id"]:
                viewids.append(row["id"])
        else:
            viewids.append(row["id"])

    db.execute("UPDATE posts SET views = views + 1 WHERE id IN (?);", viewids)

    return render_template("index.html", latestposts=latestposts)


@app.route("/search", methods=["GET", "POST"])
def search():
    if request.method == "GET":
        return render_template("search.html")
    else:
        descriptions = db.execute("SELECT id, user_id, link, description, date, tags FROM posts;")
        keywords = request.form.get("searchtag")
        keywords = keywords.lower()
        keywords = unpunctuate(keywords)
        keywordslist = keywords.split(",")

        idlist = []
        # Check tags for key words
        for row in descriptions:
            tags = row["tags"]
            if tags:
                tagslist = tags.split("#")

                def checktags(tagslist, keywordslist):
                    for phrase in keywordslist:
                        for tag in tagslist:
                            if phrase in tag:
                                idlist.append(row)
                                return
                checktags(tagslist, keywordslist)

        # Check links for key words
        for row in descriptions:
            for phrase in keywordslist:
                match = (row["link"]).find(phrase)
                if match != -1:
                    if row not in idlist:
                        idlist.append(row)
                        break

        # Check descriptions for key words
        for row in descriptions:
            description = row["description"]
            if description:
                description = unpunctuate(description)
            for phrase in keywordslist:
                match = description.find(phrase)
                if match != -1:
                    if row not in idlist:
                        idlist.append(row)
                        break

        # Increment views on those posts and add spaces between tags
        viewids = []
        for row in idlist:
            if row["tags"]:
                row["tags"] = row["tags"].replace("#", " #")
            if session:
                if row["user_id"] != session["user_id"]:
                    viewids.append(row["id"])
            else:
                viewids.append(row["id"])

        db.execute("UPDATE posts SET views = views + 1 WHERE id IN (?);", viewids)

        return render_template("result.html", tabinfo=idlist)


@app.route("/history")
@login_required
def history():
    post_history = db.execute("SELECT id, link, description, date, time, tags, views FROM posts WHERE user_id=? ORDER BY id DESC;", session["user_id"])
    if not post_history:
        return render_template("history.html", history=0)
    if session["succeeded"] == "true":
        session["succeeded"] = "false"
        return render_template("history.html", history=post_history, success="true")
    return render_template("history.html", history=post_history)


@app.route("/post", methods=["GET", "POST"])
@login_required
def post():
    if request.method == "GET":
        return render_template("post.html")
    else:
        if not request.form.get("link"):
            return apology("Please enter link", 400)

        linkname = request.form.get("link")
        linkname = linkname.replace("https://", "")
        description = request.form.get("description")
        tags = request.form.get("tags")
        if tags:
            tagsstring = tags.replace(" ", "")
            tagsstring = tagsstring.replace(",", "")

        time_data = datetime.datetime.now()
        datestr = time_data.strftime("%m/%d/%Y")
        timestr = time_data.strftime("%H:%M:%S")

        # Insert post into db
        success = db.execute("INSERT INTO posts (user_id, link, description, date, time, tags) VALUES (?, ?, ?, ?, ?, ?);", session["user_id"], linkname, description, datestr, timestr, tagsstring)
        if not success:
            return apology("Post failed", 500)
        session["succeeded"] = "true"
        return redirect("/history")
    return apology("sorry", 500)


@app.route("/tagclick", methods=["GET", "POST"])
def tagclick():
    try:
        inputtagname = request.form["tagname"]
        inputtagname = inputtagname.replace("#", "").replace(" ", "").lower()
    except:
        return apology("sorry", 500)
    descriptions = db.execute("SELECT id, user_id, link, description, date, tags FROM posts;")

    idlist = []
    # Check tags for key words
    for row in descriptions:
        alltags = row["tags"]
        if alltags:
            alltagslist = alltags.split("#")
            for searchtag in alltagslist:
                if inputtagname in searchtag.lower():
                    idlist.append(row)
                    break

        # Increment views on those posts and add spaces between tags
        viewids = []
        for row in idlist:
            if row["tags"]:
                row["tags"] = row["tags"].replace("#", " #")
            if session:
                if row["user_id"] != session["user_id"]:
                    viewids.append(row["id"])
            else:
                viewids.append(row["id"])

        db.execute("UPDATE posts SET views = views + 1 WHERE id IN (?);", viewids)

    return render_template("result.html", tabinfo=idlist)


@app.route("/deletion", methods=["GET", "POST"])
@login_required
def deletion():
    if request.method == "POST":
        # Store the id of the post to be deleted in session
        session["deletionid"] = request.form["delete"]

        return render_template("deletion.html")

    return apology("you're not supposed to be here", 400)


@app.route("/confirmdelete", methods=["GET", "POST"])
@login_required
def confirmdelete():
    if request.method == "POST":
        if request.form["confirm"] == "yes":
            deletion_id = session["deletionid"]
            if deletion_id == 'none' or deletion_id == '':
                return apology("bad request", 400)
            if int(deletion_id) <= 0:
                return apology("bad request", 400)

            # Delete row with the id
            success = db.execute("DELETE FROM posts WHERE id=?;", deletion_id)
            if not success:
                return apology("not success", 500)

            session["deletionid"] = "none"
            session["succeeded"] = "true"

        elif request.form["confirm"] == "no":
            session["deletionid"] = "none"

        return redirect("/history")

    return apology("you're not supposed to be here", 400)


@app.route("/seefriends", methods=["GET", "POST"])
@login_required
def seefriends():
    if request.method == "GET":
        friendusernames = db.execute("SELECT friends FROM friends WHERE user_id = ?;", session["user_id"])

        # If the user does not have any friends
        if not friendusernames[0]["friends"]:
            return render_template("friends.html", friendslist="none")

        # Create list of current friends
        friendslist = (friendusernames[0]["friends"]).split(", ")

        return render_template("friends.html", friendslist=friendslist)
    else:
        return redirect("/addfriends")

    return apology("incomplete", 500)


@app.route("/addfriends", methods=["GET", "POST"])
@login_required
def addfriends():
    if request.method == "GET":
        return render_template("request.html")
    else:
        friend = request.form.get("friend_username")
        # Check if the requested user exists
        exists = db.execute("SELECT id FROM users WHERE username=?;", friend)
        if not exists:
            return render_template("requestsent.html", existance="false")

        # Add comma after the friend's username
        hasfriends = db.execute("SELECT requesting_friends FROM friends WHERE username=?;", friend)
        username = db.execute("SELECT username FROM users WHERE id=?;", session["user_id"])
        if not username[0]["username"]:
            return apology("???", 900) ##############################
        if not hasfriends[0]["requesting_friends"]:
            addfriend = username[0]["username"]

            db.execute("UPDATE friends SET requesting_friends=? WHERE username=?;", addfriend, friend)

        else:
            addfriend = ", " + username[0]["username"]

            # Check whether the request has been sent before
            if (username[0]["username"]) in (hasfriends[0]["requesting_friends"]):
                return render_template("requestsent.html", sent_already="true")

            # Check whether they're already friends
            existing_friends = db.execute("SELECT friends FROM friends WHERE user_id=?;", session["user_id"])
            if username[0]["username"] in existing_friends[0]["friends"]:
                return render_template("requestsent.html", already_friends="true")

            # Add friend request to the friend's table
            db.execute("UPDATE friends SET requesting_friends=requesting_friends || ? WHERE username=?;", addfriend, friend)

        return render_template("requestsent.html", already_friends="false", sent_already="false")

    return apology("incomplete", 500)


@app.route("/acceptfriends", methods=["GET", "POST"])
@login_required
def acceptfriends():
    if request.method == "GET":
        # Find list of potential friends
        requesting_friends = db.execute("SELECT requesting_friends FROM friends WHERE user_id=?;", session["user_id"])

        # Check if there are no requests
        if not requesting_friends[0]["requesting_friends"]:
            return render_template("friendrequests.html", friends="none")

        requesting_friends_list = (requesting_friends[0]["requesting_friends"]).split(", ")
        return render_template("friendrequests.html", friends = requesting_friends_list)

    else:
        # get response from user
        response = request.form["addfriend"]
        # see if they accepted or denied
        response = response.split("; ")
        if response[1] == "deny":
            # Update table of requesting friends and remove name
            requesting_friends = db.execute("SELECT requesting_friends FROM friends WHERE user_id=?;", session["user_id"])
            requesting_friends_list = (requesting_friends[0]["requesting_friends"]).split(", ")
            requesting_friends_list.remove(response[0])
            remaining_requests = ", ".join(requesting_friends_list)
            db.execute("UPDATE friends SET requesting_friends=? WHERE user_id=?;", remaining_requests, session["user_id"])

            return redirect("/acceptfriends")

        elif response[1] == "accept":
            # Update user's friends after checking if user already has any
            friends_exist = db.execute("SELECT friends FROM friends WHERE user_id=?;", session["user_id"])
            if not friends_exist[0]["friends"]:
                addfriend = response[0]
                db.execute("UPDATE friends SET friends = ? WHERE user_id=?;", addfriend, session["user_id"])
            else:
                addfriend = ", " + response[0]
                db.execute("UPDATE friends SET friends = friends || ? WHERE user_id=?;", addfriend, session["user_id"])

            # Update friend's friends after checking if he already has any
            friends_exist = db.execute("SELECT friends FROM friends WHERE username=?;", response[0])
            username = db.execute("SELECT username FROM users WHERE id=?;", session["user_id"])
            if not friends_exist[0]["friends"]:
                addfriend = username[0]["username"]
                db.execute("UPDATE friends SET friends = ? WHERE username=?;", addfriend, response[0])
            else:
                addfriend = ", " + username[0]["username"]
                db.execute("UPDATE friends SET friends = friends || ? WHERE username=?;", addfriend, response[0])

            # Remove name from requesting friends column
            requesting_friends = db.execute("SELECT requesting_friends FROM friends WHERE user_id=?;", session["user_id"])
            requesting_friends_list = (requesting_friends[0]["requesting_friends"]).split(", ")
            requesting_friends_list.remove(response[0])
            remaining_requests = ", ".join(requesting_friends_list)
            db.execute("UPDATE friends SET requesting_friends=? WHERE user_id=?;", remaining_requests, session["user_id"])

            return redirect("/acceptfriends")

    return apology("incomplete", 500)


@app.route("/friendshistory", methods=["GET", "POST"])
@login_required
def friendshistory():
    if request.method == "POST":
        # Get friend's name
        friendsname = request.form["seehistory"]

        # Get his history
        post_history = db.execute("SELECT id, link, description, date, time, tags, views FROM posts WHERE username=? ORDER BY id DESC;", friendsname)
        if not post_history:
            return render_template("history.html", history=0, friend=friendsname)

        return render_template("history.html", history=post_history, friend=friendsname)

    return apology("incomplete", 500)
import os
import datetime
import smtplib
import uuid
import random

from os.path import join, dirname, realpath
from cs50 import SQL
from flask import Flask, flash, jsonify, redirect, render_template, request, session, url_for
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename

from helpers import apology, login_required, allowed_file

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
db = SQL("sqlite:///thriftshare.db")

# From http://code.activestate.com/recipes/252531-storing-binary-data-in-sqlite/ --> this is to save images into our SQLite database
#class Blob:
#    """Automatically encode a binary string."""
#    def __init__(self, s):
#        self.s = s

#    def _quote(self):
#        return "'%s'" % sqlite.encode(self.s)

@app.route("/", methods=["GET"])
def index():
    """"Homepage"""
    return render_template("index.html")

@app.route("/about")
def about():
    """ Information about thriftshare"""
    return render_template("about.html")

# http://flask.pocoo.org/docs/0.12/patterns/fileuploads/
UPLOAD_FOLDER = join(dirname(realpath(__file__)), 'static/images/')

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route("/post", methods=["GET", "POST"])
@login_required
def post():
    """ Posts items for claim"""
    if request.method == "GET":
        return render_template("post.html")

    else:
        # Checks if user inputs item name
        if not request.form.get("item"):
            return apology("Please provide an item name", 400)

        name = request.form.get("item")
        description = request.form.get("description")
        # http://flask.pocoo.org/docs/0.12/patterns/fileuploads/
        if 'file' not in request.files:
            flash('No file part')
            return redirect("/post")
        file = request.files['file']
        print(file)
        # if user does not select file, browser also
        # submit a empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect("/post")
        if file and allowed_file(file.filename):
            filename = file.filename
            extension = filename.split(".")
            now = str(datetime.datetime.now())
            now = now.replace(" ", "")
            newfilename = now + "." + extension[1]
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], newfilename))

            # NEEDS FILE VALIDATION
            userid = session["user_id"]
            user = db.execute("SELECT * FROM users WHERE id = :userid", userid=userid)
            username = user[0]['username']

            # Inserts newly posted item into database, gives 1 ThrifToken to the user who posted
            db.execute("INSERT INTO posted (name, image, username, userid, description) VALUES (:name, :newfilename, :username, :userid, :description)", name=name, newfilename=newfilename, username=username, userid=userid, description=description)
            db.execute("UPDATE users SET currency= :currency WHERE id= :id", currency=user[0]["currency"]+1, id=userid)
            return redirect("/browse")


@app.route("/check", methods=["GET"])
def check():
    """Return true if username available, else false, in JSON format"""
    # Code provided by a CS50 TF
    username = request.args.get("username")
    email = request.args.get("email")
    results = db.execute("SELECT * FROM users WHERE username=:username",
                        username=username)

    if results or len(username) == 0:
        return jsonify(False)

    else:
        return jsonify(True)




@app.route("/checkpass", methods=["GET"])
def checkpass():
    """For javascript credential check"""
    username = request.args.get("username")
    password = request.args.get("password")

    if not username:
        return jsonify(False)

    # Ensure password was submitted
    elif not password:
        return jsonify(False)

    # Query database for username
    rows = db.execute("SELECT * FROM users WHERE username=:username", username=username)

    # Ensure username exists and password is correct
    if len(rows) != 1 or not check_password_hash(rows[0]["hash"], password):
        return jsonify(False)

    # Remember which user has logged in
    session["user_id"] = rows[0]["id"]

    # Redirect user to home page
    return jsonify(True)


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
                          username=request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        if rows[0]["verified"] == 0:
            return apology("Your account is not verified yet! Please check your email to verify this account", 403)
        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""

    # Forget any user_id
    session.clear()

    if request.method == "POST":
        """Register user"""
        username = request.form.get("username")
        email = request.form.get("email")

        # Checks if user input a username
        if not username:
            return apology("Missing username!", 400)

        # Checks for valid email and confirmation
        if not (email or request.form.get("econfirm")):
            return apology("Missing email!", 400)

        if not email == request.form.get("econfirm"):
            return apology("Your emails do not match", 400)

        if not request.form.get("pnumber"):
            return apology("Please insert your phone number")

        # Checks for matching passwords
        if not (request.form.get("password") or request.form.get("confirmation")):
            return apology("Missing password", 400)
        if not (request.form.get("password") == request.form.get("confirmation")):
            return apology("your passwords do not match", 400)

        # Checks if user inputs dorm and year
        if not (request.form.get("dorm") or request.form.get("year")):
            return apology("Please choose your dorm and year", 400)


        name = request.form.get("firstname") + " " + request.form.get("lastname")
        # Saves user info into database

        # Checks if username is already taken
        result = db.execute("SELECT * FROM users WHERE username= :username", username=username)
        if result:
            return apology("this username is already taken", 400)

        # Checks if email is already taken
        taken = db.execute("SELECT * FROM users WHERE email= :email", email=request.form.get("email"))
        if taken:
            return apology("this email is already in use", 400)

        # Generates a string of 3-9 numbers that serves as a verification code
        # Is not unique, but would be difficult to guess
        vcode = ""
        for x in range(3):
            vcode += str(random.randint(1,100)*3)

        db.execute("INSERT INTO users (username, hash, dorm, year, name, email, pnumber, vcode) VALUES (:username, :hashp, :dorm, :year, :name, :email, :pnumber, :vcode)",
                            username=username, hashp=generate_password_hash(request.form.get("password")), dorm=request.form.get("dorm"),
                            year=request.form.get("year"), name=name, email=request.form.get("email"), pnumber=request.form.get("pnumber"), vcode=vcode)
        # Saves user id into a session
        session["user_id"] = db.execute("SELECT id FROM users WHERE username= :username", username=username)

        # Sends user a verification email
        msg = "Hello! Thank you for registering for ThriftShare! Click the link below and use this verification code \'{0}\' to verify your account to begin sharing!\nhttp://ide50-juanmolina.cs50.io:8080/verify".format(vcode)

        # Below code taken from CS50 notes @ https://cs50.harvard.edu/2018/fall/weeks/7/notes/
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login("harvardthriftshare@gmail.com", "juanvanessa")
        server.sendmail("harvardthriftshare@gmail.com", request.form.get("email"), msg)
        server.quit()
        return redirect("/login")
    else:
        return render_template("register.html")

@app.route("/verify", methods=["GET", "POST"])
def verify():
    """ Verifies a user's email by sending a message to that email containing a code"""

    if request.method == "POST":
        # Updates database to verify user (identified by username as input)
        username= request.form.get("username")

        user=db.execute("SELECT * FROM users WHERE username= :username", username=username)

        # Checks for user input
        if not username:
            return apology("Please enter a username", 400)
        if not request.form.get("password"):
            return apology("Please enter a password", 403)
        if not request.form.get("vcode"):
            return apology ("Please enter a verification code", 400)

        # Checks if verification code matches one in database
        if user[0]["vcode"] == request.form.get("vcode"):
            db.execute("UPDATE users SET verified= :verified WHERE username= :username", verified=1, username=username)
            return redirect("/login")
        else:
            return apology("invalid verification code", 400)
    else:
        return render_template("verify.html")


def emailclaim(value):
    """ Sends email detailing information about a claimed item """

    item = db.execute("SELECT * FROM posted WHERE id= :id", id=value)
    buyer = db.execute("SELECT * FROM users WHERE id= :buyerid", buyerid=item[0]["buyerid"])
    seller = db.execute("SELECT * FROM users WHERE id= :userid", userid=item[0]["userid"])

    # Formats messages to send to buyer and seller after buyer claims an item
    sellermsg = ("Hi {0}! {1} requested to claim the item you posted \'{2}\'. Below is {3}\'s information. \n Please contact the claimant to arrange a drop off time and location for the item. Thank you!\n\n".format(seller[0]["name"], buyer[0]["name"], item[0]["name"], buyer[0]["name"]) +
                "Name -- {0}\nEmail -- {1}\nPhone number -- {2}\nDorm/House -- {3}\nYear -- {4}\nItem requested -- {5}".format(buyer[0]["name"], buyer[0]["email"], buyer[0]["pnumber"], buyer[0]["dorm"],  buyer[0]["year"], item[0]["name"]))
    buyermsg = ("Hi {0}! This email is confirming that you requested to claim the item \'{1}\'. Below is the owner\'s information. \n Please contact them to arrange a drop off time and location for the item. Thank you!\n\n".format(buyer[0]["name"], item[0]["name"]) +
                "Name -- {0}\nEmail -- {1}\nPhone number -- {2}\nDorm/House -- {3}\nYear -- {4}\nItem requested -- {5}.".format(seller[0]["name"], seller[0]["email"], seller[0]["pnumber"], seller[0]["dorm"],  seller[0]["year"], item[0]["name"]))

    # Sends email to recipients, code from https://cs50.harvard.edu/2018/fall/weeks/7/notes/
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login("harvardthriftshare@gmail.com", "juanvanessa")
    server.sendmail("harvardthriftshare@gmail.com", seller[0]["email"], sellermsg)
    server.sendmail("harvardthriftshare@gmail.com", buyer[0]["email"], buyermsg)
    server.quit()



@app.route("/browse", methods=["GET", "POST"])
@login_required
def browse():

    """ Browses through items """
    if request.method == "GET":
        # Supplies data for loop in browse.html
        rows = db.execute("SELECT * FROM posted WHERE avail= :avail", avail=1)
        return render_template("browse.html", rows=rows)
    else:
        user = db.execute("SELECT * FROM users WHERE id= :id", id=session["user_id"])
        currency = user[0]['currency']

        # Gets the ID of the item "claimed" from the form
        value = int(request.form.get("submit"))

        # Checks if user has enough ThrifTokens to make the claim, if so, subtracts one from their account
        if currency > 0:
            db.execute("UPDATE users SET currency= :currency WHERE id= :id", id=session["user_id"], currency=currency-1)
            db.execute("UPDATE posted SET avail= :avail, buyerid= :buyer, ptimestamp=CURRENT_TIMESTAMP WHERE id= :id", avail=0, buyer=session["user_id"], id=value)
            emailclaim(value)
            return redirect("/browse")
        else:
            return apology("You don't have any more ThrifTokens")


@app.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    """ Shows user their profile page """
    if request.method == "GET":
        # Shows the user all of their available posts and ThrifTokens
        user = db.execute("SELECT * FROM users WHERE id= :id", id=session["user_id"])
        posts = db.execute("SELECT * FROM posted WHERE userid= :userid AND avail= :avail", userid=session["user_id"], avail=1)
        active=""
        if not posts:
            active = "you currently have no active posts"
        return render_template("profile.html", posts=posts, user=user, active=active)
    else:
        # Removes post from browse, takes away credit earned from posting something
        value = int(request.form.get("submit"))
        user=db.execute("SELECT * FROM users WHERE id=:id", id=session["user_id"])

        db.execute("UPDATE posted SET avail= :avail WHERE id=:id", avail=0, id=value)
        db.execute("UPDATE users SET currency= :currency WHERE id= :id", currency=user[0]["currency"]-1, id=session["user_id"])
        return redirect("/profile")


@app.route("/history")
@login_required
def history():
    """Shows user all of their posting/claiming history, with date"""

    posts = db.execute("SELECT * FROM posted WHERE userid= :userid", userid=session["user_id"])
    claims = db.execute("SELECT * FROM posted WHERE buyerid= :user", user=session["user_id"])
    return render_template("history.html", posts=posts, claims=claims)

@app.route("/changepass", methods=["GET", "POST"])
@login_required
def changepass():
    """Changes password """

    if request.method == "GET":
        return render_template("changepass.html")
    else:
        # Checks if inputs exists and match
        if not (request.form.get("password") or request.form.get("newpassword") or request.form.get("confirmation")):
            return apology("Missing input", 400)
        if not request.form.get("newpassword") == request.form.get("confirmation"):
            return apology("your passwords do not match", 400)
        # Checks if the old password is correct
        oldpass = db.execute("SELECT hash FROM users WHERE id= :userid", userid=session["user_id"])
        if not check_password_hash(oldpass[0]["hash"], request.form.get("password")):
            return apology("Old password invalid!", 400)
        db.execute("UPDATE users SET hash = :hash WHERE id= :userid", hash=generate_password_hash(request.form.get("newpassword")),
                  userid=session["user_id"])
        return render_template("success.html")

@app.route("/forgot", methods=["GET", "POST"])
def forgot():
    """ Sends an email to the user if they forgot their username or password """

    if request.method == "GET":
        return render_template("forgot.html")
    else:
        # Checks if user input email
        email = request.form.get("email")
        if not email:
            return apology("Please enter a valid email address")
        # Checks for valid email
        user = db.execute("SELECT * FROM users WHERE email = :email", email=email)
        if not user:
            return apology("Email not found!", 400)

        # Formats message to be emailed to the user
        msg = ("Hello {0}! It seems like you forgot your ThriftShare account information!\n\nYour username is -- \'{1}\'.\n\n".format(user[0]["name"], user[0]["username"])
              + "If you forgot your password, click this link to reset it \nhttp://ide50-juanmolina.cs50.io:8080/resetpass")
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login("harvardthriftshare@gmail.com", "juanvanessa")
        server.sendmail("harvardthriftshare@gmail.com", email, msg)
        server.quit()
        return redirect("/login")


@app.route("/resetpass", methods=["GET", "POST"])
def resetpass():
    """Resets password if the user forgot and cannot login"""

    if request.method == "GET":
        return render_template("resetpass.html")
    else:
        # Checks if inputs exists and match
        if not (request.form.get("email") or request.form.get("username") or request.form.get("newpassword") or request.form.get("confirmation")):
            return apology("Missing input", 400)
        # Checks if user's email and username match to the same account
        input1 = db.execute("SELECT * FROM users WHERE username= :username AND email= :email", username=request.form.get("username"),
                            email= request.form.get("email"))
        if not input1:
            return apology("Account information invalid", 400)
        # Checks if the password inptus match
        if not request.form.get("newpassword") == request.form.get("confirmation"):
            return apology("your passwords do not match", 400)

        db.execute("UPDATE users SET hash = :hash WHERE id= :userid", hash=generate_password_hash(request.form.get("newpassword")),
                  userid=input1[0]["id"])
        return render_template("success.html")



def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)

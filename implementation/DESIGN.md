To create our web application, ThriftShare, we used a combination of mainly Python, HTML, and SQL.  We used the structure of CS50 Finance as a
base for our python code and the HTML layout.  Our platform requires users to create an account and login to use this application.

The “/” route is the route that is accessed by going to the homepage of ThriftShare, http://ide50-juanmolina.cs50.io:8080/.  Upon GET
requesting the “/” route, the python code renders the “index.html” template.  On “index.html” a user that has not yet logged in can access four
separate routes: Register, Log In, About, and Forgot Username/Password.

Clicking the link for the ‘Register,’ GET requests the “/register” route, calling the register function which renders the template
“register.html.”  The user can then provide his or her registration information via a POST request.  When the request method is POST, the
register function requests the values for “username” and “email” from the form, storing these in variables (because they are used throughout
the function).  Then, the function checks that the user has filled in every field (this is also checked on the front-end with ‘required’ in all
of the input tags on “register.html”).  If the email and password match their respective confirmation fields, the function checks that the
username and/or email do not already exist in the users table of the thriftshare.db database using SELECT in SQL in the db.execute() method
(the username check is also done in javascript on the front-end, detailed in the paragraph after next).  If the username and/or email are not
taken, a verification code is generated randomly and sent to the user’s email.  The user’s information along with the verification code are
saved into the users table of the SQL database.  The function then redirects to the “/” route, rendering the homepage.

To login, a new user must first check their email.  On this email, the user must click the link, redirecting him to the
http://ide50-juanmolina.cs50.io:8080/verify url.  A GET request is made to the verify route, the user is able to enter their username,
password, and verification code.  Upon POST requesting the verify form, the information on the form is submitted to the verify function which
checks using SQL that the password and verification code match the username.  If so, the function redirects to the login page.  The user can
request the login page via GET to render the “login.html” template.  Upon submitting a POST request, the username and password are submitted to
the “/login” route, the password is hashed; and using SQL, the function verifies that the password hash and username match the ones in the
users table of the database, thriftshare (this is also done front-end in javascript, detailed in the next paragraph).

Upon attempted submission of the register and login forms, javascript in each respective HTML templates prevent submission of the form,
requests the “/check” or “/checkpass” route, sends the username and/or password to that route, and via a $.get() method verifies that the
credentials are valid.

Not to be confused with a “POST” request, application.py also includes an app route “/post” which allows users to post items to the website.
Upon a “GET” request, the route renders the template “post.html” which includes the form that formats an item post.  Upon a “POST” request,
the python function ensures that the item name has been provided.  Then, function creates a variable for the item name and for the description,
if applicable.  Using code from http://flask.pocoo.org/docs/0.12/patterns/fileuploads/, the function saves the image provided, requesting any files submitted
with the form.  The file extension is stored in a variable using the split() method.  The file name is replaced with a unique name, the exact date and time of
the submission.  The file is saved with its new name in a directory, /images, within the /static directory.  The function then users SQL to insert the name of
the item, a reference to the location and new name of the image file, the username and id of the poster, and the description.  A ThrifToken is then added to the
user’s currency.  The user is then redirected to the “/browse” route.

The “/browse” route is GET requested upon login and the completion of a post.  The browse function uses SQL to SELECT all values from the posted table in
thriftshare.db where the available boolean is not false and store them in the ‘rows’ variable.  The function then renders the “browse.html” template, sending
the information stored in the rows variable to the HTML page, where a for loop in jinja prints the information for each item.  If the route is requested via
POST (ie. the user clicks claim).  The function calls requests the user’s information using SQL; checks that the user has enough currency; if so, 1 is
subtracted from the user’s current currency; and emails are sent to the claimant and poster via the emailclaim() function.

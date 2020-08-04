Welcome to ThriftShare! ThriftShare is a sharing and trading web application--kind of like Craigslist--except everything is free. The goal of
ThriftShare is to create a network that allows people to conveniently donate unwanted or unneeded items, and others to claim said items.
Because ThriftShare does not require monetary funds, all users are allotted with a ThriftShare currency, called ThrifTokens, which allow
users to claim items.

This web application was implemented in CS50 IDE and is run as a flask application. To use ThriftShare, you must enter CS50 IDE and have access
to the ‘project’ folder--including all files in the ‘static’ and ‘templates’ folders--all additional files outside of these two folders, and a
working email address.

Once verifying that all documents are present, enter a terminal in the IDE. Use the command ‘cd’ to make sure you are in the workspace, and
then after use the command ‘cd project/files’ to enter the proper folder. Next, execute command ‘flask run’ to run the web application. From
there, you can clink the link presented in the terminal that will allow you to fully access ThriftShare, and you can begin to use the site.

The first step to utilizing ThriftShare is to register for an account. To do this, click the ‘Register’ tab located at the top right of the
homepage, and all of the required information prompted to you. You must have access to a valid email address in order to complete registration
because the after registration is completed, a verification code will be emailed to you that will allow you to verify their account.

If you (the user) supplied a functioning, valid email during the registration process, then you should receive an email that supplies you with
a verification code and a link. Copy this verification code (inside the quotation marks ‘ ’), click the link--which should take you to an
account verification page--and enter your username and password created during registration and the provided verification code.
After clicking ‘Verify,’ your account should be accessible. After verification, log in to your account to utilize all features of ThriftShare.

ThriftShare includes several features, the main ones being ‘Post’ and ‘Browse.’ Post allows a user to post an image, title, and description of
their unwanted items to be displayed to other users; each time a user posts an image they receive one ThrifToken. If a user makes an accidental
post, they can opt to ‘Cancel’ it (this feature is located in the ‘Profile’ route under the ‘Me’ tab). On the other hand, ‘Browse’ is a page
that allows users to browse through items and claim the ones they want to redeem; once a user claims an item, ThriftShare initiates a
correspondence between the user and the “seller,” and the user spends one ThrifToken. Once a user runs out of ThrifTokens, they can no longer
claim items.

The ‘Me’ dropdown menu includes three fields: profile, history, and logout. ‘Profile’ allows a user to see their basic account information,
including their username, number of ThrifTokens available, and active posts (posts that have not been claimed or cancelled). ‘History’ shows a
users entire post and claim history and the date of each action. ‘Logout’ simply logs the user out of ThriftShare.

































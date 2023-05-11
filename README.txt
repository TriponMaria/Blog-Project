Adding Users to Our Blog Project

1. Register New Users
	The users will go to the '/register' route to sign up to my blog. I created a WTForm in 	forms.py called RegisterForm and use FlaskBootstrap to render a wtf quick_form.
	The data the user entered will be used to create a new entry in my blof.db in a User table
2. Login Registered Users
	Users who have been successfully registered (added to the user table in the database) will 	be able to go to the 'login' route to use their credentials to log in. 
	When users successfully register they are taken back to the home page and are logged in with 	Flask-Login.
	In the '/register' routeIf a user is trying to register with an email that already exists in
	the database then they will be redirected to the '/login' route and a flash message will 	tell them to log in with that email instead.
	In the '/login' route, if a user's email does not exist in the database or if their password 	does not match to one stored using check_password() then they will be redirected back to 	'/login' and a flash message will let them know what they issue was and ask them to try 	again.
	Navbar when a user is not logged in shows: HOME, LOGIN, REGISTER, ABOUT, CONTACT
	Navbar when a user is logged in/authenticated shows: HOME, LOG OUT, ABOUT, CONTACT
	When a user click on the LOG OUT button, it logs them out and takes them back to the home 	page.
3. Protect Routes
	The first registered will be the admin. He will be able to create new blog posts, edit posts 
	and delete posts.
	The first user's id is 1. We use this in index.html and post.html to make sure that only the 	admin user can see the "Create New Post" and "Edit Post" and Delete buttons.
	Just because a user can't see the buttons, they can still manually access the '/edit-post' 	or '/new-post' or '/delete' routes. I protected these routes by creating a Python decorator 	called @admin_only
4. Relational Databases
	Given that the 1st user in the admin and the blog owner. It would make sense if we could 	link  the blog posts they write to their user in the database. In the future, maybe I will 	want to invite other users to write posts in the blog and grant them the admin privileges.
	So I created a relationship between the User table and the BlogPost table to link them 	together. I can see which BlogPosts a User has written, or wee which User is the author of a 	particular BlogPost.
	This make it easy to find all the BlogPosts a particular user has written. 
	I created a One-to-Many relationship between the User Table and the BlogPost table, where 	One User can create Many BlogPost objects. I am able to easily locate the BlogPosts a User 	has written and also the User of any BlogPost object.
5. Allow Any User to Add Comments to BlogPosts
	CommentForm in the form.py file it only contain a single CKEditorField for user to write 	their comments.
	I allow users to leave a comment and save the comment.
	The table Comment where tablename is "comments" contain an id and a text property which is 	the primary key and the text entered into the CKEditor
	Between User table and Comment table exist a One-to-Many relationship. Where one User is 	linked to many Comment objects.
	Between BlogPost table and Comment table exist a One-to-Many relationship where each 	BlogPost can have many associated Comment objects.
	I make sure that only authentificated(logged-in) users can save their comment. Otherwise, 	they will see a flash message telling them to log in and redirect them to the '/login' route
	All the commenta associated with the blog post will be displayed.
	I use Gravatar to add images into the comments sections.
	
	
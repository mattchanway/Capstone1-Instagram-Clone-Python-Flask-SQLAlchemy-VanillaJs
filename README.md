Welcome to Gramly, my first capstone project.

The objective here was to create a simple 'Insta-inspired' full-stack app using Python, Flask, and PostgresQL. The styling is plain, and there will be future improvements and features implemented, however, it was a tremendously fulfilling and fun project to complete after only having coded for four months or so (I say this humbly, as I know there are people who have achieved far more in a much shorter time frame). I opted to create a simple CRUD 'api' that handles the back-end operations, detailed specifically below. For now, these 'api' routes can just be found in app.py.

During this project, I had weekly mentoring calls with Christos Gkoros, a software engineer located in Athens, Greece. His patient manner and years of wisdom as a software architect were invaluable to my learning. Four test accounts haved been created, johndoe, janedoe, lisadoe, and markdoe, all with the password 'password.'

Here is a list of the simple features implemented so far:

-A user can login, and they will shown a 'feed' of posts from accounts they follow that have been made within the last 7 days.
-New users may sign up
-A user can view other user accounts, either by clicking on the account name in the header of a given post in their feed, or by navigating to them directly '/user/<username>.'
-A user can follow or unfollow other users, and these following/followers totals are shown in individual user pages, and affect what is seen in the home feed for a given user.
-A user can click and get a detailed list of the followers and followings of a given account, viewable from that account's detail page.
-Users can like posts, and click a button see a list of all the users that have liked that post. Posts can be unliked by the same user after they have been liked.
-Similar to the post workflow, users can make comments on posts, delete those comments (if they are the orignal commentor), like/unlike comments,
and see a list of all users who have liked a given comment.
-Users can delete any of their own posts, and also delete their own account.
-If a user is not logged in, they can still view posts and account detail pages, but they cannot carry out activities that are tied to a user (ie they cannot post, like posts, comment, etc).

How To Run:

As there have been minor tweaks made to the code since the initial deployment, the easiest approach would be to create a database, 'gramly,' and then run seed.py. The app can be demoed on a local server, and the latest codebase will be deployed live as part of my upcoming portfolio upon completion of my final capstone project. Stay tuned!






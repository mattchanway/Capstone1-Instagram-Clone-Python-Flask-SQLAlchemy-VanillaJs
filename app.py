from flask import Flask, render_template, request, flash, redirect, session, g, url_for, jsonify, Response
import requests
import datetime 
import os
from sqlalchemy.exc import IntegrityError
from forms import LoginForm, SignupForm, PostForm
from urllib.parse import urlparse, parse_qs


from models import db, connect_db, User, Post, Dm, Follows, Likes, Story, Save, Comment, CommentLikes

app = Flask(__name__)
CURR_USER_KEY = "username"

app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL','postgresql:///gramly')
# app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL').replace("://", "ql://", 1)

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = False
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = True
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY','secretkey12345')


connect_db(app)

# ***Global, Login, Logout, Signup, and Delete User Routes********************


# get_video_id was sourced from Stack Overflow, an extremely helpful function created by Mikhail Kashkin.
def get_video_id(val):
    query = urlparse(val)
    if query.hostname == 'youtu.be':
        return query.path[1:]
    if query.hostname in ('www.youtube.com', 'youtube.com'):
        if query.path == '/watch':
            p = parse_qs(query.query)
            return p['v'][0]
        if query.path[:7] == '/embed/':
            return query.path.split('/')[2]
        if query.path[:3] == '/v/':
            return query.path.split('/')[2]

    return None



def not_found(e):
    return 'Bad request', 404

def server_error(e):
    return 'Server error, please try again later', 500

app.register_error_handler(404, not_found)


def do_login(user):

    session["username"] = user.username
    session["id"] = user.id

def do_logout():

    if "username" in session:
        del session["username"]
        del session["id"]

@app.route('/logout')
def logout():
    """Handle logout of user."""

    do_logout()
    flash('You have logged out.', 'alert alert-primary')
    return redirect('/login')

@app.route('/login', methods = ['GET', 'POST'])
def show_login():

    """Show the login form, or if the form has been validated, attempt to authenticate the form's login details. 
    If a user is active in their session, redirect to the root/home feed. """

    form = LoginForm()

    if CURR_USER_KEY in session:
        return redirect('/')

    if form.validate_on_submit():
        user = User.authenticate(form.username.data, form.password.data)

        if user:
            do_login(user)
            flash(f"Welcome back {user.username}.",'alert alert-primary')
            return redirect("/")
        else:
            flash("Invalid login.", 'alert alert-danger')
            return redirect("/")

    else:
        return render_template('login.html', form = form)

@app.route('/signup', methods = ['POST', 'GET'])
def show_signup():
    """Show the signup form, or if validating submitted form, make an 'api call' to add a new user to Gramly's database,
    log the newly-created user in, flash a welcome message, and redirect them to the root directory."""
    form = SignupForm()
    if form.validate_on_submit():

        json = {
            "username" : form.username.data,
            "password" : form.password.data,
            "email" : form.email.data,
            "image" : form.image.data
        }
       
        res = add_user(json)
        new_user_id = res.json['user']['id']
        new_user = User.query.get(new_user_id)
        do_login(new_user)
        flash(f"Welcome to Gramly, {new_user.username}", 'alert alert-primary')

        
        return redirect('/')
    else:
        return render_template('signup.html', form = form)



# ************************API Routes********************

@app.route('/api/users/<username>/feed')
def generate_feed(username):
    """For a given user, generate their feed"""
    user = User.query.filter(User.username == username).one()
    today = datetime.datetime.today()
    one_week_ago = today -datetime.timedelta(days=7)
    # get all the users the U follows, get all their posts within the last week, pass someinfo to a feedroute with ability to view indiv posts
    user_following = user.following
    all_posts = []
    for account in user_following:
        for item in account.posts:
            if item.timestamp > one_week_ago:
                all_posts.append(item)
    data = sorted([{
        "post_id": post.id,
        "post_userid": post.user_id,
        "media": post.media,
        "caption": post.caption,
        "timestamp": post.timestamp,
        "poster": post.poster.username,
        "poster_image": post.poster.image
} for post in all_posts],key = lambda post: post['timestamp'], reverse = True)
    return jsonify(data)



@app.route('/api/users', methods = ['POST'])
def add_user(dict):
    """Add a new user to Instant-gram's backend."""
    new_user = User.signup(
        username = dict["username"],
        password = dict["password"],
        email = dict["email"],
        image = dict["image"]
    )
    db.session.add(new_user)
    db.session.commit()
    return jsonify(user = new_user.serialize())

@app.route('/api/users/<username>', methods = ['POST'])
def delete_user(username):
    """Delete the user specified by the username variable. """
    user = User.query.filter(User.username == username).one()
    db.session.delete(user)
    db.session.commit()
    return jsonify(message="User deleted")

@app.route('/api/users/<username>')
def generate_user_profile_info(username):
    """For a given user, retrieve the user's profile information, including posts, followers, and followed users."""
    try:
        user = User.query.filter(User.username == username).one()
    except:
        return Response("Not found", status = 500)
    posts = user.posts
    posts_comprehension = sorted([{"id": post.id,"media": post.media, "caption": post.caption, "timestamp": post.timestamp} for post in posts],
    key = lambda post: post["timestamp"], reverse = True)
    followers_comp = [account.username for account in user.followers]
    following_comp = [account.username for account in user.following]
    likes_comprehension = [like.id for like in user.likes]
    # list comprehension so the response obj is valid json
    return jsonify(
        {
            "user": {
                "id": user.id,
                "username": username,
                "image": user.image,
                "bio": user.bio,
                "posts": posts_comprehension,
                "likes": likes_comprehension,
                "followers": followers_comp,
                "following": following_comp
            }
        }
    )


@app.route('/api/posts/<username>', methods = ['POST'])
def add_post(dict):
    """Add a new post for a given user."""

    media_url = dict["media"]

    if 'youtube' in media_url or 'youtu.be' in media_url:
        id_str = get_video_id(media_url)
        dict["media"] = f'https://www.youtube.com/embed/{id_str}'
   
    new_post = Post(
        user_id = dict["user_id"],
        media = dict["media"],
        caption = dict["caption"],
        
        )
    db.session.add(new_post)
    db.session.commit()
    return(jsonify(post = new_post.serialize()),201)

@app.route('/api/posts/likes/<int:postid>', methods = ['POST'])
def handle_post_likes(postid):
    """Handles adding a like to a post, as well as removing a like from a post"""

    post = Post.query.get(postid)
    liked_by = [liker.username for liker in post.likers]
    curr_userid = request.json["curr_userid"]
    curr_user = User.query.get(curr_userid)
    if curr_user.username in liked_by:
        like_to_remove = Likes.query.get((postid, curr_userid ))
        db.session.delete(like_to_remove)
        db.session.commit()
        return jsonify(message = "Post unliked")
    else:
        new_like = Likes(liked_post_id = postid, user_liking_id = curr_userid)
        db.session.add(new_like)
        db.session.commit()
        return jsonify(message = "Post liked")

@app.route('/api/posts/likes/<int:postid>', methods = ['GET'])
def show_post_likes(postid):
    """Returns a list of users who have liked a post."""

    post = Post.query.get(postid)
    likers = post.likers
    resp = [{"userid":liker.id, 
    "username":liker.username,
    "image":liker.image
    } for liker in likers]
    
    return jsonify(resp)

@app.route('/api/posts/<int:postid>', methods = ['POST'])
def delete_post(postid):
    """Delete a post for a given user."""
    post = Post.query.get(postid)
    
    db.session.delete(post)
    db.session.commit()
    return jsonify(message="Post deleted")

@app.route('/api/posts/<int:postid>', methods = ['GET'])
def retrieve_post(postid):
    """For individual viewing of a post, retrives all the post details, including all likes and saves"""
    
    post = Post.query.get(postid)
    if post == None:
        return Response("Not found", status = 500)
    comments = post.comments
    comments_comprehension = [{
        "id": comment.id,
        "commentor": comment.commentor,
        "text": comment.text,
        "comment_timestamp": comment.timestamp,
        "commentor_image": comment.user.image,
        "liked_by": [comment_liker.username for comment_liker in comment.liked_by]
    } for comment in comments]
    likers = post.likers
    likers_comprehension = [like.username for like in likers]
    return jsonify(({
        "post":{
            "id": post.id,
            "user_id": post.user_id,
            "media": post.media,
            "caption": post.caption,
            "post_timestamp": post.timestamp,
            "comments": comments_comprehension,
            "liked_by": likers_comprehension
        }
    }))



@app.route('/api/follows/<username>', methods = ['POST'])
def follow_unfollow(username):
    """Will create a follow from the session user to the username specified"""
    following_username = request.json["curr_user"]
    following_user = User.query.filter(User.username == following_username).one()
    user = User.query.filter(User.username == username).one()
    if user in following_user.following:
        follow = Follows.query.get((following_user.id, user.id))
        db.session.delete(follow)
        db.session.commit()
        return jsonify(
        message="unfollowed"
    )
    else:
        follow = Follows(user_following_id=following_user.id, followed_user_id = user.id)
        db.session.add(follow)
        db.session.commit()
        return(jsonify(
            {
                "follow":{
                    "followed": user.id,
                    "following": following_user.id
                }
            }
        ))

@app.route('/api/comments/add/<int:postid>', methods = ['POST'])
def add_comment(postid):
    """Adds a comment to a specified post"""

    if CURR_USER_KEY in session:
        comment_data = request.json["comment"]
        comment = Comment(commentor = session[CURR_USER_KEY], post_id = postid, text = comment_data)
        db.session.add(comment)
        db.session.commit()
        return jsonify(message="Comment added")
    else:
        flash("You must be logged in to comment.", 'alert alert-danger')
        return redirect('/login')

@app.route('/api/comments/<int:comment_id>', methods = ['POST', 'GET'])
def remove_comment(comment_id):
    """Remove a comment from a specified post"""

    comment = Comment.query.get(comment_id)
    db.session.delete(comment)
    db.session.commit()
    return jsonify(message="Comment deleted")
    

@app.route('/api/commentlikes/<int:comment_id>', methods = ['POST'])
def handle_comment_likes(comment_id):
    """Add and remove likes from comments on posts"""

    curr_user_username = request.json["curr_user"]
    curr_user = User.query.filter(User.username == curr_user_username).one()
    curr_user_liked_comments = [comment.id for comment in curr_user.liked_comments]
    if comment_id in curr_user_liked_comments:
        commentlike_to_remove = CommentLikes.query.get((comment_id, curr_user_username))
        db.session.delete(commentlike_to_remove)
        db.session.commit()
        return jsonify(message="Comment unliked")
    else:
        new_commentlike = CommentLikes(liked_comment_id = comment_id, liking_user = curr_user_username)
        db.session.add(new_commentlike)
        db.session.commit()
        return jsonify(message="Comment liked")

@app.route('/api/commentlikes/<int:comment_id>')
def retrieve_comment_likes(comment_id):
    """Retrieve a list of users who have liked a comment"""

    comment = Comment.query.get(comment_id)
    liked_by = comment.liked_by
    response = [{"username": user.username, "id": user.id, "image": user.image} for user in liked_by]
    return jsonify(response)

@app.route('/api/users/followers/<username>')
def retrieve_user_followers(username):
    """Retrieve a list of user followers"""

    user = User.query.filter(User.username == username).one()
    followers = user.followers
    response = [{"username": account.username, "image": account.image} for account in followers]
    return jsonify(response)

@app.route('/api/users/following/<username>')
def retrieve_user_following(username):
    """Retrieve a list of who the user follows"""

    user = User.query.filter(User.username == username).one()
    following = user.following
    response = [{"username": account.username, "image": account.image} for account in following]
    return jsonify(response)


# ***************General Instant-gram routes************

@app.route('/')
def show_home_feed():
    """If a logged-in user is detected in session, we will call the API to generate their feed. If the call does not yield a single
    post, they will be redirected to a prompt page telling them they are either all caught up, or need to follow some users."""

    if CURR_USER_KEY in session and "id" in session:
        response = generate_feed(session[CURR_USER_KEY])
        posts = response.json
        
        if len(posts) < 1:
            return render_template('empty-feed.html')

        return render_template('home-feed.html', posts = posts, curr_user = session[CURR_USER_KEY], curr_userid = session["id"])
    else:

        return redirect('/login')

@app.route('/user/<username>')
def show_user_profile(username):
    """Show the profile of a given user and populate data on if the current user follows the viewed user, if applicable."""

    response = generate_user_profile_info(username)
    if response.status_code == 500:
        flash("User not found.", 'alert alert-danger')
        return redirect('/')
    data = response.json['user']
    if CURR_USER_KEY in session:
        current_user = User.query.filter(User.username == session[CURR_USER_KEY]).one()
        curr_user = session[CURR_USER_KEY]
        logged_in_user_following = [follow.id for follow in current_user.following]
    
    else:
        logged_in_user_following = []
        curr_user = None

    return render_template('user-profile.html', data = data, logged_in_user_following = logged_in_user_following, curr_user = curr_user)

@app.route('/create-post', methods = ['POST', 'GET'])
def handle_new_posts():

    """If a user is logged in, handle adding a new post."""

    if CURR_USER_KEY in session:
        current_user = User.query.filter(User.username == session[CURR_USER_KEY]).one()

        form = PostForm()
        if form.validate_on_submit():
            
            json = {
                "user_id" : current_user.id,
                "media" : form.media.data,
                "caption" : form.caption.data
            }
            res = add_post(json)


            return redirect('/')
        else:
            return render_template('new-post.html', form = form)
    else:
        flash('You must be logged in to create posts.', 'alert alert-danger')
        return redirect('/')

@app.route('/posts/<int:postid>', methods = ['POST', 'GET'])
def view_post(postid):
    """View function for a single post."""
    response = retrieve_post(postid)
    if response.status_code == 500:
        flash("Post not found.", 'alert alert-danger')
        return redirect('/')
    data = response.json['post']
    if CURR_USER_KEY in session:
        curr_user = session[CURR_USER_KEY]
        curr_userid = session["id"]
    else:
        curr_user = None
        curr_userid = None

    return render_template('view-post.html', data = data, curr_user = curr_user, curr_userid = curr_userid)

@app.route('/posts/<int:postid>/likers')
def view_post_likers(postid):
    """See a list of users who liked a post"""

    response = show_post_likes(postid)
    data = response.json

    return render_template('post-likers.html', data = data)

@app.route('/commentlikes/<int:commentid>')
def view_comment_likers(commentid):
    """See a list of users who liked a comment."""
    
    response = retrieve_comment_likes(commentid)
    data = response.json

    return render_template('comment-likers.html', data = data)

@app.route('/user/followers/<username>')
def show_followers_list(username):
    """Retrieve a list of followers for a given user."""

    response = retrieve_user_followers(username)
    data = response.json

    return render_template('profile-followers.html', data=data)

@app.route('/user/following/<username>')
def show_following_list(username):
    """Retrieve a list of followings for a given user."""

    response = retrieve_user_following(username)
    data = response.json

    return render_template('profile-following.html', data=data)

@app.route('/posts/delete/<int:postid>', methods = ['POST'])
def handle_delete_post(postid):
    """Delete a given post (provided the request is made by the original owner of the post)."""
    post = Post.query.get(postid)
    if CURR_USER_KEY in session and post.user_id == session["id"] :
        delete_post(postid)
        flash("Post deleted.", 'alert alert-primary')
    
        return redirect('/')
    else:
        flash("You do not have permission to delete this post.", 'alert alert-danger')
        return redirect('/')

@app.route('/users/delete/<username>', methods = ['POST'])
def handle_delete_user(username):
    """Delete a given account (provided the request is made by the original owner of the account)."""
    user = User.query.filter(User.username == username).one()
    if CURR_USER_KEY in session and user.id == session["id"]:
        do_logout()
        delete_user(username)
        flash("Account deleted.", 'alert alert-primary')
        return redirect('/')
    else:
        flash("You do not have permission to delete this user.", 'alert alert-danger')
        return redirect('/')
    








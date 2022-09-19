from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy

from datetime import datetime

bcrypt = Bcrypt()

db = SQLAlchemy()

def connect_db(app):
    db.app=app
    db.init_app(app)


class Follows(db.Model):
    """Track which users are following whom."""

    __tablename__ = "follows"

    user_following_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable = False, primary_key=True)
    followed_user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable = False, primary_key=True)
    

class Likes(db.Model):
    """Tracks likes on individual posts."""
    
    __tablename__ = "likes"
    liked_post_id = db.Column(db.Integer, db.ForeignKey('posts.id'), nullable = False, primary_key = True)
    user_liking_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable = False, primary_key = True)

class Dm(db.Model):
    """Short for direct message, or private message between users."""
    
    __tablename__ = "dms"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable = False)
    receiver_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable = False)
    content = db.Column(db.Text, nullable = False)

class Story(db.Model):
    """Similar to a post, but only viewable by clicking on a specific button on a user's profile. Disappears after 24 hours."""

    __tablename__ = "stories"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable = False)
    media = db.Column(db.Text, nullable = False)
    timestamp = db.Column(db.DateTime, nullable = False, default = datetime.now())



class Save(db.Model):
    """A user can 'save' posts, and access their saved posts for easy viewing on a private page."""

    __tablename__ = "saves"
    id = db.Column(db.Integer, primary_key = True, autoincrement=True)
    saved_post_id = db.Column(db.Integer, db.ForeignKey('posts.id'), nullable = False)
    user_saving_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable = False)

class User(db.Model):

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.Text, nullable = False, unique = True)
    password = db.Column(db.Text, nullable = False)
    bio = db.Column(db.Text)
    email = db.Column(db.Text, nullable = False)
    image = db.Column(db.Text, nullable = False, default = 'https://icon-library.com/images/default-profile-icon/default-profile-icon-24.jpg')

    def serialize(self):

        return{
            'id': self.id,
            'username': self.username,
            'password': self.password,
            'image': self.image
        }

    @classmethod
    def signup(cls, username, email, password, image):

        hash_pwd = bcrypt.generate_password_hash(password).decode('UTF-8')

        user = User(
            username = username,
            email = email,
            password = hash_pwd,
            image = image
        )
        db.session.add(user)
        return user

    @classmethod
    def authenticate(cls, username, password):

        user = cls.query.filter_by(username = username).first()
        if user:
            is_auth = bcrypt.check_password_hash(user.password, password)
            if is_auth:
                return user
        return False
    
 
    posts = db.relationship('Post', cascade = "all, delete", backref= "poster")

    followers = db.relationship(
        "User",
        secondary="follows",
        primaryjoin=(Follows.followed_user_id == id),
        secondaryjoin=(Follows.user_following_id == id)
    )

    following = db.relationship(
        "User",
        secondary="follows",
        primaryjoin=(Follows.user_following_id == id),
        secondaryjoin=(Follows.followed_user_id == id)
    )
    # following = db.relationship(
    #     "User",
    #     secondary="follows",
    #     primaryjoin=(Follows.user_following_id == id),
    #     secondaryjoin=(Follows.followed_user_id == id),
    #     cascade = "all,delete"
    # )

    likes = db.relationship(
        'Post',
        secondary="likes",
        cascade = "all,delete",
        backref = "likers"
    )

    stories = db.relationship('Story', cascade = "all, delete")

    saves = db.relationship('Save', cascade = "all,delete")


    threads = db.relationship('User',
    secondary = "dms",
    primaryjoin=(Dm.receiver_id == id),
    secondaryjoin=(Dm.sender_id == id),
    cascade = "all, delete"
    )

    comments = db.relationship('Comment', cascade = "all,delete", backref = "user")

    liked_comments = db.relationship(
        'Comment',
        secondary='commentlikes',
        cascade = 'all,delete',
        backref = 'liked_by'
    )

class Comment(db.Model):
    """Comments on an individual's post. You do not have to follow a user to post a comment on one of their posts."""

    __tablename__ = "comments"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    commentor = db.Column(db.Text, db.ForeignKey('users.username'), nullable = False)
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'), nullable = False)
    text = db.Column(db.Text, nullable = False)
    timestamp = db.Column(db.DateTime, nullable = False, default = datetime.utcnow())

 

   

class Post(db.Model):

    __tablename__ = "posts"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id' ), nullable = False)
    media = db.Column(db.Text, nullable = False)
    caption = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, nullable = False, default = datetime.now)

    comments = db.relationship("Comment",
    cascade = "all,delete")

    def serialize(self):

        return{
            'id': self.id,
            'user_id': self.user_id,
            'media': self.media,
            'caption': self.caption,
            'timestamp': self.timestamp
        }

class CommentLikes(db.Model):
    """Keeps track of likes on individual comments on a post."""

    __tablename__ = "commentlikes"

    liked_comment_id = db.Column(db.Integer, db.ForeignKey('comments.id'), nullable = False, primary_key = True)
    liking_user = db.Column(db.Text, db.ForeignKey('users.username'), nullable = False, primary_key = True)


    



    







    


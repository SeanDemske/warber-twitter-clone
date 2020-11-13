"""User model tests."""

# run these tests like:
#
#    python -m unittest test_user_model.py


import os
from unittest import TestCase
from sqlalchemy import exc

from models import db, User, Message, Follows

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql://postgres:developer@localhost:5432/warbler-test"


# Now we can import app

from app import app

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()


class UserModelTestCase(TestCase):
    """Test user model functionality"""

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        Message.query.delete()
        Follows.query.delete()

        u1 = User(
            email="test1@test.com",
            username="testuser1",
            password="HASHED_PASSWORD"
        )
    
        u2 = User(
            email="test2@test.com",
            username="testuser2",
            password="HASHED_PASSWORD"
        )

        db.session.add(u1)
        db.session.add(u2)
        db.session.commit()

        self.client = app.test_client()

    def test_user_model(self):
        """Does basic model work?"""

        u = User.query.filter(User.username == "testuser1").one()

        # User should have no messages & no followers
        self.assertEqual(len(u.messages), 0)
        self.assertEqual(len(u.followers), 0)

    def test_repr_method(self):
        """Does the repr method return the correct information"""

        u = User.query.filter(User.username == "testuser1").one()

        self.assertEqual(str(u), f"<User #{u.id}: {u.username}, {u.email}>")

    def test_following_feature(self):
        """Tests the following functionality"""

        u1 = User.query.filter(User.username == "testuser1").one()
        u2 = User.query.filter(User.username == "testuser2").one()

        self.assertEqual(u1.is_following(u2), False)
        self.assertEqual(u1.is_followed_by(u2), False)

        follow = Follows(user_being_followed_id=u1.id, user_following_id=u2.id)
        db.session.add(follow)
        db.session.commit()

        self.assertEqual(u2.is_following(u1), True)
        self.assertEqual(u1.is_followed_by(u2), True)

    def test_user_signup(self):
        """Testing user create functionality"""

        valid_user = User.signup("valid_user", "testdevemail@email.com", "password", None)
        valid_user.id = 9001
        db.session.commit()

        valid_user = User.query.get(9001)
        self.assertIsNotNone(valid_user)
        self.assertEqual(valid_user.username, "valid_user")
        self.assertEqual(valid_user.email, "testdevemail@email.com")
        self.assertNotEqual(valid_user.password, "password")
        # Bcrypt strings should start with $2b$
        self.assertTrue(valid_user.password.startswith("$2b$"))

        invalid_user = User.signup(None,  None, "password", None)
        invalid_user.id = 9002
        with self.assertRaises(exc.IntegrityError) as context:
            db.session.commit()

        #Testing invalid passwords
        with self.assertRaises(ValueError) as context:
            User.signup("testtest", "email@email.com", "", None)
        
        with self.assertRaises(ValueError) as context:
            User.signup("testtest", "email@email.com", None, None)

    def test_authentication(self):
        """Tests the authentication functionality"""

        u = User.signup("authenticated_user", "testdevemail@email.com", "password", None)
        self.assertEqual(str(User.authenticate("authenticated_user", "password")), f"<User #{u.id}: {u.username}, {u.email}>")
        self.assertEqual(User.authenticate("incorrect_username", "password"), False)
        self.assertEqual(User.authenticate("authenticated_user", "incorrect_password"), False)
    



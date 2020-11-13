"""Message model tests"""

# To run these tests:
# "python -m unittest test_message_model.py"

import os
from unittest import TestCase
from sqlalchemy import exc

from models import db, User, Message, Follows

# Make sure to use a testing database as not to interfere with production

os.environ['DATABASE_URL'] = 'postgresql://postgres:developer@localhost:5432/warbler-test'

from app import app

# Now we create our tables

db.create_all()

class MessageModelTestCase(TestCase):
    """Tests message model functionality"""

    def setUp(self):
        """Create test client, add sample data"""

        # Delete all previous instance so each test is ran with clean data
        User.query.delete()
        Message.query.delete()
        Follows.query.delete()

        u1 = User(
            email="test1@test.com",
            username="testuser1",
            password="HASHED_PASSWORD"
        )

        db.session.add(u1)
        db.session.commit()

        m1 = Message(
            text="This is message number one",
            user_id=u1.id
        )

        db.session.add(m1)
        db.session.commit()

    def tearDown(self):
        db.session.rollback()

    def test_message_model(self):
        """Does the basic model work?"""

        m = Message.query.filter(Message.text == "This is message number one").one()
        u = User.query.filter(User.username == "testuser1").one()

        self.assertEqual(m.user_id, u.id)
        self.assertEqual(m.text, "This is message number one")

        invalid_message = Message(text=None, user_id=u.id)
        db.session.add(invalid_message)

        with self.assertRaises(exc.IntegrityError) as context:
            db.session.commit()
        

    def test_message_to_user_association(self):
        """Are the messages correctly associated with the user"""

        u = User.query.filter(User.username == "testuser1").one()

        self.assertEqual(len(u.messages), 1)

        m2 = Message(
            text="This is message number two",
            user_id=u.id
        )

        db.session.add(m2)
        db.session.commit()

        self.assertEqual(len(u.messages), 2)
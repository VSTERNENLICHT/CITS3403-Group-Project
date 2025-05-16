import unittest
from app_factory import create_app
from models import db, User, SharedGraph, GPA, WAM
import re


class ShareGraphTestCase(unittest.TestCase):

    def setUp(self):
        config = {
            "TESTING": True,
            "WTF_CSRF_ENABLED": False,
            "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:"
        }
        self.app = create_app(config)
        self.client = self.app.test_client()
        self.ctx = self.app.app_context()
        self.ctx.push()

        db.create_all()
        # Create users
        self.user1 = User(email="sharer@test.com")
        self.user1.set_password("password")
        self.user2 = User(email="recipient@test.com")
        self.user2.set_password("password")
        db.session.add_all([self.user1, self.user2])
        db.session.commit()

        # Log in as user1
        with self.client.session_transaction() as sess:
            sess["_user_id"] = str(self.user1.id)

    def test_share_page_loads(self):
        response = self.client.get('/share')
        self.assertEqual(response.status_code, 200)
        self.assertIn("Share To Your Friends", response.get_data(as_text=True))

    def test_my_shared_graphs_loads(self):
        # First share something
        self.client.post('/share-graph', data={
            'shareMarks': 'yes',
            'sharedto': 'recipient@test.com'
        })
        response = self.client.get('/my-shared-graphs')
        self.assertEqual(response.status_code, 200)
        self.assertIn("Graphs You've Shared", response.get_data(as_text=True))

    def test_invalid_share_to_self(self):
        response = self.client.post('/share-graph', data={
            'shareMarks': 'yes',
            'sharedto': 'sharer@test.com'  # Sharing to self
        })
        self.assertIn("You cannot share with yourself", response.get_data(as_text=True))

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.ctx.pop()

if __name__ == '__main__':
    unittest.main()

import unittest
import os
from app import app, db
from models import User, SharedGraph, GPA, WAM
from flask_login import login_user

class ShareGraphTestCase(unittest.TestCase):

    def setUp(self):
        os.environ["FLASK_ENV"] = "testing"
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'

        self.app = app
        self.client = app.test_client()

        with self.app.app_context():
            db.create_all()
            # Create two users: one sharer and one recipient
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
        self.assertIn(b"Share To Your Friends", response.data)

    def test_share_graph_success(self):
        response = self.client.post('/share-graph', data={
            'shareMarks': 'yes',
            'sharedto': 'recipient@test.com'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"share_link", response.get_data(as_text=True))  # Because your view renders with share_link

    def test_my_shared_graphs_loads(self):
        # First share something
        self.client.post('/share-graph', data={
            'shareMarks': 'yes',
            'sharedto': 'recipient@test.com'
        })
        response = self.client.get('/my-shared-graphs')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Graphs You've Shared", response.data)

    def test_invalid_share_to_self(self):
        response = self.client.post('/share-graph', data={
            'shareMarks': 'yes',
            'sharedto': 'sharer@test.com'  # Sharing to self
        })
        self.assertIn(b"You cannot share with yourself", response.data)

    def tearDown(self):
        with self.app.app_context():
            db.drop_all()

if __name__ == '__main__':
    unittest.main()

import unittest
import json
from app import app, db
from models import User, Goal

class SetGoalTestCase(unittest.TestCase):

    def setUp(self):
        # Configure test app
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.client = app.test_client()
        self.ctx = app.app_context()
        self.ctx.push()

        db.create_all()

        # Create and login a test user
        self.user = User(email='test@example.com')
        self.user.set_password('password123')
        db.session.add(self.user)
        db.session.commit()

        # Log in the user manually via session
        with self.client.session_transaction() as session:
            session['_user_id'] = str(self.user.id)

    def test_save_goal_valid(self):
        payload = {
            "user_id": str(self.user.id),
            "wam": 85.0,
            "gpa": 6.7
        }
        response = self.client.post('/save-goal',
                                    data=json.dumps(payload),
                                    content_type='application/json')

        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Your goals have been saved!', response.data)

        goal = Goal.query.filter_by(user_id=self.user.id).first()
        self.assertIsNotNone(goal)
        self.assertEqual(goal.wam, 85.0)
        self.assertEqual(goal.gpa, 6.7)

    def test_save_goal_invalid_wam(self):
        payload = {
            "user_id": str(self.user.id),
            "wam": 120.0,  # Invalid WAM
            "gpa": 6.7
        }
        response = self.client.post('/save-goal',
                                    data=json.dumps(payload),
                                    content_type='application/json')

        self.assertEqual(response.status_code, 400)
        self.assertIn(b'WAM must be between 0 and 100', response.data)
    
    def test_save_goal_invalid_gpa(self):
        payload = {
            "user_id": str(self.user.id),
            "wam": 85.0,
            "gpa": 7.5  # Invalid GPA
        }
        response = self.client.post('/save-goal',
                                    data=json.dumps(payload),
                                    content_type='application/json')

        self.assertEqual(response.status_code, 400)
        self.assertIn(b'GPA must be between 0 and 7', response.data)
    
    def test_save_goal_update(self):
        payload = {
            "user_id": str(self.user.id),
            "wam": 70.0,
            "gpa": 6
        }
        response = self.client.post('/save-goal',
                                    data=json.dumps(payload),
                                    content_type='application/json')

        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Your goals have been saved!', response.data)

        goal = Goal.query.filter_by(user_id=self.user.id).first()
        self.assertIsNotNone(goal)
        self.assertEqual(goal.wam, 70.0)
        self.assertEqual(goal.gpa, 6.0)

    def test_save_goal_wrong_user(self):
        payload = {
            "user_id": str(self.user.id + 1),  # Wrong user ID
            "wam": 70.0,
            "gpa": 5.5
        }
        response = self.client.post('/save-goal',
                                    data=json.dumps(payload),
                                    content_type='application/json')

        self.assertEqual(response.status_code, 403)
        self.assertIn(b'Unauthorized access', response.data)

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.ctx.pop()

if __name__ == '__main__':
    unittest.main()
from app_factory import create_app
from models import db, User, Calculations, GPA, WAM
import unittest
import json

class CalculatorRouteTestCase(unittest.TestCase):
    def setUp(self):
        # Create a test version of the app
        config = {
            'TESTING': True,
            'WTF_CSRF_ENABLED': False,
            'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:'
        }
        self.app = create_app(config)
        self.client = self.app.test_client()
        self.ctx = self.app.app_context()
        self.ctx.push()

        db.create_all()

        # Create and login a test user
        self.user = User(email='test@example.com')
        self.user.set_password('password123')
        db.session.add(self.user)
        db.session.commit()

        # Manually log in the user
        with self.client.session_transaction() as session:
            session['_user_id'] = str(self.user.id)

    def test_works_without_regular_units(self):
        form_data = {
            'previous_units_tab-0-previous_units-0-unit': 'COMP1000',
            'previous_units_tab-0-previous_units-0-semester': 'Semester 1',
            'previous_units_tab-0-previous_units-0-year': 'Year 1',
            'previous_units_tab-0-previous_units-0-mark': '90',
            'previous_units_tab-0-previous_units-1-unit': 'COMP2000',
            'previous_units_tab-0-previous_units-1-semester': 'Semester 1',
            'previous_units_tab-0-previous_units-1-year': 'Year 2',
            'previous_units_tab-0-previous_units-1-mark': '80',
        }
        response = self.client.post('/calculator', data=form_data, follow_redirects=True)
        self.assertIn(b"Predicted GPA/WAM</div>", response.data)

    def test_invalid_mark_flash_message(self):
        form_data = {
            'previous_units_tab-0-previous_units-0-unit': 'COMP1000',
            'previous_units_tab-0-previous_units-0-semester': 'Semester 1',
            'previous_units_tab-0-previous_units-0-year': 'Year 1',
            'previous_units_tab-0-previous_units-0-mark': '110',  # Invalid mark
        }
        response = self.client.post('/calculator', data=form_data, follow_redirects=True)
        self.assertIn(b"needs to be between 0 to 100", response.data)

    def test_total_weighting_not_100_flash_message(self):
        form_data = {
            'previous_units_tab-0-previous_units-0-unit': 'COMP1000',
            'previous_units_tab-0-previous_units-0-semester': 'Semester 1',
            'previous_units_tab-0-previous_units-0-year': 'Year 1',
            'previous_units_tab-0-previous_units-0-mark': '90',
            'units-0-unit': 'COMP2000',
            'units-0-semester': 'Semester 1',
            'units-0-year': 'Year 2',
            'units-0-assessments-0-atype': 'Exam',
            'units-0-assessments-0-student_mark': '40',
            'units-0-assessments-0-max_mark': '50',
            'units-0-assessments-0-weight': '90',  # Should be 100
        }
        response = self.client.post('/calculator', data=form_data, follow_redirects=True)
        self.assertIn(b"do not add up to 100%", response.data)


    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.ctx.pop()
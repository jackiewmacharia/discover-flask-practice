import unittest
from project import app, db
from flask_testing import TestCase
from project.models import User, BlogPost
from flask_login import current_user


class BaseTestCase(TestCase):
    """A base test case."""

    def create_app(self):
        app.config.from_object('config.TestConfig')
        return app

    def setUp(self):
        db.create_all()
        db.session.add(BlogPost("Test post", "Hello from the other side", "admin"))
        db.session.add(User("admin", "ad@min.com", "admin"))
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()


class FlaskTestCase(BaseTestCase):

    # Ensure that flask was set up correctly
    def test_index(self):
        response = self.client.get('/login', content_type='html/text')
        self.assertEqual(response.status_code, 200)

    # Ensure that main page requires login
    def test_main_route_requires_login(self):
        response = self.client.get('/', follow_redirects=True)
        self.assertIn(b'Please log in to access this page.', response.data)

    # Ensure that posts show up on the main page
    def test_posts_show_up_on_main_page(self):
        response = self.client.post(
            '/login',
            data=dict(username="admin", password="admin"),
            follow_redirects=True
        )
        self.assertIn(b'Hello from the other side', response.data)  # Never mix test data with real data


class UserViewsTests(BaseTestCase):
    # Ensure that login page loads correctly
    def test_login_page_loads(self):
        response = self.client.get('/login', content_type='html/text')
        self.assertTrue(b'Please login' in response.data)

    # Ensure that login page behaves correctly given correct credentials
    def test_correct_login(self):
        with self.client:
            response = self.client.post(
                '/login', data=dict(username="admin", password="admin"),
                follow_redirects=True
            )
            self.assertIn(b'You were just logged in', response.data)
            self.assertTrue(current_user.name == 'admin')
            self.assertTrue(current_user.is_active())

    # Ensure that login page behaves correctly given incorrect credentials
    def test_incorrect_login(self):
        response = self.client.post(
            '/login', data=dict(username="anhfkd", password="kfvf"),
            follow_redirects=True
        )
        self.assertIn(b'Invalid credentials. Please try again.', response.data)

    # Ensure that logout page behaves correctly
    def test_logout(self):
        with self.client:
            response = self.client.post(
                '/login', data=dict(username="admin", password="admin"),
                follow_redirects=True
            )
            response = self.client.get('/logout', follow_redirects=True)
            self.assertIn(b'You were just logged out', response.data)
            self.assertFalse(current_user.is_active)

    # Ensure that logout page requires user to be logged in first
    def test_logout_requires_login(self):
        response = self.client.get('/logout', follow_redirects=True)
        self.assertIn(b'Please log in to access this page.', response.data)

    # Ensure user can register
    def test_user_registration(self):
        with self.client:
            response = self.client.post(
                '/register', data=dict(username='jax', email='jax@example.com', password='password', confirm='password'),
                follow_redirects=True
            )
            self.assertIn(b'Welcome to Flask!', response.data)
            self.assertTrue(current_user.name == 'jax')
            self.assertTrue(current_user.is_active())

    # Ensure registration errors are caught
    def test_registration_errors(self):
        with self.client:
            response = self.client.post(
                '/register', data=dict(username='jax', email='jax@example.com', password='password', confirm='pssword'),
                follow_redirects=True
            )
            self.assertIn(b'Invalid credentials. Please try again.', response.data)
            self.assertFalse(current_user.is_active)


if __name__ == '__main__':
    unittest.main()

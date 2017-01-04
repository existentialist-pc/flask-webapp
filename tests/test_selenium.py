from selenium import webdriver
import unittest
from app import create_app, db
from app.models import Role, User, Post
import threading
import re


class SeleniumTestCase(unittest.TestCase):
    client = None

    @classmethod
    def setUpClass(cls):
        try:
            cls.client = webdriver.Firefox()  # 启动firefox; move geckodriver to /usr/local/bin
        except:
            pass

        if cls.client:
            cls.app = create_app('testing')
            cls.app_context = cls.app.app_context()
            cls.app_context.push()

            import logging
            logger = logging.getLogger('werkzeug')
            logger.setLevel('ERROR')

            db.create_all()
            Role.insert_roles()
            User.generate_fake(10)
            Post.generate_fake(10)

            admin_role = Role.query.filter_by(permissions=0xff).first()
            admin = User(email='test@test.com', username='test', password='password', role=admin_role, confirmed=True)
            db.session.add(admin)
            db.session.commit()

            threading.Thread(target=cls.app.run).start()

    @classmethod
    def tearDownClass(cls):
        if cls.client:
            cls.client.get('http://localhost:5000/shutdown')
            cls.client.close()

            db.session.remove()
            db.drop_all()
            cls.app_context.pop()

    def setUp(self):
        if not self.client:
            self.skipTest('Web browser not available')

    def tearDown(self):
        pass

    def test_admin_home_page(self):
        self.client.get('http://localhost:5000/')
        self.assertTrue(re.search('游客', self.client.page_source))  # .client.page_source 获得页面内容

        self.client.find_element_by_link_text('登录').click()
        self.assertTrue('<h1>登录</h1>' in self.client.page_source)

        self.client.find_element_by_name('email').send_keys('test@test.com')
        self.client.find_element_by_name('password').send_keys('password')
        self.client.find_element_by_name('submit').click()
        self.assertTrue(re.search('test!', self.client.page_source))

        self.client.find_element_by_link_text('Profile').click()
        self.assertTrue('<h1>test</h1>' in self.client.page_source)


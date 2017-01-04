import unittest
from app import create_app,db
from app.models import Role, User
from flask import url_for
import re


class FlaskClientTestCase(unittest.TestCase):

    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        Role.insert_roles()
        self.client = self.app.test_client(use_cookies=True)  # 通过app.test_client创建测试客户端

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_home_page(self):
        response = self.client.get(url_for('main.index'))  # 访问测试视图函数
        self.assertTrue('游客' in response.get_data(as_text=True))  # 获得响应内容

    def test_register_and_login(self):  # 用法有点像 爬虫
        response = self.client.post(url_for('auth.register'), data={
            'email':'test1@test.com',
            'username':'tester',
            'password':'password',
            'password2': 'password'
        })
        self.assertTrue(response.status_code == 302)  # 判断返回码

        response = self.client.post(url_for('auth.login'), data={
            'email':'test1@test.com',
            'password': 'password'
        }, follow_redirects=True)  # 跟踪重定向
        data = response.get_data(as_text=True)
        self.assertTrue(re.search('tester', data))
        self.assertTrue('尚未激活' in data)

        user= User.query.filter_by(email='test1@test.com').first()
        token = user.generate_confirmation_token()
        response = self.client.get(url_for('auth.confirm', token=token), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertTrue('成功激活' in data)

        response = self.client.get(url_for('auth.logout'), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertTrue('您已登出' in data)



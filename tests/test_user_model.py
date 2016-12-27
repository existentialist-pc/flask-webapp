import unittest  # 测试过程：shell中test命令=>运行manager.py中test()，找到该文件内容，按测试流程执行该文件的类内函数
from app import create_app, db  # 所以必要的测试模块，web实现app，均要在这里导入。类似只启动调用某些需要测试的模块包的程序
from app.models import User

class UserModelTestCase(unittest.TestCase):

    def setUp(self):
        self.app = create_app(config_name='testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()  # 启动程序上下文环境，数据库初始化。并没有app.run()!

    def tearDown(self):
        db.session.remove()
        db.drop_all()  # 删表
        self.app_context.pop()

    def test_password_getter(self):
        u1 = User(password='something')
        with self.assertRaises(AttributeError):  # 这句会导致出AttributeError
            u1.password

    def test_password_verification(self):
        u1 = User(password='something')
        self.assertTrue(u1.verify_password('something'))
        self.assertFalse(u1.verify_password('nothing'))

    def test_password_salts_are_random(self):
        u1 = User(password='something')
        u2 = User(password='something')
        self.assertTrue(u1.password_hash != u2.password_hash)

#! /usr/bin/env python3.5

import os
from flask_script import Manager, Shell
from flask_migrate import Migrate, MigrateCommand
from app import create_app, db
from app.models import Role, User


app = create_app(os.environ.get('FLASK_CONFIG') or 'default')
manager = Manager(app)
migrate = Migrate(app, db)


def make_shell_context():
    return dict(app=app, db=db, Role=Role, User=User)

manager.add_command("shell", Shell(make_context=make_shell_context))
manager.add_command("db", MigrateCommand)

@manager.command
def test():  # 在shell中加入命令
    import unittest
    tests = unittest.TestLoader().discover('tests')  # 无需通过import导入！而是主动扫描tests模块包，查找测试
    unittest.TextTestRunner(verbosity=2).run(tests)  # verbosity为数字，越大显示细节越多。默认为1


if __name__ == '__main__':
    # db.create_all()
    manager.run()

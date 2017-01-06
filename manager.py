#! /usr/bin/env python3.5

import os
from flask_script import Manager, Shell
from flask_migrate import Migrate, MigrateCommand
from app import create_app, db
from app.models import Role, User, Post


app = create_app(os.environ.get('FLASK_CONFIG') or 'default')
manager = Manager(app)
migrate = Migrate(app, db)


def make_shell_context():
    return dict(app=app, db=db, Role=Role, User=User, Post=Post)

manager.add_command("shell", Shell(make_context=make_shell_context))
manager.add_command("db", MigrateCommand)

COV = None
if os.environ.get('FLASK_COVERAGE'):
    import coverage  # 对COV start到stop过程中运行的代码内容提供覆盖报告。在这里即对tests模块的测试覆盖进行评估
    COV = coverage.coverage(branch=True, include='app/*')
    COV.start()


@manager.command
def test(coverage=False):  # 在shell中加入命令
    """Run the unit tests."""
    if coverage and not os.environ.get('FLASK_COVERAGE'):
        import sys
        os.environ['FLASK_COVERAGE'] = '1'  # 设定环境变量
        os.execvp(sys.executable, [sys.executable] + sys.argv)  # 在该进程自动重启脚本，sys.executable为python3.5路径+python3.5执行
    import unittest
    tests = unittest.TestLoader().discover('tests')  # 无需通过import导入！而是主动扫描tests模块包，查找测试
    unittest.TextTestRunner(verbosity=2).run(tests)  # verbosity为数字，越大显示细节越多。默认为1
    if COV:
        COV.stop()
        COV.save()
        print('Coverage Summary:')
        COV.report()
        basedir = os.path.abspath(os.path.dirname(__file__))
        covdir = os.path.join(basedir, 'tmp/coverage')
        COV.html_report(directory=covdir)
        print('HTML version: file://%s/index.html' % covdir)
        COV.erase()


@manager.command
def profile(length=25, profile_dir=None):
    from werkzeug.contrib.profiler import ProfilerMiddleware
    app.wsgi_app = ProfilerMiddleware(app.wsgi_app, restrictions=[length], profile_dir=profile_dir)
    app.run()


@manager.command
def deploy():
    from flask_migrate import upgrade
    from app.models import Role
    upgrade()
    Role.insert_roles()  # 初始化


if __name__ == '__main__':
    # db.create_all()
    manager.run()

from . import main
from .forms import NameForm
from flask import render_template


@main.route('/', methods=['GET', 'POST'])
def index():
    return render_template('index.html')

from flask import request, redirect, render_template, abort
from flask_login import login_user, login_required, logout_user
from markupsafe import Markup

from app import app
from core.auth import auth_user
from utils.utils import get_markdown


UNITY_GAMES = ('simple_cube', 'delimiter', 'kot_guide')
HINTS = ('bash', 'git', 'markdown', 'python', 'sql', 'vim')


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/ping')
def ping():
    return "Requester IP: " + request.remote_addr


@app.errorhandler(404)
def page_not_fount(error):
    """TODO: логирование mongo"""
    print(error)
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_error(error):
    """TODO: логирование mongo"""
    print(error)
    return render_template('500.html'), 500


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('signin.html')

    user = auth_user(request.form['username'], request.form['password'])
    if user:
        login_user(user)
        return redirect('/')
    return redirect('/login')


@app.route('/logout')
def logout():
    logout_user()
    return redirect('/')


# @app.route('/protected')
# @login_required
# def protected():
#     return 'Logged in as: ' + current_user.id


@app.route('/unity/<string:game>')
def unity_game(game):
    if game in UNITY_GAMES:
        template = f'unity/{game}.html'
        return render_template(template)
    abort(404)


@app.route('/unity/privacy_policy/<string:game>')
def unity_privacy_policy(game):
    if game in UNITY_GAMES:
        game_name = game.replace('_', ' ').title()
        return render_template('unity/privacy_policy.html', game=game_name)
    abort(404)


@app.route('/utils/hints/<string:hint>')
def docs_git(hint):
    if hint in HINTS:
        doc_content = Markup(get_markdown(f'{hint}.md'))
        return render_template('utils/hints.html', doc=doc_content)
    abort(404)


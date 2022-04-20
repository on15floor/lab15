from flask import request, redirect, render_template, abort
from flask_login import login_user, login_required, logout_user
from markupsafe import Markup

from app import app
from core.auth import auth_user
from core.models import NoSmokingStages, Blog, Chrods, Birthdays
from utils.utils import get_markdown
from utils.binance_wrap import Binance
from utils.tinkoff_wrap import Tinkoff
from utils.git import get_gitlog
from utils.mongodb_wrap import MongoDB
from utils.beget_wrap import Crontab


UNITY_GAMES = ('simple_cube', 'delimiter', 'kot_guide')
HINTS = ('bash', 'git', 'markdown', 'python', 'sql', 'vim')
MUSIC_INSTRUMENT = ('ukulele', 'guitar')


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
def utils_hints(hint):
    if hint in HINTS:
        doc_content = Markup(get_markdown(f'{hint}.md'))
        return render_template('utils/hints.html', doc=doc_content)
    abort(404)


@app.route('/utils/converter')
def utils_converter():
    return render_template('utils/converter.html')


@app.route('/utils/no_smoking', methods=['GET', 'POST'])
def utils_no_smoking():
    obj = NoSmokingStages()

    data = obj.get_statistic() \
        if request.method == 'GET' \
        else obj.get_statistic(dict(list(request.form.items())))

    return render_template('utils/no_smoking.html', data=data,
                           no_smoking_db=obj.get_stages())


@app.route('/blog')
def blog():
    page = request.args.get('page')
    page = int(page) if page and page.isdigit() else 1
    return render_template('blog/index.html', blog=Blog(page=page))


@app.route('/blog/<int:post_id>')
def blog_post(post_id):
    post = Blog().get_post(post_id)
    return render_template('blog/post.html', post=post)


@app.route('/blog/create', methods=['POST', 'GET'])
@login_required
def blog_create():
    if request.method == 'GET':
        return render_template('blog/post_edit.html')

    context = dict(list(request.form.items()))
    Blog().commit_post(context)
    return redirect('/blog')


@app.route('/blog/<int:pos_id>/del')
@login_required
def blog_post_del(pos_id):
    Blog().delete_post(pos_id)
    return redirect('/blog')


@app.route('/blog/<int:post_id>/update', methods=['POST', 'GET'])
@login_required
def blog_post_update(post_id):
    if request.method == 'GET':
        return render_template('blog/post_edit.html',
                               post=Blog().get_post(post_id))

    context = dict(list(request.form.items()))
    Blog().update_post(post_id, context)
    return redirect(f'/blog/{post_id}')


@app.route('/chords/<string:instrument>')
def chords(instrument):
    if instrument in MUSIC_INSTRUMENT:
        obj = Chrods(instrument)
        instrument_name = obj.get_instrument_name_rus()
        q = request.args.get('q')   # seraching
        songs = obj.search(q) if q else obj.get_songs()

        return render_template('chords/index.html',
                               songs=songs, instrument=instrument_name)
    abort(404)


@app.route('/chords/<int:song_id>')
def chords_song(song_id):
    return render_template('chords/song.html', song=Chrods().get_song(song_id))


@app.route('/chords/create', methods=['POST', 'GET'])
@login_required
def chords_create():
    if request.method == 'GET':
        return render_template('chords/song_edit.html')

    context = dict(list(request.form.items()))
    Chrods().commit_song(context)
    return redirect(f'/chords/{MUSIC_INSTRUMENT[1]}')


@app.route('/chords/<int:song_id>/del')
@login_required
def chords_song_del(song_id):
    Chrods().delete_song(song_id=song_id)
    return redirect(f'/chords/{MUSIC_INSTRUMENT[1]}')


@app.route('/chords/<int:song_id>/update', methods=['POST', 'GET'])
@login_required
def chords_song_update(song_id):
    if request.method == 'GET':
        return render_template('chords/song_edit.html',
                               song=Chrods().get_song(song_id))

    context = dict(list(request.form.items()))
    Chrods().update_song(song_id, context)
    return redirect(f'/chords/{MUSIC_INSTRUMENT[1]}')


@app.route('/money/crypto')
@login_required
def money_crypto():
    binance = Binance()
    return render_template('money/crypto.html',
                           wallet=binance.get_wallet(),
                           deposit=binance.get_deposits())


@app.route('/money/stocks')
@login_required
def money_stocks():
    return render_template('money/stocks.html',
                           portfolio=Tinkoff().get_portfolio())


@app.route('/birthdays/<string:scope>/')
@login_required
def birthdays(scope):
    obj = Birthdays()
    q = request.args.get('q')  # seraching
    data = obj.search(q) if q else obj.get_birthdays(scope)
    return render_template('birthdays/index.html', birthdays=data)


@app.route('/birthdays/create', methods=['POST', 'GET'])
@login_required
def birthdays_create():
    if request.method == 'GET':
        return render_template('birthdays/bd_details.html')

    context = dict(list(request.form.items()))
    Birthdays().commit_birthday(context)
    return redirect('/birthdays/month/')


@app.route('/birthdays/<int:birthday_id>/del')
@login_required
def birthdays_del(birthday_id):
    Birthdays().delete_birthday(birthday_id)
    return redirect('/birthdays/month/')


@app.route('/birthdays/<int:birthday_id>/update', methods=['POST', 'GET'])
@login_required
def birthdays_update(birthday_id):
    if request.method == 'GET':
        return render_template('birthdays/bd_details.html',
                               birthday=Birthdays().get_birthday(birthday_id))

    context = dict(list(request.form.items()))
    Birthdays().update_birthday(birthday_id, context)
    return redirect('/birthdays/month/')


@app.route('/dashboard/gitlog/')
@login_required
def dashboard_gitlog():
    return render_template('dashboard/gitlog.html', git_log=get_gitlog())


@app.route('/dashboard/mongolog/<string:state>')
@login_required
def dashboard_mongolog(state):
    logs = []
    mongo = MongoDB()
    if state == 'all':
        logs = mongo.get_logs_all()
    elif state == 'errors':
        logs = mongo.get_logs_errors()

    return render_template('dashboard/mongologs.html', mongo_log=list(logs))


@app.route('/dashboard/crontab/')
@login_required
def dashboard_crontab():
    tasks = Crontab().tasks_get()
    return render_template('dashboard/crontab.html', crontab_tasks=tasks)


@app.route('/dashboard/crontab/<int:task_id>/del')
@login_required
def dashboard_crontab_del(task_id):
    Crontab().task_del(task_id)
    return redirect('/dashboard/crontab/')


@app.route('/dashboard/crontab/<int:task_id>/stop')
@login_required
def dashboard_crontab_stop(task_id):
    Crontab().task_change_state(task_id, 1)
    return redirect('/dashboard/crontab/')


@app.route('/dashboard/crontab/<int:task_id>/start')
@login_required
def dashboard_crontab_start(task_id):
    Crontab().task_change_state(task_id, 0)
    return redirect('/dashboard/crontab/')

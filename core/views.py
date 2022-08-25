import traceback

from markupsafe import Markup
from werkzeug.wrappers import Response
from flask_login import login_required, logout_user
from flask import request, redirect, render_template, abort, jsonify

from app import app
from core.auth import auth_user
from core.models import (
    NoSmokingStages, Blog, Chrods, Birthdays, Reminerds, CarsManager)
from core.decorators import api_token_required
from services.telegram import TBot
from services.beget import BegetApi
from services.binance import Binance
from utils.git import get_gitlog
from utils.mongodb_wrap import MongoDB
from utils.apple_music import playlist_data_gen
from utils.utils import get_markdown, get_ip, Calendar, Statistic


UNITY_GAMES = ('simple_cube', 'delimiter', 'kot_guide')
HINTS = ('bash', 'git', 'markdown', 'python', 'sql', 'vim')
MUSIC_INSTRUMENT = ('ukulele', 'guitar')
CURRENCIES = {'RUB': '🇷🇺', 'USD': '🇺🇸', 'EUR': '🇪🇺', 'UAH': '🇺🇦',
              'KZT': '🇰🇿', 'TRY': '🇹🇷', 'AMD': '🇦🇲'}


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/ping')
def ping():
    return jsonify(get_ip(request))


# noinspection PyUnusedLocal
@app.errorhandler(404)
def page_not_fount(error):
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_error(error):
    e = {'error_code': error.code, 'traceback': traceback.format_exc()}
    TBot().send_error(e, get_ip(request))
    return render_template('500.html'), 500


@app.route('/login', methods=['POST'])
def login():
    return jsonify(auth_user(request.json))


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
        return render_template('unity/privacy_policy.html',
                               game=game.replace('_', ' ').title())
    abort(404)


@app.route('/utils/hints/<string:hint>')
def utils_hints(hint):
    if hint in HINTS:
        return render_template('utils/hints.html',
                               doc=Markup(get_markdown(f'{hint}.md')))
    abort(404)


@app.route('/utils/converter')
def utils_converter():
    return render_template('utils/converter.html', currencies=CURRENCIES)


@app.route('/utils/no_smoking', methods=['GET', 'POST'])
def utils_no_smoking():
    obj = NoSmokingStages()
    context = None if request.method == 'GET' else dict(request.form.items())

    return render_template('utils/no_smoking.html', stages=obj.get_stages(),
                           data=obj.get_statistic(context))


@app.route('/utils/apple_music', methods=['GET', 'POST'])
def utils_apple_music():
    if request.method == 'GET':
        return render_template('utils/apple_music.html')

    playlist_link = request.form.get('playlist')
    response = Response(playlist_data_gen(playlist_link), mimetype='text/csv')
    response.headers.set(
        "Content-Disposition", "attachment", filename="playlist.csv")
    return response


@app.route('/utils/calendar', methods=['GET', 'POST'])
def utils_calendar():
    obj = Calendar()
    calculate = None if request.method == 'GET' \
        else obj.calculate(dict(request.form.items()))

    return render_template('utils/calendar.html',
                           content=obj.gen(), calculate=calculate)


@app.route('/blog')
@login_required
def blog():
    page = request.args.get('page')
    page = int(page) if page and page.isdigit() else 1
    return render_template('blog/index.html', blog=Blog(page=page))


@app.route('/blog/<int:post_id>')
@login_required
def blog_post(post_id):
    return render_template('blog/post.html',
                           post=Blog().get_post(post_id))


@app.route('/blog/create', methods=['POST', 'GET'])
@login_required
def blog_create():
    if request.method == 'GET':
        return render_template('blog/post_edit.html')

    Blog().commit_post(context=dict(request.form.items()))
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

    Blog().update_post(post_id, context=dict(request.form.items()))
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

    Chrods().commit_song(context=dict(request.form.items()))
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

    Chrods().update_song(song_id, context=dict(request.form.items()))
    return redirect(f'/chords/{MUSIC_INSTRUMENT[1]}')


@app.route('/crypto')
@login_required
def crypto():
    binance = Binance()
    return render_template('admin/crypto.html', wallet=binance.get_wallet(),
                           deposit=binance.get_deposits())


@app.route('/reminders', methods=['POST', 'GET'])
@login_required
def reminders():
    obj = Reminerds()
    if request.method == 'POST':
        obj.commit_remind(context=dict(request.form.items()))

    return render_template('admin/reminders.html',
                           reminders=obj.get_reminders())


@app.route('/cars', methods=['GET'])
@login_required
def cars():
    obj = CarsManager()
    return render_template('admin/cars.html', cars=obj.get_data())


@app.route('/reminders/<int:remind_id>/del')
@login_required
def reminders_del(remind_id):
    Reminerds().delete_remind(remind_id)
    return redirect('/reminders')


@app.route('/reminders/<int:remind_id>/change_status')
@login_required
def reminders_change_status(remind_id):
    Reminerds().change_status(remind_id)
    return redirect('/reminders')


@app.route('/birthdays/<string:scope>/')
@login_required
def birthdays(scope):
    obj = Birthdays()
    q = request.args.get('q')  # seraching
    data = obj.search(q) if q else obj.get_birthdays(scope)
    return render_template('admin/birthdays/index.html', birthdays=data)


@app.route('/birthdays/create', methods=['POST', 'GET'])
@login_required
def birthdays_create():
    if request.method == 'GET':
        return render_template('admin/birthdays/bd_details.html')

    Birthdays().commit_birthday(context=dict(request.form.items()))
    return redirect('/birthdays/month/')


@app.route('/birthdays/<int:birthday_id>/del')
@login_required
def birthdays_del(birthday_id):
    Birthdays().delete_birthday(birthday_id)
    return redirect('/birthdays/month/')


@app.route('/birthdays/<int:birthday_id>/update', methods=['POST', 'GET'])
@login_required
def birthdays_update(birthday_id):
    obj = Birthdays()
    if request.method == 'GET':
        return render_template('admin/birthdays/bd_details.html',
                               birthday=obj.get_birthday(birthday_id))

    obj.update_birthday(birthday_id, context=dict(request.form.items()))
    return redirect('/birthdays/month/')


@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard/index.html', data=Statistic().get())


@app.route('/dashboard/gitlog/')
@login_required
def dashboard_gitlog():
    return render_template('dashboard/gitlog.html', git_log=get_gitlog())


@app.route('/dashboard/mongolog/<string:state>')
@login_required
def dashboard_mongolog(state):
    logs = MongoDB().get_logs_errors() \
        if state == 'errors' else MongoDB().get_logs_all()
    return render_template('dashboard/mongologs.html', mongo_logs=logs)


@app.route('/dashboard/crontab/')
@login_required
def dashboard_crontab():
    tasks = BegetApi().get_tasks()
    return render_template('dashboard/crontab.html', crontab_tasks=tasks)


@app.route('/dashboard/crontab/<int:task_id>/del')
@login_required
def dashboard_crontab_del(task_id):
    BegetApi().task_del(task_id)
    return redirect('/dashboard/crontab/')


@app.route('/dashboard/crontab/<int:task_id>/stop')
@login_required
def dashboard_crontab_stop(task_id):
    BegetApi().task_change_state(task_id, 1)
    return redirect('/dashboard/crontab/')


@app.route('/dashboard/crontab/<int:task_id>/start')
@login_required
def dashboard_crontab_start(task_id):
    BegetApi().task_change_state(task_id, 0)
    return redirect('/dashboard/crontab/')


@app.route('/api/v1.0/send_daily')
@api_token_required
def api_send_daily():
    result = TBot().send_daily()
    status = MongoDB().save_log_from_request(
        request, f'Daily report sent: {result}')
    return jsonify(status)


@app.route('/api/v1.0/get_ios_sale')
@api_token_required
def api_get_ios_sale():
    count = TBot().send_ios_sale()
    status = MongoDB().save_log_from_request(
        request, f'Apptime fresh sales: {count}')
    return jsonify(status)

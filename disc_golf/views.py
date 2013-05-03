import os
from functools import wraps
from flask import request, render_template, redirect, \
    url_for, session, g, flash, Blueprint
from config import app
from disc_golf.models import Course, ScoreCard
from forms import LoginForm, ScoreForm

from flask.ext.openid import OpenID
from config import OPENID_PROVIDERS
from models import User


index_page = Blueprint(
    'index_page', __name__,
    template_folder='templates'
)


############################ OPENID ######################
basedir = os.path.abspath(os.path.dirname(__file__))
oid = OpenID(app, os.path.join(basedir, 'tmp'))


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if g.user is None:
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function


@app.route('/success', methods=['GET', 'POST'])
def success():
    return "success!"


@app.before_request
def before_request():
    g.user = None
    if 'email' in session:
        g.user = User.objects.get_or_404(email=session['email'])


@app.route('/login', methods=['GET', 'POST'])
@oid.loginhandler
def login():
    if g.user is not None and g.user.is_authenticated():
        return redirect(url_for('posts.list'))
    form = LoginForm()
    if form.validate_on_submit():
        session['remember_me'] = form.remember_me.data
        return oid.try_login(
            form.openid.data, ask_for=['nickname', 'email']
        )
    return render_template(
        'login.html',
        next=oid.get_next_url(),
        error=oid.fetch_error(),
        title='Sign In',
        form=form,
        providers=OPENID_PROVIDERS
    )


@oid.after_login
def after_login(resp):
    # if fields empty, flash error message
    if resp.email is None or resp.email == "":
        flash('Invalid login. Please try again.')
        redirect(url_for('login'))
    try:
        # get user object based on request
        user = User.objects.get(email=resp.email)
    except User.DoesNotExist:
        return redirect(url_for('login'))
    """
    if user is None:
        username = resp.nickname
        if username is None or username == "":
            username = resp.email.split('@')[0]
        user = User(username=username, email=resp.email, role=ROLE_USER)
        session['username'] = username

    remember_me = False
    if 'remember_me' in session:
        remember_me = session['remember_me']
        session.pop('remember_me', None)
    return redirect(request.args.get('next') or url_for('admin.list'))
    """
    session['user'] = user
    session['email'] = resp.email
    if user is not None:
        flash(u'Successfully signed in')
        g.user = user
        return redirect(oid.get_next_url())
    else:
        flash(u'Your credentials have not been recognized')
        return redirect(url_for('login'))
    return redirect(url_for('success', next=oid.get_next_url(),
                            username=resp.nickname,
                            email=resp.email))


@app.route('/logout')
def logout():
    session.pop('email', None)
    session.pop('remember_me', None)
    flash(u'You were signed out')
    return redirect(oid.get_next_url())
######################## END OPENID ######################


@index_page.route('/')
#@login_required
def index():
    courses = Course.objects.all()
    return render_template(
        'index.html',
        title='Disc Golf - Home',
        courses=courses
    )


@app.route('/course/<slug>/', methods=['GET', 'POST'])
def course_detail(slug):
    course = Course.objects.get(slug=slug)
    # score form
    form = ScoreForm(request.form)
    if request.method == 'POST' and form.validate():
        print g.user
        course_score = ScoreCard(
            user=g.user,
            score=form.score.data,
            baskets=form.baskets.data,
        )
        course_score.save()
        flash('Thanks for submitting a score!')
    # get course data
    data = {'nine_sum': 0, 'eighteen_sum': 0}
    nine_count = 0
    eighteen_count = 0
    all_scores = ScoreCard.objects.all()

    if all_scores:
        for card in all_scores:
            if card.baskets == 9 and card.score:
                nine_count += 1
                data['nine_sum'] += card.score
            elif card.baskets == 18 and card.score:
                eighteen_count += 1
                data['eighteen_sum'] += card.score

    if nine_count > 0:
        data['nine_basket_avg'] = data['nine_sum'] / nine_count
    if eighteen_count > 0:
        data['eighteen_basket_avg'] = data['eighteen_sum'] / eighteen_count

    return render_template(
        'course_detail.html',
        title='Course Detail -' + course.name,
        course=course,
        form=form,
        data=data,
    )

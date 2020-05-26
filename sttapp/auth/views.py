import datetime

from flask import flash, Blueprint, session, request, url_for, render_template, redirect, current_app
from itsdangerous import TimedJSONWebSignatureSerializer
from itsdangerous import SignatureExpired, BadSignature
from flask_login import login_user, current_user, login_required, logout_user
# from mongoengine.queryset.visitor import Q

from sttapp.users.models import SttUser, InvitationInfo
from sttapp.base.enums import FlashCategory
from sttapp.base.utils import get_obj_or_404
from .forms import SignupForm, InvitationForm, LoginForm
from .services.mail import send_mail
from .services.google import get_request_uri, callback
from .enums import Expiration, SocialLogin

import iso8601


bp = Blueprint('auth', __name__, url_prefix='/auth')


@bp.route('/invite/', methods=["GET", "POST"])
@login_required
def invite():
    form = InvitationForm(request.form)
    if form.validate_on_submit():

        s = TimedJSONWebSignatureSerializer(
            current_app.config['SECRET_KEY'], expires_in=Expiration.invitation_expire_days*3600*24
        )

        invitation_token = s.dumps({
            'email': form.email.data,
            'user_id': str(current_user.id), 
            'invited_at': datetime.datetime.utcnow().isoformat(),
        })
        
        if len(invitation_token) >= 1700:
            flash("邀請註冊連結生成發生問題，請洽管理員", FlashCategory.error)
            return redirect(url_for('auth.invite'))

        send_mail(
            subject="邀請您註冊成大山協網站帳號",
            recipients=[form.email.data, ],
            html_body=render_template(
                "auth/invitation_email.html",
                url=request.host_url + url_for("auth.signup_choices", invitation_token=invitation_token),
                days=Expiration.invitation_expire_days)
        )
        flash(
            '已寄出邀請信，請於{}天內申請帳號'.format(Expiration.invitation_expire_days), 
            FlashCategory.info
        )
        return redirect(url_for('auth.invite'))
    return render_template('auth/invitation_form.html', form=form)


def validate_token(token):

    if not token:
        flash("連結載入失敗，請重新點擊邀請信中的連結", FlashCategory.error)
        return None

    s = TimedJSONWebSignatureSerializer(current_app.config['SECRET_KEY'])
    try:
        invitation_info_dict = s.loads(token)
    except SignatureExpired:
        flash("該連結已經過期~請申請新的註冊連結", FlashCategory.error)
        return None
    except BadSignature:
        flash("該連結為無效連結~請重新申請", FlashCategory.error)
        return None

    # 避免同一token被重複註冊的情況
    if SttUser.objects(invitation_info__token=token):
        flash("該連結已經被註冊過了喔~請申請新的註冊連結", FlashCategory.warn)
        return None
    return invitation_info_dict


@bp.route('/signup_choices/<string:invitation_token>/')
def signup_choices(invitation_token):

    session['invitation_token'] = invitation_token

    invitation_info_dict = validate_token(invitation_token)
    if not invitation_info_dict:
        return redirect("/")
    return render_template('auth/signup_choices.html')


@bp.route('/google_signup/')
def google_signup():

    return redirect(get_request_uri(current_app, request.base_url))
    # print('~~~!!!!', get_request_uri(current_app, request.base_url))
    # return redirect("/")


@bp.route('/google_signup/callback/')
def google_callback():
    
    code = request.args.get("code")

    google_user_data = callback(
        app=current_app, code=code, url=request.url, base_url=request.base_url)
    
    if not google_user_data:
        flash("您的google帳戶為失效狀態，請使用其他方式註冊", FlashCategory.error)
        return redirect(url_for("auth.signup_choices", invitation_token=session.get('invitation_token')))

    # del invitation email session
    invitation_info_dict = validate_token(session.get('invitation_token'))
    if not invitation_info_dict:
        return redirect("/")

    user = SttUser(
        username=google_user_data.get("users_name"),
        email=google_user_data.get("users_email"),
        social_login_with=SocialLogin.google,
        social_login_id=str(google_user_data.get("unique_id")),
        # profile_img=google_user_data.get("picture"),
        created_at=datetime.datetime.utcnow(),
        invitation_info=InvitationInfo(
            email=invitation_info_dict['email'],
            token=session["invitation_token"],
            invited_at=iso8601.parse_date(invitation_info_dict['invited_at']),
            invited_by=invitation_info_dict['user_id']
        )
    )
    try:
        user.save()
    except Exception as e:
        flash(e, FlashCategory.error)
        return redirect("/")
    else:
        session.pop("invitation_token", None)
        return redirect(url_for("auth.post_signup", user_id=user.id))


@bp.route('/post_signup/<string:user_id>/',methods=["GET", "POST"])
def post_signup(user_id):
    
    user = get_obj_or_404(SttUser, id=user_id)
    flash("you are {}, {}, {}".format(user_id, user.username, user.email), FlashCategory.info)
    return redirect(url_for("auth.login"))


@bp.route('/signup/', methods=["GET", "POST"])
def signup():

    invitation_info_dict = validate_token(session.get('invitation_token'))

    if not invitation_info_dict:
        return redirect("/")
    
    form = SignupForm(request.form)

    if request.method == "POST":
        if form.validate_on_submit():
            user = SttUser(
                username=form.username.data,
                email=invitation_info_dict['email'],
                created_at=datetime.datetime.utcnow(),
                invitation_info=InvitationInfo(
                    email=invitation_info_dict['email'],
                    token=session["invitation_token"],
                    invited_at=iso8601.parse_date(invitation_info_dict['invited_at']),
                    invited_by=invitation_info_dict['user_id']
                )
            )
            user.password = form.password.data
            user.save()

            session.pop("invitation_token", None)
            
            flash('註冊成功！歡迎光臨~~~已登入', FlashCategory.success)
            login_user(user, remember=True, 
                duration=datetime.timedelta(days=Expiration.remember_cookie_duration_days))
            return redirect('/')
        else:
            flash('格式錯誤', FlashCategory.error)
    return render_template('auth/signup.html', form=form, email=invitation_info_dict['email'])


@bp.route('/login/', methods=["GET", "POST"])
def login():
    form = LoginForm(request.form)
    if request.method == "POST":
        if form.validate_on_submit():
            user = form.user_in_db
            
            login_user(user, remember=True, 
                duration=datetime.timedelta(days=Expiration.remember_cookie_duration_days))
            SttUser.objects(id=user.id).update_one(last_login_at=datetime.datetime.utcnow())

            next_ = request.args.get('next')
            # if not is_safe_url(next_):
            #     return redirect('/')
            
            flash('登入成功！歡迎光臨 {}'.format(current_user.username), FlashCategory.info)
            return redirect(next_ or '/')
        else:
            flash('登入失敗', FlashCategory.error)
    return render_template('auth/login.html', form=form)


@bp.route('/google_login/')
def google_login():
    pass


@bp.route('/logout/')
@login_required
def logout():
    logout_user()
    flash('已登出帳號', FlashCategory.success)
    return redirect("/")

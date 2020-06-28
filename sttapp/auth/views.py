import datetime

from flask import flash, Blueprint, session, request, url_for, render_template, redirect, current_app
from itsdangerous import TimedJSONWebSignatureSerializer
from itsdangerous import SignatureExpired, BadSignature

from mongoengine.errors import NotUniqueError
from flask_login import login_user, current_user, login_required, logout_user

from sttapp.users.models import SttUser, InvitationInfo
from sttapp.base.enums import FlashCategory, Identity
from sttapp.tasks import send_mail
from .forms import SttSignupForm, InvitationForm, LoginForm, PostSignupForm
from .services.google import get_request_uri, callback, google_signup_action, google_login_action
from .enums import Expiration, SocialLogin, SocialAction

import iso8601


bp = Blueprint('auth', __name__, url_prefix='/auth')


@bp.route('/invite/', methods=["GET", "POST"])
@login_required
def invite():
    form = InvitationForm(request.form)
    if request.method == "POST" and form.validate_on_submit():

        s = TimedJSONWebSignatureSerializer(
            current_app.config['SECRET_KEY'], expires_in=Expiration.invitation_expire_days*3600*24
        )

        invitation_token = s.dumps({
            'email': form.email.data,
            'user_id': str(current_user.id),
            'invited_at': datetime.datetime.utcnow().isoformat(),
        })

        if len(invitation_token) >= 1700:
            flash("邀請註冊連結生成發生問題，請洽管理員", FlashCategory.ERROR)
            return redirect(url_for('auth.invite'))

        send_mail.delay(
            subject="邀請您註冊成大山協網站帳號",
            recipients=[form.email.data, ],
            html_body=render_template(
                "auth/invitation_email.html",
                url=request.host_url.rstrip(
                    "/") + url_for("auth.signup_choices", invitation_token=invitation_token),
                days=Expiration.invitation_expire_days)
        )
        flash(
            '已寄出邀請信，請於{}天內申請帳號'.format(Expiration.invitation_expire_days),
            FlashCategory.INFO
        )
        return redirect(url_for('auth.invite'))
    return render_template('auth/invitation_form.html', form=form)


def validate_token(token):

    if not token:
        flash("連結載入失敗，請重新點擊邀請信中的連結", FlashCategory.ERROR)
        return None

    s = TimedJSONWebSignatureSerializer(current_app.config['SECRET_KEY'])
    try:
        invitation_info_dict = s.loads(token)
    except SignatureExpired:
        flash("該連結已經過期~請申請新的註冊連結", FlashCategory.ERROR)
        return None
    except BadSignature:
        flash("該連結為無效連結~請重新申請", FlashCategory.ERROR)
        return None

    # 避免同一token被重複註冊的情況
    if SttUser.objects(invitation_info__token=token):
        flash("該連結已經被註冊過了喔~請申請新的註冊連結", FlashCategory.WARNING)
        return None
    invitation_info_dict.update({"token": token})
    return invitation_info_dict


@bp.route('/signup_choices/<string:invitation_token>/')
def signup_choices(invitation_token):

    invitation_info_dict = validate_token(invitation_token)
    if not invitation_info_dict:
        return redirect("/")
    session['invitation_token'] = invitation_token
    return render_template('auth/signup_choices.html')


@bp.route('/google_signup/')
def google_signup():

    session["social_action"] = SocialAction.signup
    return redirect(get_request_uri(current_app, request))


@bp.route('/google/callback/')
def google_callback():

    google_user_data = callback(current_app, request)
    social_action = session.get("social_action")
    session.pop("social_action", None)  # drop session

    if not google_user_data:
        flash("您的google帳戶為失效狀態，請使用其他方式登入或註冊", FlashCategory.ERROR)
        return redirect(url_for("auth.signup_choices", invitation_token=session.get('invitation_token')))

    if social_action == SocialAction.signup:

        invitation_info_dict = validate_token(session.get('invitation_token'))
        session.pop("invitation_token", None)

        if not invitation_info_dict:
            return redirect("/")

        try:
            user = google_signup_action(google_user_data, invitation_info_dict)
        except NotUniqueError:
            flash("您使用的google帳號的信箱已經被註冊過了，請使用google登入", FlashCategory.INFO)
            return redirect(url_for("auth.login"))
        else:
            flash("最後一步！再填寫詳細資料後就完成囉！", FlashCategory.INFO)

            # login user
            login_user(user, remember=True, duration=datetime.timedelta(
                days=Expiration.remember_cookie_duration_days))
            SttUser.objects(id=user.id).update_one(
                last_login_at=datetime.datetime.utcnow())
            return redirect(url_for("auth.post_signup"))

    elif social_action == SocialAction.login:

        try:
            user = google_login_action(google_user_data)
        except SttUser.DoesNotExist:
            flash("您尚未註冊，無法登入喔，請向山協隊員申請註冊連結", FlashCategory.WARNING)
            return redirect("/")

        login_user(user, remember=True, duration=datetime.timedelta(
            days=Expiration.remember_cookie_duration_days))
        SttUser.objects(id=user.id).update_one(
            last_login_at=datetime.datetime.utcnow())

        next_ = request.args.get('next')
        # if not is_safe_url(next_):
        # return redirect('/')
        flash('登入成功！歡迎光臨', FlashCategory.SUCCESS)
        return redirect(next_ or '/')

    else:
        flash("發生奇怪問題，請再試一次，或是聯絡系統管理員", FlashCategory.ERROR)
        return redirect("/")


@bp.route('/post_signup/', methods=["GET", "POST"])
@login_required
def post_signup():

    form = PostSignupForm(request.form)
    form.username.data = current_user.username

    if request.method == "POST":
        if form.validate_on_submit():
            SttUser.objects(id=current_user.id).update_one(
                username=form.username.data,
                name=form.name.data or None,
                birthday=form.birthday_dt or None,
                cellphone_number=form.cellphone_number.data or None,
                department=form.department.data or None,
                graduation_year=form.graduation_year.data or None,
                group=form.group.data,
                position=form.position.data,
                identity=form.identity.data,
                level=form.level.data,
                introduction=form.introduction.data,
                updated_at=datetime.datetime.utcnow()
            )
            flash("恭喜註冊完成，已登入", FlashCategory.SUCCESS)
            flash('重要提醒：若您為在校生，請盡速填寫出隊資訊以利領隊開隊', FlashCategory.WARNING)
            return redirect("/")
        else:
            flash('格式錯誤', FlashCategory.ERROR)
    return render_template("auth/post_signup.html", form=form)


@bp.route('/signup/', methods=["GET", "POST"])
def signup():

    invitation_info_dict = validate_token(session.get('invitation_token'))

    if not invitation_info_dict:
        return redirect("/")

    form = SttSignupForm(request.form)

    if request.method == "POST":
        if form.validate_on_submit():
            user = SttUser(
                username=form.username.data,
                name=form.name.data or None,
                birthday=form.birthday_dt or None,
                cellphone_number=form.cellphone_number.data or None,
                department=form.department.data or None,
                graduation_year=form.graduation_year.data or None,
                group=form.group.data,
                position=form.position.data,
                level=form.level.data,
                identity=form.identity.data,
                email=invitation_info_dict['email'],
                created_at=datetime.datetime.utcnow(),
                updated_at=datetime.datetime.utcnow(),
                invitation_info=InvitationInfo(
                    email=invitation_info_dict['email'],
                    token=invitation_info_dict['token'],
                    invited_at=iso8601.parse_date(
                        invitation_info_dict['invited_at']),
                    invited_by=invitation_info_dict['user_id']
                )
            )
            user.password = form.password.data
            user.save()

            session.pop("invitation_token", None)

            flash("恭喜註冊完成，已登入", FlashCategory.SUCCESS)
            flash('重要提醒：若您為在校生，請盡速至個人頁面的"出隊用資料"填寫/匯入出隊資訊，以利領隊開隊', FlashCategory.WARNING)
            login_user(user, remember=True,
                       duration=datetime.timedelta(days=Expiration.remember_cookie_duration_days))
            SttUser.objects(id=user.id).update_one(
                last_login_at=datetime.datetime.utcnow())
            return redirect('/')
        else:
            flash('格式錯誤', FlashCategory.ERROR)
    return render_template('auth/signup.html', form=form, email=invitation_info_dict['email'])


@bp.route('/google_login/')
def google_login():

    session["social_action"] = SocialAction.login
    return redirect(get_request_uri(current_app, request))


@bp.route('/login/', methods=["GET", "POST"])
def login():
    form = LoginForm(request.form)
    if request.method == "POST":
        if form.validate_on_submit():
            user = form.user_in_db

            login_user(user, remember=True,
                       duration=datetime.timedelta(days=Expiration.remember_cookie_duration_days))
            SttUser.objects(id=user.id).update_one(
                last_login_at=datetime.datetime.utcnow())

            next_ = request.args.get('next')
            # if not is_safe_url(next_):
            #     return redirect('/')

            if not user.member_id and user.identity == Identity.get_map()[Identity.IN_NCKU]:
                flash('您尚未連結/建立出隊用資料，請盡速至個人頁面的"出隊用資料"操作，以利領隊開隊', FlashCategory.WARNING)

            flash('登入成功！歡迎光臨', FlashCategory.SUCCESS)
            return redirect(next_ or url_for("user.detail", user_id=user.id))
        else:
            flash('登入表格有誤，請重新登入', FlashCategory.ERROR)
    return render_template('auth/login.html', form=form)


@bp.route('/logout/')
@login_required
def logout():
    logout_user()
    flash('已登出帳號', FlashCategory.SUCCESS)
    return redirect("/")

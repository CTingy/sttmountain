import json
import datetime
from flask import url_for
from oauthlib.oauth2 import WebApplicationClient
from sttapp.users.models import SttUser, InvitationInfo
from sttapp.auth.enums import SocialLogin
import requests
import iso8601


def get_google_provider_cfg(app):
    return requests.get(app.config["GOOGLE_DISCOVERY_URL"]).json()


def get_request_uri(app, request):
    # OAuth2 client setup
    client = WebApplicationClient(app.config["GOOGLE_CLIENT_ID"])

    # Find out what URL to hit for Google login
    google_provider_cfg = get_google_provider_cfg(app)
    authorization_endpoint = google_provider_cfg["authorization_endpoint"]

    # Use library to construct the request for login and provide
    # scopes that let you retrieve user's profile from Google
    request_uri = client.prepare_request_uri(
        authorization_endpoint,
        redirect_uri=request.host_url.rstrip(
            "/") + url_for("auth.google_callback"),
        scope=["openid", "email", "profile"],
    )
    return request_uri


def callback(app, request):
    # Get authorization code Google sent back to you
    code = request.args.get("code")
    client = WebApplicationClient(app.config["GOOGLE_CLIENT_ID"])

    # Find out what URL to hit to get tokens that allow you to ask for
    # things on behalf of a user
    google_provider_cfg = get_google_provider_cfg(app)
    token_endpoint = google_provider_cfg["token_endpoint"]

    # Prepare and send request to get tokens! Yay tokens!
    token_url, headers, body = client.prepare_token_request(
        token_endpoint,
        authorization_response=request.url,
        redirect_url=request.base_url,
        code=code,
    )
    token_response = requests.post(
        token_url,
        headers=headers,
        data=body,
        auth=(app.config["GOOGLE_CLIENT_ID"],
              app.config["GOOGLE_CLIENT_SECRET"]),
    )

    # Parse the tokens!
    client.parse_request_body_response(json.dumps(token_response.json()))

    # Now that we have tokens (yay) let's find and hit URL
    # from Google that gives you user's profile information,
    # including their Google Profile Image and Email
    userinfo_endpoint = google_provider_cfg["userinfo_endpoint"]
    uri, headers, body = client.add_token(userinfo_endpoint)
    userinfo_response = requests.get(uri, headers=headers, data=body)

    # We want to make sure their email is verified.
    # The user authenticated with Google, authorized our
    # app, and now we've verified their email through Google!
    if userinfo_response.json().get("email_verified"):
        return {
            "unique_id": userinfo_response.json()["sub"],
            "users_name": userinfo_response.json()["given_name"],
            "users_email": userinfo_response.json()["email"],
            "picture": userinfo_response.json()["picture"],
        }
    else:
        return None


def google_signup_action(google_user_data, invitation_info_dict):
    user = SttUser(
        username=google_user_data.get("users_name"),
        email=google_user_data.get("users_email"),
        social_login_with=SocialLogin.google,
        social_login_id=str(google_user_data.get("unique_id")),
        # profile_img=google_user_data.get("picture"),
        created_at=datetime.datetime.utcnow(),
        invitation_info=InvitationInfo(
            email=invitation_info_dict['email'],
            token=invitation_info_dict['token'],
            invited_at=iso8601.parse_date(invitation_info_dict['invited_at']),
            invited_by=invitation_info_dict['user_id']
        )
    )
    if SttUser.objects(social_login_with=user.social_login_with,
                       social_login_id=user.social_login_id):
        raise ValueError("this social login has already existed in DB")
    user.save()
    return user


def google_login_action(google_user_data):

    user = SttUser.objects.get(social_login_id=str(google_user_data.get("unique_id")),
                               social_login_with=SocialLogin.google)
    # 檢查是否更換信箱
    if user.email != google_user_data.get("users_email"):
        SttUser.objects(id=user.id).update_one(
            email=google_user_data.get("users_email"))

    return user

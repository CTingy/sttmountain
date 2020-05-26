import json
from oauthlib.oauth2 import WebApplicationClient
import requests


def get_google_provider_cfg(app):
    return requests.get(app.config["GOOGLE_DISCOVERY_URL"]).json()


def get_request_uri(app, base_url):
    # OAuth2 client setup
    client = WebApplicationClient(app.config["GOOGLE_CLIENT_ID"])
    
    # Find out what URL to hit for Google login
    google_provider_cfg = get_google_provider_cfg(app)
    authorization_endpoint = google_provider_cfg["authorization_endpoint"]

    # Use library to construct the request for login and provide
    # scopes that let you retrieve user's profile from Google
    request_uri = client.prepare_request_uri(
        authorization_endpoint,
        redirect_uri=base_url + "callback/",
        scope=["openid", "email", "profile"],
    )
    return request_uri


def callback(app, code, url, base_url):
    # Get authorization code Google sent back to you
    
    client = WebApplicationClient(app.config["GOOGLE_CLIENT_ID"])

    # Find out what URL to hit to get tokens that allow you to ask for
    # things on behalf of a user
    google_provider_cfg = get_google_provider_cfg(app)
    token_endpoint = google_provider_cfg["token_endpoint"]

    # Prepare and send request to get tokens! Yay tokens!
    token_url, headers, body = client.prepare_token_request(
        token_endpoint,
        authorization_response=url,
        redirect_url=base_url,
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
        unique_id = userinfo_response.json()["sub"]
        users_email = userinfo_response.json()["email"]
        picture = userinfo_response.json()["picture"]
        users_name = userinfo_response.json()["given_name"]
    else:
        return False

    # Create a user in our db with the information provided
    # by Google
    # user = User(
    #     id_=unique_id, name=users_name, email=users_email, profile_pic=picture
    # )

    # # Doesn't exist? Add to database
    # if not User.get(unique_id):
    #     User.create(unique_id, users_name, users_email, picture)

    # # Begin user session by logging the user in
    # login_user(user)

    # Send user back to homepage
    return unique_id, users_name, users_email, picture

# 專案設定
export FLASK_APP=sttapp/app.py
export SECRET_KEY=
export FLASK_ENV=development
export DB_HOST=127.0.0.1
export DB_PORT=27017
export DB_NAME=
export DB_USERNAME=
export DB_PASSWORD=

# redis server for celery broker and cache
export CELERY_BROKER_URL=
export CELERY_RESULT_BACKEND=

# google service
# 此為goole第三方登入使用，不需要此功能的話這邊不用寫
export GOOGLE_CLIENT_ID=
export GOOGLE_CLIENT_SECRET=

# mail server
export DEV_MAIL_USERNAME=
export DEV_MAIL_PASSWORD=

# google drive api
# 此為至goole drive產生人員名冊用，不需要此功能的話這邊不用寫
export GOOGLE_DRIVE_FOLDER_ID=
export GOOGLE_DRIVE_API_CERD_PATH=

# other setups
export ADMIN_EMAIL=
export MAIL_DEFAULT_SENDER=

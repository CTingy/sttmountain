import os
from sttapp.exts.celery  import celery
from sttapp.base.tasks import send_mail
from .service import GoogleDriveService


@celery.task()
def gen_files_on_gsuite(proposal_id, google_folder_id, user_email):
    
    gd = GoogleDriveService(proposal_id=proposal_id, google_folder_id=google_folder_id)
    try:
        gd.generate_sheets()
        gd.generate_doc()
    except Exception as e:
        send_mail(
            subject='您在山協網站操作的事項已失敗', 
            recipients=[user_email],
            html_body='''<p>網站主機至山協G suite產生檔案發生錯誤，請檢查輸入的資料夾位址是否有效，
                      或是確認輸入的資料夾已開啟編輯權限給山協網站主機<br>您輸入的檔案ID為：{}</p>'''.format(google_folder_id)
        )
        send_mail(
            subject='至G suite產生人員名冊發生問題', 
            recipients=[os.environ.get("ADMIN_EMAIL")],
            html_body="prop_id = {}, folder_id = {}, user_email = {}, err = {} | {}".format(
                proposal_id, google_folder_id, user_email, type(e).__name__, str(e)
            )
        )

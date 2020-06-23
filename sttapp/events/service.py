import os
import pygsheets
import datetime

from sttapp.base.utils import get_local_dt
from sttapp.proposals.models import Proposal


class GoogleDriveService():

    def __init__(proposal_id, service_file_path=None, google_folder_id=None):
        
        service_file = service_file_path or os.environ.get('GOOGLE_DRIVE_API_CERD_PATH')
        self.client = pygsheets.authorize(service_account_file=service_file)
        self.folder_id = google_folder_id or os.environ.get('GOOGLE_DRIVE_FOLDER_ID')
        
        # get information of proposal
        proposal = Proposal.objects.get(id=proposal_id)
        self.proposal = proposal
        self.file_name = "{}_{}".format(
            proposal.title, get_local_dt(datetime.datetime.utcnow()).strftime("%Y%m%d%H%M%s"))

    def generate_sheets(self):
        
        sheet = self.client.create(self.file_name + "_入山", folder=self.folder_id)
        base_worksheet = self.client.open("內本鹿人員資料 的副本")
        wsh = base_worksheet.copy_to(sheet.id)

        wsh.title = "入山人員資料"
        wsh.index = 0

        for i, a in enumerate(self.proposal.attendees, 3): 
            wsh.update_row(i, [
                # 姓名、性別、出生年別、出生日期、國別、身份證字號
                a.name, 1 if a.gender == "男" else 2, 2, a.birthday.strftime("%Y%m%d"), 1, a.security_number,
                # 電話、電子郵件(不紀錄)、地址(不紀錄)、緊急聯絡人姓名、緊急聯絡人電話
                a.cellphone_number, "", "", a.emergency_contact, a.emergency_contact_phone
            ])
        wks.sync()

    def generate_doc(self):

        sheet = self.client.create(self.file_name + "_直企", folder=self.folder_id)
        sheet.add_row()




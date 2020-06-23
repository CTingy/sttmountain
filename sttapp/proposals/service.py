import os
import pygsheets
import datetime

from pygsheets.drive import DriveAPIWrapper

from sttapp.base.utils import get_local_dt
from sttapp.proposals.models import Proposal


class GoogleDriveService():

    def __init__(self, proposal_id, google_folder_id=None, service_file_path=None):
        
        service_file = service_file_path or os.environ.get('GOOGLE_DRIVE_API_CERD_PATH')
        self.client = pygsheets.authorize(service_account_file=service_file)
        self.folder_id = google_folder_id or os.environ.get('GOOGLE_DRIVE_FOLDER_ID')
        
        # get information of proposal
        proposal = Proposal.objects.get(id=proposal_id)
        self.proposal = proposal
        self.file_name = "{}_{}".format(
            proposal.title, get_local_dt(datetime.datetime.utcnow()).strftime("%Y%m%d%H%M%s"))

    def _validate_folder_id(self):
        pass

    def generate_sheets(self):
        
        sheet = self.client.create(self.file_name + "_入山", folder=self.folder_id)
        base_worksheet = self.client.open("系統用_入山人員資料_範本_sttmt_attendees_mountain_policy_template")
        wks = base_worksheet.worksheet().copy_to(sheet.id)

        wks.title = "入山人員資料"
        wks.index = 0
        for i, a in enumerate(self.proposal.attendees, 3): 
            wks.update_row(i, [
                # 姓名、性別、出生年別、出生日期、國別、身份證字號
                a.name, 1 if a.gender == "男" else 2, 2, a.birthday.strftime("%Y%m%d"), 1, a.security_number,
                # 電話、電子郵件(不紀錄)、地址(不紀錄)、緊急聯絡人姓名、緊急聯絡人電話
                a.cellphone_number, "", "", a.emergency_contact, a.emergency_contact_phone
            ])
        wks.sync()

    def generate_doc(self):

        sheet = self.client.create(self.file_name + "_直企人員資料", folder=self.folder_id)
        base_worksheet = self.client.open("系統用_直企人員資料_範本_sttmt_attendees_A4_template")
        wks = base_worksheet.worksheet().copy_to(sheet.id)

        wks.title = "直企人員資料"
        wks.index = 0
        for i, a in enumerate(self.proposal.attendees, 2):
            wks.update_row(i, [
                f"{a.department_and_grade}\n{a.student_id}",
                f"{a.name}\n{a.cellphone_number}",
                f"{a.get_highest_difficulty_display()}\n{a.highest_difficulty_experience or ''}",
                f"{a.security_number}\n{a.birthday_str}",
                f"{a.emergency_contact}\n{a.emergency_contact_phone}",
                f"{a.blood_type or ''}",
                f"{a.drug_allergy}",
                f"{'' if a.is_adult else ''}",
            ])
        wks.sync()


## @file GDriveSender.py
#  @brief Sender to Google Drive
#  @details DON'T WORK
# @author: Romain Durieux and Nathan Trouillet (2022)

from pydrive.drive import GoogleDrive
from pydrive.auth import GoogleAuth
import os

class GDriveSender:
    
    def __init__(self):
        try :
            self.gauth = GoogleAuth()           
            self.drive = GoogleDrive(self.gauth)
        except :
            print("Error when init Google Drive")
        
    def upload(self,path):
        gfile = self.drive.CreateFile({'parents': [{'id': '109lymlUpPLet_sWUXiwpTk3EVUA4aDNY'}]})
        # Read file and set it as the content of this instance.
        gfile.SetContentFile(path)
        gfile.Upload() # Upload the file.
        gfile = None
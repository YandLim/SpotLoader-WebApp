import os
import shutil

class zipped:
    def __init__(self):
        self.DOWNLOAD_FOLDER = "static/downloads"
        if not os.path.exists(self.DOWNLOAD_FOLDER):
            os.makedirs(self.DOWNLOAD_FOLDER)

        self.ZIP_FOLDER = "static/finish_files"        
        if not os.path.exists(self.ZIP_FOLDER):
                os.makedirs(self.ZIP_FOLDER)


    def create_zip(self, album_name, song_folder):
        zip_path = os.path.join(self.ZIP_FOLDER, album_name)

        shutil.make_archive(zip_path, 'zip', song_folder)
        return zip_path + ".zip"

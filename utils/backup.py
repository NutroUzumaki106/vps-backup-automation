from .nas_server import NasServer
from datetime import datetime
import logging
import os


class Backup:
    def __init__(
        self,
        project_name: str,
        base_path: str,
        save_path: str,
        backup_type: str = "_bkp",
    ) -> None:
        self.project_name = project_name
        self.base_path = base_path
        self.save_path = save_path
        self.current_date = datetime.today().strftime("%Y-%m-%d")
        self.backup_type = backup_type
        self.logger = logging.getLogger(os.getenv("LOGGER_APP"))
        self.nas_max_retry = 3
        self.config()

    def config(self) -> None:
        if not self.save_path:
            self.save_path = f"{self.base_path}/backup"
        self.save_path = f"{self.save_path}/{self.backup_type}/{self.project_name}/{self.current_date}"
        if not os.path.exists(self.save_path):
            os.makedirs(self.save_path)

    def start_backup(self, paths) -> None:
        while self.nas_max_retry:
            try:
                nas = NasServer(paths)
                if nas.start_saving():
                    break
            except:
                self.nas_max_retry -= 1

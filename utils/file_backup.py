from dotenv import load_dotenv
from .backup import Backup
import subprocess
import os

load_dotenv()


class FileBackup(Backup):
    def __init__(self, base_path: str) -> None:
        super().__init__(
            os.getenv("PROJECT"), base_path, os.getenv("BACKUP_PATH"), "file_backup"
        )
        self.folder_paths = (
            os.getenv("FOLDER_PATHS").split(",") if os.getenv("FOLDER_PATHS") else []
        )
        self.command = [
            f"scp -r -i {os.getenv('IDENTITY_FILE_PATH')}",
        ]

    def start_backup(self) -> None:
        if not self.folder_paths:
            return

        for paths in self.folder_paths:
            command = self.command.copy()
            command.append(
                f"{os.getenv('SERVER_USERNAME')}@{os.getenv('SERVER_HOST')}:{paths}"
            )
            command.append(self.save_path)
            subprocess.run(" ".join(command), shell=True)
        super().start_backup([{"storage_type": "folder", "path": self.save_path}])

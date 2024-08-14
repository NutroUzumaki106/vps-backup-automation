from dotenv import load_dotenv
from .backup import Backup
from .db import Database
import subprocess
import os


load_dotenv()


class DBBackup(Backup):
    def __init__(self, base_path: str) -> None:
        super().__init__(
            os.getenv("PROJECT"), base_path, os.getenv("BACKUP_PATH"), "db_backup"
        )
        self.db = Database()
        self.command = [
            "mysqldump.exe",
            f"-h{os.getenv('MYSQL_HOST')}",
            f"-u{os.getenv('MYSQL_USERNAME')}",
            f'--password="{os.getenv("MYSQL_PASSWORD")}"',
            "--skip-lock-tables",
            "--ignore-table=octanet.master_city",
            "--ignore-table=octanet.master_pin",
        ]
        self.databases = self.get_databases()

    def start_backup(self) -> None:
        for database in self.databases:
            try:
                os.chdir(os.getenv("MYSQL_DUMP_PATH"))
                command = self.command.copy()
                command.append(f"{database} > {self.save_path}/_bkp_{database}.sql")
                a = " ".join(command)
                subprocess.run(
                    " ".join(command),
                    shell=True,
                )
            except Exception as e:
                self.logger.info(str(e))
                continue
        return super().start_backup([{"storage_type": "folder", "path": self.save_path}])

    def get_databases(self) -> list:
        try:
            databases = self.db.execute_query("show Databases", if_data=True)
            excluded_databases = (
                os.getenv("EXCLUDED_DATABASES").split(",")
                if os.getenv("EXCLUDED_DATABASES")
                else []
            )
            return [
                _["Database"]
                for _ in databases
                if not _["Database"] in excluded_databases
            ]
        except Exception as e:
            self.logger.info(str(e))
            return []

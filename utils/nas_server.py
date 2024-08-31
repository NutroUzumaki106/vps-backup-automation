from smb.SMBConnection import OperationFailure, NotReadyError
from smb.SMBConnection import SMBConnection
from dotenv import load_dotenv
from halo import Halo
import threading
import logging
import time
import os

load_dotenv()

class NasServer:
    def __init__(self, local_paths) -> None:
        self.conn = None
        self.conn_status = False
        self.server_ip = os.getenv("NAS_SERVER")
        self.username = os.getenv("NAS_USERNAME")
        self.password = os.getenv("NAS_PASSWORD")
        self.share_name = os.getenv("NAS_FOLDER_NAME")
        self.remote_save_path = os.getenv("NAS_SAVE_PATH")
        self.logger = logging.getLogger(os.getenv("LOGGER_APP"))
        self.local_paths = local_paths
        self.connect()

    def connect(self) -> None:
        try:
            self.conn = SMBConnection(self.username, self.password, "pynas", "")
            self.conn.connect(self.server_ip, 445)
            self.conn_status = self.test_connection()
        except Exception as e:
            self.logger.error()

    def start_saving(self):
        if not self.conn_status:
            return False
        try:
            self.stop_event = threading.Event()
            for data in self.local_paths:
                try:
                    skip_directories = ["venv", ".venv", "__pycache__"]
                    my_spinner_thread = threading.Thread(
                        target=self.my_spinner, args=(data["path"],)
                    )
                    my_spinner_thread.start()
                    if data["storage_type"] == "file":
                        self.save_file(data["path"], self.remote_save_path)
                    elif data["storage_type"] == "folder":
                        # Set the base remote save path
                        base_remote_save_path = os.path.join(
                            self.remote_save_path, os.path.basename(data["path"])
                        )

                        # Traverse the directory tree
                        for root, dirs, files in os.walk(data["path"]):
                            # Check if any directory in the current path should be skipped
                            if any(
                                dir_name in skip_directories
                                for dir_name in root.split(os.path.sep)
                            ):
                                continue
                            # Construct the remote save path for the current directory
                            if root == data["path"]:
                                remote_save_path = base_remote_save_path
                            else:
                                remote_save_path = os.path.join(
                                    base_remote_save_path,
                                    os.path.relpath(root, data["path"]),
                                )

                            # Create the remote directory if it doesn't exist
                            if not files:
                                self.check_save_path(remote_save_path)

                            # Process files in the current directory
                            for file_name in files:
                                # Save each file to the corresponding remote directory
                                self.save_file(
                                    os.path.join(root, file_name), remote_save_path
                                )
                except OperationFailure as e:
                    self.stop_event.set()
                    my_spinner_thread.join()
                    self.logger.error(str(str(e)))
                    return False
            self.stop_event.set()
            my_spinner_thread.join()
            self.logger.info(f"Data saved on NAS {os.getenv('NAS_SERVER')}")
            return True
        except NotReadyError as e:
            self.stop_event.set()
            my_spinner_thread.join()
            self.logger.error("Auth failed for NAS server:", str(e))
            return False

    def my_spinner(self, file_path):
        spinner = Halo(text="Uploading to NAS server", spinner="dots")
        spinner.start()
        self.stop_event.wait()
        spinner.stop()

    def save_file(self, file_path: str, save_path: str):
        with open(file_path, "rb") as binary_file:
            file_name = os.path.basename(file_path)
            self.check_save_path(save_path)
            self.conn.storeFile(
                self.share_name,
                os.path.join(save_path, file_name),
                binary_file,
            )

    def check_save_path(self, path: str) -> None:
        if not self.check_path(path):
            created_path = ""
            for directory in path.split("/"):
                created_path = os.path.join(created_path, directory)
                if not self.check_path(created_path):
                    self.conn.createDirectory(self.share_name, created_path)

    def check_path(self, path) -> bool:
        try:
            self.conn.listPath(self.share_name, path)
            return True
        except Exception as e:
            # path not found
            return False

    def test_connection(self) -> bool:
        try:
            shares = self.conn.listShares()
            for share in shares:
                if share.name == self.share_name:
                    return True
            return False
        except NotReadyError as e:
            self.logger.error("Auth failed for NAS server:", str(e))
            return False
        except Exception as e:
            self.logger.error("Failed to connect to NAS server:", str(e))
            return False

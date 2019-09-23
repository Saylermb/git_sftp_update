import sys
from pathlib import Path

import paramiko
from git import Repo


class SFTP:
    """
    Do:
    |with SFTP('localhost', 'root', '123456') as sftp:|
    |     ...                                         |
    for return object paramiko.sftp_client.SFTPClient
    """
    def __init__(self, host:str, user:str, password:str, port:int=22):
        self.transport = paramiko.Transport((host, port))
        self.transport.connect(username=user, password=password)

    def __enter__(self):
        with paramiko.SFTPClient.from_transport(self.transport) as sftp:
            return sftp

    def __exit__(self, exc_type, exc_val, exc_tb):
        print('close')
        self.transport.close()

# with SFTP('195.123.195.243', 'root', 'zzUA4SjKt9Jn4aj3', 3110) as sftp:
#     print(dir(sftp))
#     print(type(sftp))


class DiffGenerator:
    repo = Repo(str(Path(__file__).parent.absolute()))

    def __iter__(self):
        for item in self.repo.index.diff(None):
            yield item.a_path


for s in DiffGenerator():
    print(s)
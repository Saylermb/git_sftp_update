import sys
from pathlib import Path
from itertools import chain, cycle

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


class DiffGenerator:
    """
    generate old_file_name :str, new _file_name: str
    and what with him to do.
    variant to do:
       add -
       delete -
       add-delete -
    """
    def __init__(self, repo_path:str):
        self.repo = Repo(repo_path)

    def _iter(self, commit):
        change_type = {"A":"delete", "D":"add", "R":"add-delete", "M":"add", "T":"add"}
        for name, value in change_type.items():
            yield zip(commit.diff('HEAD~1').iter_change_type(name), cycle([value]))

    def __iter__(self):
        head_commit = self.repo.head.commit
        for iterator in self._iter(head_commit):
            for item, do in iterator:
                yield item.b_path, item.a_path, do


if __name__ == '__main__':
    if 5 > len(sys.argv) > 5 or sys.argv in ['-h', '--help', '?']:
        print('    python3 deploy.py {host} {port} {user} {password} {dir_on_server}\n',
              'where:\n',
              '   host = address server, example 123.456.788.90 or localhost\n',
              '   port = port server, example 22\n',
              '   user = user on server, example root or administrator\n',
              '   password = password of user, example Qwerty\n',
              '   dir_on_server = path for dir with edit data, example /var/www/html/site_dir',)
        exit(1)
    repo_path = str(Path(__file__).parent.absolute())


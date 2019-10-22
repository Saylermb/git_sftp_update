import sys
import traceback
from pathlib import Path
from itertools import cycle

import paramiko
from git import Repo


class SFTP:
    """
    Do:
    |with SFTP('localhost', 'root', '123456') as sftp:|
    |     ...                                         |
    for return object paramiko.sftp_client.SFTPClient
    """

    def __init__(self, host: str, user: str, password: str, port: [int, str] = 22):
        self.transport = paramiko.Transport((host, int(port)))
        self.transport.connect(username=user, password=password)

    def __enter__(self) -> paramiko.sftp_client.SFTPClient:
        return paramiko.SFTPClient.from_transport(self.transport)

    def __exit__(self, exc_type, exc_val, exc_tb):
        print('connection is close')
        self.transport.close()

    def __getattr__(self, item):
        raise AttributeError


class DiffGenerator:
    """
    generate old_file_name :str, new _file_name: str
    and what with him to do.
    variant to do:
       add -
       delete -
       add-delete -
    """

    def __init__(self, repo_path: str, commit: str = None):
        self.repo = Repo(repo_path)
        self.last_commit = commit or self.repo.head.commit.name_rev

    def head_commit_name(self):
        return self.repo.head.commit.name_rev

    def _iter(self, commit):
        change_type = {"A": "delete", "D": "add", "M": "add", "T": "add", "R": "move", }
        for dif in commit.diff('HEAD~1'):
            yield dif, change_type.get(dif.change_type)
        # change_type = {"R": "move", }
        # for name, value in change_type.items():
        #     yield zip(commit.diff('HEAD~1').iter_change_type(name), cycle([value]))

    def __iter__(self):
        commits_list =  list(self.repo.iter_commits())
        while commits_list:
            commit = commits_list.pop()
            print(f"{commit.name_rev} == {self.last_commit}")
            if commit.name_rev == self.last_commit:
                break
        print(commits_list)
        for commit in reversed(commits_list):
            if commit.name_rev != self.last_commit:
                break
            for item, do in self._iter(commit):
                yield item.b_path, item.a_path, do


# def recursive_create_dir(sftp, path):
#     try:
#         print(str(path))
#         sftp.mkdir(str(path))
#     except OSError:
#         if str(path) == '.':
#             print('error')
#             exit(0)
#         print(f'Exception! Not found file {str(path)}')
#         recursive_create_dir(sftp, path.parent)

def recursive_create_dir(sftp, path, depth=0):
    if depth >= len(path.parents) - 1:
        return
    print(sftp.listdir(str(path.parents[len(path.parents) - 1 - depth])))
    directory = path.parents[len(path.parents) - 2 - depth]

    if not directory.name in sftp.listdir(str(path.parents[len(path.parents) - 1 - depth])):
        print(f'create dir {str(directory)}')
        sftp.mkdir(str(directory))
        depth += 1
        recursive_create_dir(sftp, path, depth)
    else:
        depth += 1
        recursive_create_dir(sftp, path, depth)


delete = lambda old, new: sftp.remove(old)
move = lambda old, new: sftp.rename(old, new)
add = lambda old, new: sftp.put(old, new)
S = {'delete': delete, 'move': move, 'add': add}

if __name__ == '__main__':
    if len(sys.argv) != 6 or sys.argv in ['-h', '--help', '?']:
        print('    python3 deploy.py {host} {user} {password} {port} {dir_on_server}\n',
              'where:\n',
              '   host = address server, example 123.456.788.90 or localhost\n',
              '   port = port server, example 22\n',
              '   user = user on server, example root or administrator\n',
              '   password = password of user, example Qwerty\n',
              '   dir_on_server = path for dir with edit data, example /var/www/html/site_dir', )
        exit(1)
    print("")
    repo_path = str(Path(__file__).parent.absolute())
    remote_dir = sys.argv[-1]
    with SFTP(*sys.argv[1:-1]) as sftp:
        sftp.chdir(remote_dir)
        try:
            sftp.get('.git.update', '.git.update')
            with open('.git.update') as file_commit:
                last_commit_name = file_commit.read()
        except FileNotFoundError:
            last_commit_name = None
        print(f'last commit {last_commit_name}')
        diff = DiffGenerator(repo_path, last_commit_name)
        for old_path, new_path, what_do in diff:
            print(old_path, new_path, what_do)
            try:
                S.get(what_do)(old_path, new_path)
            except:
                if what_do == 'delete':
                    continue
                print(f'Exception in file change {old_path} > {new_path}')
                recursive_create_dir(sftp, Path(new_path))
                S.get(what_do)(old_path, new_path)
                print(old_path, new_path, what_do)
        with open('.git.update', 'w') as file_commit:
            file_commit.write(diff.head_commit_name())

        sftp.put('.git.update', '.git.update')

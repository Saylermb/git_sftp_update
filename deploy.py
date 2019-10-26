import os
import sys
from itertools import dropwhile
from pathlib import Path
from typing import Union

from git import Repo

from sftp import SFTP


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
        self.last_commit = commit or self._pre_last_commit().name_rev

    def _pre_last_commit(self):
        iter = self.repo.iter_commits()
        next(iter)
        return next(iter)

    def head_commit_name(self):
        return self.repo.head.commit.name_rev

    def _iter(self, commit, last_commit):
        change_type = {"A": "add", "D": "delete", "M": "add", "T": "add", "R": "move", }
        for dif in commit.diff(last_commit):
            yield dif, change_type.get(dif.change_type)
        # change_type = {"R": "move", }
        # for name, value in change_type.items():
        #     yield zip(commit.diff('HEAD~1').iter_change_type(name), cycle([value]))

    def __iter__(self):
        print(f'head commit: {self.head_commit_name()}')
        func = lambda commit: commit.name_rev.split(' ')[0] != self.last_commit.split(' ')[0]
        commits_list = list(dropwhile(func, reversed(list(self.repo.iter_commits()))))
        print(commits_list[0], commits_list[-1])

        for item, do in self._iter(commits_list[0], commits_list[-1]):
            yield item.a_path, item.b_path, do


class SFTPDeploy(SFTP):

    def __init__(self, host: str, user: str, password:str,
                 port: Union[int, str], path: str, repo_path=None):
        super().__init__(host, user, password, port)
        self.repo_path = repo_path if repo_path else str(Path(__file__).parent)
        self.remote_dir = path
        self.structure = self.get_structure(self.repo_path)
        self.sftp = None

    def __call__(self, *args, **kwargs):
        self.sftp = self.connect()
        self.sftp.chdir(self.remote_dir)
        diff = self.get_difference()

        for old_path, new_path, what_do in diff:
            print(what_do, old_path, new_path)
            if what_do == 'add':
                self.sftp.put(str(Path(self.repo_path).joinpath(old_path)), new_path)
            elif what_do == 'delete':
                self.sftp.remove(new_path)
            elif what_do == 'move':
                self.sftp.remove(old_path)
                self.sftp.put(str(Path(self.repo_path).joinpath(old_path)), new_path)
        with open('.git.update', 'w') as file_commit:
            file_commit.write(diff.head_commit_name())

        self.sftp.put('.git.update', '.git.update')

    def get_difference(self):
        try:
            self.sftp.get('.git.update', '.git.update')
            with open('.git.update') as file_commit:
                last_commit_name = file_commit.read()
        except FileNotFoundError:
            last_commit_name = None
        print(f'last commit {last_commit_name}')
        return DiffGenerator(self.repo_path, last_commit_name)

    @staticmethod
    def recursive_create_dir(sftp, path, depth=0):
        if depth >= len(path.parents) - 1:
            return
        print(sftp.listdir(str(path.parents[len(path.parents) - 1 - depth])))
        directory = path.parents[len(path.parents) - 2 - depth]

        if not directory.name in sftp.listdir(str(path.parents[len(path.parents) - 1 - depth])):
            print(f'create dir {str(directory)}')
            sftp.mkdir(str(directory))
            depth += 1
            SFTPDeploy.recursive_create_dir(sftp, path, depth)
        else:
            depth += 1
            SFTPDeploy.recursive_create_dir(sftp, path, depth)

    @staticmethod
    def get_structure(path):
        return [path_[0] for path_ in os.walk(path)]


if __name__ == '__main__':

    if len(sys.argv) != 7 or sys.argv in ['-h', '--help', '?']:
        print('    python3 deploy.py {host} {user} {password} {port} {dir_on_server} {repo_dir}\n',
              'where:\n',
              '   host = address server, example 123.456.788.90 or localhost\n',
              '   port = port server, example 22\n',
              '   user = user on server, example root or administrator\n',
              '   password = password of user, example Qwerty\n',
              '   dir_on_server = path for dir with edit data, example /var/www/html/site_dir\n',
              '   repo_dir dir for repository')
        exit(1)
    print("")
    SFTPDeploy(*sys.argv[1:])()

import os
from itertools import dropwhile, chain
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


class SFTPGitDeploy(SFTP):

    def __init__(self, host: str, user: str, password: str,
                 port: Union[int, str], path: str, repo_path=None, after_use = None):
        super().__init__(host, user, password, port)
        self.repo_path = repo_path if repo_path else str(Path(__file__).parent)
        self.remote_dir = path
        self.sftp = None
        self.after_use = after_use

    def __call__(self, *args, **kwargs):
        self.sftp = self.connect()
        self.sftp.chdir(self.remote_dir)
        diff = self.get_difference()

        for old_path, new_path, what_do in diff:
            print(what_do, old_path, new_path)
            if what_do == 'add':
                self._add(new_path)
            elif what_do == 'delete':
                self.sftp.remove(new_path)
            elif what_do == 'move':
                self.sftp.remove(old_path)
                self._add(new_path)
        self.write_change_file(diff)
        self.sftp.close()
        if self.after_use:
            self.command_execute()

    def command_execute(self):
        print(f'execute command {self.after_use}')
        ssh = self.ssh_connect()
        ssh.exec_command(f'')
        stdin, stdout, stderr = ssh.exec_command(f'cd {self.remote_dir} && {self.after_use}')
        for line in stdout.readlines():
            print(line.replace('\n', ''))

    def write_change_file(self, diff):
        with open('.git.update', 'w') as file_commit:
            file_commit.write(diff.head_commit_name())

        self.sftp.put('.git.update', '.git.update')

    def _add(self, path: str):
        try:
            self.sftp.put(str(Path(self.repo_path).joinpath(path)), path)
        except:
            self.recursive_create_dir(self.sftp, Path(path))
            self.sftp.put(str(Path(self.repo_path).joinpath(path)), path)

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
    def recursive_create_dir(sftp, path: Path, depth=0):
        if depth >= len(path.parents) - 1:
            return
        print(sftp.listdir(str(path.parents[len(path.parents) - 1 - depth])))
        directory = path.parents[len(path.parents) - 2 - depth]

        if not directory.name in sftp.listdir(str(path.parents[len(path.parents) - 1 - depth])):
            print(f'create dir {str(directory)}')
            sftp.mkdir(str(directory))
        depth += 1
        SFTPGitDeploy.recursive_create_dir(sftp, path, depth)


class SFTPFullDeploy(SFTPGitDeploy):

    def get_difference(self):
        file_list = [[str(Path(path_[0]).joinpath(s)) for s in path_[2]]
                     for path_ in os.walk(self.repo_path) if path_[0]]

        return list(map(lambda x:(
            x[len(self.repo_path) + 1:],
            x[len(self.repo_path) + 1:],
            'add'),
                        chain(*file_list)))

    def write_change_file(self, *args):
        pass


if __name__ == '__main__':
    host = os.environ.get('HOST')
    user = os.environ.get('USER', 'root')
    password = os.environ.get('PASSWORD')
    port = os.environ.get('PORT', '22')
    dir_on_server = os.environ.get('DIR_ON_SERVER')
    repo_dir = '/github/workspace'
    mode = os.environ.get('MODE', 'GIT')
    build_folder = os.environ.get('BUILD_FOLDER', 'GIT')
    if build_folder and mode == 'FULL':
        raise ValueError('Mode GIT can\'t be use with BUILD_FOLDER')
    if build_folder:
        repo_dir = str(Path(repo_dir).joinpath(build_folder))
        repo_dir = repo_dir if repo_dir[-1] !='/' else repo_dir[:-1]
    after_use = os.environ.get('USE_COMMAND_AFTER_UPDATE')
    print(host, user, password, port, dir_on_server, repo_dir)
    if mode == 'GIT':
        SFTPGitDeploy(host, user, password, port, dir_on_server, repo_dir, after_use)()
    elif mode == 'FULL':
        SFTPFullDeploy(host, user, password, port, dir_on_server, repo_dir, after_use)()
    else:
        raise ValueError('Unknown mod name')

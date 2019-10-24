import os
import sys
from pathlib import Path

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
            if commit.name_rev.split(' ')[0] == self.last_commit.split(' ')[0]:
                commits_list = [commit]
                break
        print(commits_list)
        for commit in reversed(commits_list):
            for item, do in self._iter(commit):
                yield item.b_path, item.a_path, do

class Deploy:
    delete = lambda old, new: sftp.remove(old)
    move = lambda old, new: sftp.rename(old, new)
    add = lambda old, new: sftp.put(old, new)
    S = {'delete': delete, 'move': move, 'add': add}

    def __init__(self, host, username, password, port, path, repo_path=None):
        self.repo_path = repo_path if repo_path else str(Path(__file__).parent)
        self.remote_dir = path
        self._client = SFTP(host, username, password, port)
        self.structure = self.get_structure()
        self.sftp = None


    def __call__(self, *args, **kwargs):
        self.sftp = self._client.connect()
        sftp.chdir(self.remote_dir)

        for old_path, new_path, what_do in diff:
            print(old_path, new_path, what_do)
            try:
                self.S.get(what_do)(old_path, new_path)
            except:
                if what_do == 'delete':
                    continue
                print(f'Exception in file change {old_path} > {new_path}')
                self.recursive_create_dir(sftp, Path(new_path))
                self.S.get(what_do)(old_path, new_path)
                print(old_path, new_path, what_do)
        with open('.git.update', 'w') as file_commit:
            file_commit.write(diff.head_commit_name())

        sftp.put('.git.update', '.git.update')
        

    def get_difference(self):
        try:
            self.sftp.get('.git.update', '.git.update')
            with open('.git.update') as file_commit:
                last_commit_name = file_commit.read()
        except FileNotFoundError:
            last_commit_name = None
        print(f'last commit {last_commit_name}')
        return DiffGenerator(repo_path, last_commit_name)

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
                Deploy.recursive_create_dir(sftp, path, depth)
            else:
                depth += 1
                Deploy.recursive_create_dir(sftp, path, depth)

    @staticmethod
    def get_structure(path):
        return [path_[0] for path_ in os.walk(path)]




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

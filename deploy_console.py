import sys

from deploy import SFTPGitDeploy, SFTPFullDeploy

if __name__ == '__main__':

    if len(sys.argv) != 8 or sys.argv in ['-h', '--help', '?']:
        print('    python3 deploy.py {mode} {host} {user} {password} {port} {dir_on_server} {repo_dir}\n',
              'where:\n',
              '   mode = using update mode:',
              '          GIT = The list of changes is obtained from git',
              '          FULL  = Update all files without delete'
              '   host = address server, example 123.456.788.90 or localhost\n',
              '   port = port server, example 22\n',
              '   user = user on server, example root or administrator\n',
              '   password = password of user, example Qwerty\n',
              '   dir_on_server = path for dir with edit data, example /var/www/html/site_dir\n',
              '   repo_dir dir for repository')
        exit(1)
    mode = sys.argv[2]
    if mode == 'GIT':
        SFTPGitDeploy(*sys.argv[2:])()
    elif mode == 'FULL':
        SFTPFullDeploy(*sys.argv[2:])()
    else:
        raise ValueError('Unknown mod name')
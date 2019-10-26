import sys

from deploy import SFTPDeploy

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
    SFTPDeploy(*sys.argv[1:])()
#### Scrypt for update remote storage with sftp connect in github Action


##### How this work:
- Script update only change files (add, move, delete)

```text
RUN:
 python3 deploy.py {host} {user} {password} {port} {dir_on_server} {repo_dir}
 where:
    host = address server, example 123.456.788.90 or localhost
    port = port server, example 22
    user = user on server, example root or administrator
    password = password of user, example Qwerty
    dir_on_server = path for dir with edit data, example /var/www/html/site_dir
    repo_dir dir for repository
```
- After first usage, in remove directory will appear .git.update file with number commit. 
If there is no file, the script updates according to the penultimate commit.

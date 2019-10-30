#### Scrypt for update remote repository with sftp-connections in github-action


##### How this work:
- Script update only change files (add, move, delete)

- Add to your github-actions file next stage:
```yaml
      uses: Saylermb/github-sftp-deploy-action@master
      if: github.event.prerelease == false
      env:
        HOST: ${{ secrets.HOST }}
        USER: ${{ secrets.USER }}
        PASSWORD: ${{ secrets.PASSWORD }}
        PORT: ${{ secrets.PORT }}
        DIR_ON_SERVER: ${{ secrets.PATH }}
        MODE: GIT
```
    where
     - secrets.HOST: ip address server
     - secrets.USER: user name
     - secrets.PASSWORD: password
     - secrets.PORT: sftp port
     - secrets.PATH: path to direcotory for update
    
- After first usage, in remove directory will appear .git.update file with number commit. 
If there is no file, the script updates according to the penultimate commit.


##### Example

```yaml
name: Python package

on: [push]

jobs:
  build:

    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: [3.7]

    steps:
    - uses: actions/checkout@v1
    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v1
      with:
        python-version: ${{ matrix.python-version }}
    - name: Install dependencies
      run: |
        python -m pip install .
    - name: Build and Deploy 

      uses: Saylermb/github-sftp-deploy-action@master
      if: github.event.prerelease == false
      env:
        HOST: ${{ secrets.HOST }}
        USER: ${{ secrets.USER }}
        PASSWORD: ${{ secrets.PASSWORD }}
        PORT: ${{ secrets.PORT }}
        DIR_ON_SERVER: /var/www/html/
        MODE: GIT
```
##### Update without git

Add {MODE: FULL} and all files will be moved from the github-actions folder to the remote directory. This 

```yaml
      uses: Saylermb/github-sftp-deploy-action@master
      if: github.event.prerelease == false
      env:
        HOST: ${{ secrets.HOST }}
        USER: ${{ secrets.USER }}
        PASSWORD: ${{ secrets.PASSWORD }}
        PORT: ${{ secrets.PORT }}
        DIR_ON_SERVER: ${{ secrets.PATH }}
        MODE: FULL
```

It may come in handy if you make build of project.

You can specify the build folder through ENV {BUILD_FOLDER}

```yaml
      uses: Saylermb/github-sftp-deploy-action@master
      if: github.event.prerelease == false
      env:
        HOST: ${{ secrets.HOST }}
        USER: ${{ secrets.USER }}
        PASSWORD: ${{ secrets.PASSWORD }}
        PORT: ${{ secrets.PORT }}
        DIR_ON_SERVER: ${{ secrets.PATH }}
        MODE: FULL
        BUILD_FOLDER: build
```

##### Use command after update

If you need to use the command on remote server, add to ENV {USE_COMMAND_AFTER_UPDATE}. Before change files, the command will be executed.

```yaml
      uses: Saylermb/github-sftp-deploy-action@master
      if: github.event.prerelease == false
      env:
        HOST: ${{ secrets.HOST }}
        USER: ${{ secrets.USER }}
        PASSWORD: ${{ secrets.PASSWORD }}
        PORT: ${{ secrets.PORT }}
        DIR_ON_SERVER: ${{ secrets.PATH }}
        MODE: GIT
        USE_COMMAND_BEFOR_UPDATE: cp setting.py setting_old.py
```

##### Use command after update

If you need to use the command on remote server, add to ENV {USE_COMMAND_AFTER_UPDATE}. After change files, the command will be executed.

```yaml
      uses: Saylermb/github-sftp-deploy-action@master
      if: github.event.prerelease == false
      env:
        HOST: ${{ secrets.HOST }}
        USER: ${{ secrets.USER }}
        PASSWORD: ${{ secrets.PASSWORD }}
        PORT: ${{ secrets.PORT }}
        DIR_ON_SERVER: ${{ secrets.PATH }}
        MODE: GIT
        USE_COMMAND_AFTER_UPDATE: ls -la
```


##### Exit without update file

in this config, command will be used but without change files

```yaml
      uses: Saylermb/github-sftp-deploy-action@master
      if: github.event.prerelease == false
      env:
        HOST: ${{ secrets.HOST }}
        USER: ${{ secrets.USER }}
        PASSWORD: ${{ secrets.PASSWORD }}
        PORT: ${{ secrets.PORT }}
        DIR_ON_SERVER: ${{ secrets.PATH }}
        USE_COMMAND_BEFOR_UPDATE: cp setting.py setting_old.py
        USE_COMMAND_AFTER_UPDATE: python3 test.py
```

#### Scrypt for update remote storage with sftp connect in github Action


##### How this work:
- Script update only change files (add, move, delete)

- Add to your github-actions file next stage:
```yaml
      uses: Saylermb/git_sftp_update@master
      if: github.event.prerelease == false
      env:
        HOST: ${{ secrets.HOST }}
        USER: ${{ secrets.USER }}
        PASSWORD: ${{ secrets.PASSWORD }}
        PORT: ${{ secrets.PORT }}
        DIR_ON_SERVER: ${{ secrets.PATH }}
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

      uses: Saylermb/git_sftp_update@master
      if: github.event.prerelease == false
      env:
        HOST: ${{ secrets.HOST }}
        USER: ${{ secrets.USER }}
        PASSWORD: ${{ secrets.PASSWORD }}
        PORT: ${{ secrets.PORT }}
        DIR_ON_SERVER: /var/www/html/
```
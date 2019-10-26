FROM Python:3.7.4

ADD deploy.py /deploy.py
ADD sftp.py /sftp.py
ADD requirements.txt /requirements.txt

RUN pip install -r requirements.txt
ENTRYPOINT python3 deploy.py 
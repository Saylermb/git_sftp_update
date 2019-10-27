import paramiko


class SFTP:
    """
    Do:
    |with SFTP('localhost', 'root', '123456') as sftp:|
    |     ...                                         |
    for return object paramiko.sftp_client.SFTPClient
    """
    def connect(self):
        return paramiko.SFTPClient.from_transport(self.transport)

    def ssh_connect(self):
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(hostname=self._host, password=self._password,
                           username=self._user, port=self._port)
        return ssh

    def __init__(self, host: str, user: str, password: str, port: [int, str] = 22):
        self._host = host
        self._user = user
        self._password = password
        self._port = port
        self.transport = paramiko.Transport((host, int(port)))
        self.transport.connect(username=user, password=password)

    def __enter__(self) -> paramiko.sftp_client.SFTPClient:
        return paramiko.SFTPClient.from_transport(self.transport)

    def __exit__(self, exc_type, exc_val, exc_tb):
        print('connection is close')
        self.transport.close()

    def __getattr__(self, item):
        raise AttributeError
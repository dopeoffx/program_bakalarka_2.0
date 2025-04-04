import paramiko
import os
from dotenv import load_dotenv

class SFTPConnectionWrapper:
    def __init__(self, key_path=None):
        load_dotenv("config.env")
        self.hostname = os.getenv("HOST")
        self.username = os.getenv("USERNAME")
        self.password =  os.getenv("PASSWORD") 
        self.port = int(os.getenv("PORT", "22"))
        self.transport = paramiko.Transport((self.hostname, self.port))
        self.key_path = key_path
        self.sftp = None
        self.connect()

    def connect(self):
        print("Navazuji SFTP spojení...")
        try:
            if self.key_path:
                private_key = paramiko.RSAKey.from_private_key_file(self.key_path)
                self.transport.connect(username=self.username, pkey=private_key)
            else:
                self.transport.connect(username=self.username, password=self.password)
            self.sftp = paramiko.SFTPClient.from_transport(self.transport)


        except Exception as e:
            print(f"Nepodařilo se připojit k SFTP: {e}")
            self.sftp = None

    def reconnect_if_needed(self):
        try:
            self.sftp.listdir('.')
        except Exception as e:
            print(f"Spojení padlo ({type(e).__name__}: {e}), obnovuji...")
            self.close()
            self.connect()
            
    def reconnect(self):
        load_dotenv("config.env", override=True)
        self.host = os.getenv("HOST")
        self.port = int(os.getenv("PORT", "22"))
        self.username = os.getenv("USERNAME")
        self.password = os.getenv("PASSWORD")
        self.close()       
        self.transport = paramiko.Transport((self.hostname,  self.port))
        self.connect()

    def get_sftp(self):
        self.reconnect_if_needed()
        return self.sftp

    def close(self):
        if self.sftp:
            self.sftp.close()
        if self.transport:
            self.transport.close()

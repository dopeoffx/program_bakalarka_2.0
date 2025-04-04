import io
import logging
import os
import typing
from paramiko import SFTPClient, SFTPFile, Transport, SFTPError, Message
from paramiko.sftp import CMD_STATUS, CMD_READ, CMD_DATA

import logging

logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

class _SFTPFileDownloader:
    """
    Třída pro stahování velkého souboru přes SFTP s omezením počtu současných požadavků.
    """
    _DOWNLOAD_MAX_REQUESTS = 48
    _DOWNLOAD_MAX_CHUNK_SIZE = 0x8000  # 32 768 bajtů

    def __init__(self, f_in: SFTPFile, f_out: typing.BinaryIO, callback=None):
        self.f_in = f_in
        self.f_out = f_out
        self.callback = callback

        self.requested_chunks = {}
        self.received_chunks = {}
        self.saved_exception = None

    def download(self):
        file_size = self.f_in.stat().st_size
        requested_size = 0
        received_size = 0

        while True:
            # Odesíláme čtecí požadavky, dokud není fronta plná nebo nedosáhneme konce souboru.
            while len(self.requested_chunks) + len(self.received_chunks) < self._DOWNLOAD_MAX_REQUESTS and requested_size < file_size:
                chunk_size = min(self._DOWNLOAD_MAX_CHUNK_SIZE, file_size - requested_size)
                request_id = self._sftp_async_read_request(
                    fileobj=self,
                    file_handle=self.f_in.handle,
                    offset=requested_size,
                    size=chunk_size
                )
                self.requested_chunks[request_id] = (requested_size, chunk_size)
                requested_size += chunk_size

            # Zpracujeme odpovědi (volání _async_response probíhá asynchronně)
            self.f_in.sftp._read_response()
            self._check_exception()

            # Zapíšeme přijaté bloky do výstupního proudu
            while True:
                chunk = self.received_chunks.pop(received_size, None)
                if chunk is None:
                    break
                _, chunk_size, chunk_data = chunk
                self.f_out.write(chunk_data)
                if self.callback is not None:
                    self.callback(chunk_data)
                received_size += chunk_size

            # Pokud jsme přečetli celý soubor, ukončíme cyklus
            if received_size >= file_size:
                break

            # Bezpečnostní kontrola front požadavků a přijatých dat
            if not self.requested_chunks and len(self.received_chunks) >= self._DOWNLOAD_MAX_REQUESTS:
                raise ValueError("SFTP communication error. The queue with requested file chunks is empty and"
                                 "the received chunks queue is full and cannot be consumed.")

        return received_size

    def _sftp_async_read_request(self, fileobj, file_handle, offset, size):
        sftp_client = self.f_in.sftp
        with sftp_client._lock:
            num = sftp_client.request_number
            msg = Message()
            msg.add_int(num)
            msg.add_string(file_handle)
            msg.add_int64(offset)
            msg.add_int(size)
            sftp_client._expecting[num] = fileobj
            sftp_client.request_number += 1

        sftp_client._send_packet(CMD_READ, msg)
        return num

    def _async_response(self, t, msg, num):
        if t == CMD_STATUS:
            # Při chybě si uložíme výjimku, kterou později vyhodíme
            try:
                self.f_in.sftp._convert_status(msg)
            except Exception as e:
                self.saved_exception = e
            return
        if t != CMD_DATA:
            raise SFTPError("Expected data")
        data = msg.get_string()

        chunk_info = self.requested_chunks.pop(num, None)
        if chunk_info is None:
            return

        offset, size = chunk_info
        if size != len(data):
            raise SFTPError(f"Invalid data block size. Expected {size} bytes, but got {len(data)}")
        self.received_chunks[offset] = (offset, size, data)

    def _check_exception(self):
        if self.saved_exception is not None:
            ex = self.saved_exception
            self.saved_exception = None
            raise ex


def download_file_content(sftp_client: SFTPClient, remote_path: str) -> str:
    """
    Stáhne vzdálený soubor pomocí _SFTPFileDownloader a vrátí jeho obsah jako text.
    Logování průběhu stahování je zajištěno callback funkcí.
    """
    with sftp_client.open(remote_path, 'rb') as f_in:
        f_out = io.BytesIO()
        total_downloaded = 0
        step_size = 4 * 1024 * 1024 

        def progress_callback(data):
            nonlocal total_downloaded
            total_downloaded += len(data)
            # Jednoduché logování – pokud jsme překročili další násobek step_size, vypíšeme info.
            if total_downloaded % step_size < len(data):
                logger.info(f"{total_downloaded // (1024 ** 2)} MB bylo staženo")

        downloader = _SFTPFileDownloader(f_in, f_out, callback=progress_callback)
        downloader.download()
        content = f_out.getvalue().decode('utf-8')
    return content



from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from node_manage import get_nodes
import time
import socket
import os
import logging
import json

KANISHKA_FOLDER = './Kanishka'
BUFFER_SIZE = 4096
SERVER_PORT = 9999

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class FolderEventHandler(FileSystemEventHandler):
    def __init__(self):
        self.nodes = get_nodes()

    def on_any_event(self, event):
        if event.is_directory and event.event_type != 'deleted':
            return
        self.sync_event(event)

    def sync_event(self, event):
        relative_path = os.path.relpath(event.src_path, KANISHKA_FOLDER)
        for node in self.nodes:
            self.notify_and_transfer(node, relative_path, event.event_type)

    def notify_and_transfer(self, node, path, event_type):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.connect((node, SERVER_PORT))
                event_data = {
                    'event_type': event_type,
                    'path': path,
                    'source_node': socket.gethostbyname(socket.gethostname())
                }
                s.sendall(json.dumps(event_data).encode())

                if event_type in ['created', 'modified']:
                    response = s.recv(BUFFER_SIZE)
                    if response == b'READY':
                        self.send_file(s, path)
                elif event_type == 'deleted':
                    logging.info(f"Notified {node} about deletion of {path}")
                
            except Exception as e:
                logging.error(f"Error notifying {node}: {e}")

    def send_file(self, sock, path):
        full_path = os.path.join(KANISHKA_FOLDER, path)
        with open(full_path, 'rb') as file:
            while True:
                data = file.read(BUFFER_SIZE)
                if not data:
                    break
                sock.sendall(data)
        logging.info(f"File {path} sent successfully")

def start_listener():
    event_handler = FolderEventHandler()
    observer = Observer()
    observer.schedule(event_handler, KANISHKA_FOLDER, recursive=True)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

if __name__ == "__main__":
    start_listener()

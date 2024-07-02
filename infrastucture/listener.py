#### File Operation Listener

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from node_manage import read_nodes
import time
import socket

KANISHKA_FOLDER = 'Kanishka'

class FolderEventHandler(FileSystemEventHandler):
    def __init__(self, nodes):
        self.nodes = nodes

    def on_modified(self, event):
        self.sync_event(event)

    def on_created(self, event):
        self.sync_event(event)

    def on_deleted(self, event):
        self.sync_event(event)

    def sync_event(self, event):
        for node in self.nodes:
            self.notify_node(node, event.src_path, event.event_type)

    def notify_node(self, node, path, event_type):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((node, 9999))
            s.sendall(f'{event_type}:{path}'.encode())

nodes = read_nodes()
event_handler = FolderEventHandler(nodes)
observer = Observer()
observer.schedule(event_handler, KANISHKA_FOLDER, recursive=True)
observer.start()

try:
    while True:
        time.sleep(20)
except KeyboardInterrupt:
    observer.stop()
observer.join()
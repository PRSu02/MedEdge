import os
import shutil
import socket
import logging
import json
from threading import Thread

KANISHKA_FOLDER = './Kanishka'
BUFFER_SIZE = 4096
SERVER_PORT = 9999

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def receive_file(conn, file_path):
    full_path = os.path.join(KANISHKA_FOLDER, file_path)
    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    
    with open(full_path, 'wb') as file:
        while True:
            data = conn.recv(BUFFER_SIZE)
            if not data:
                break
            file.write(data)

def send_file(conn, file_path):
    full_path = os.path.join(KANISHKA_FOLDER, file_path)
    with open(full_path, 'rb') as file:
        while True:
            data = file.read(BUFFER_SIZE)
            if not data:
                break
            conn.sendall(data)

def handle_sync(conn, addr):
    try:
        data = conn.recv(BUFFER_SIZE).decode()
        event_data = json.loads(data)
        event_type = event_data['event_type']
        relative_path = event_data['path']
        source_node = event_data['source_node']

        full_path = os.path.join(KANISHKA_FOLDER, relative_path)
        logging.info(f"Handling {event_type} event for {full_path} from {source_node}")

        if event_type in ['created', 'modified']:
            conn.sendall(b'READY')
            receive_file(conn, relative_path)
            logging.info(f"File {relative_path} received from {source_node}")
        elif event_type == 'deleted':
            if os.path.isdir(full_path):
                shutil.rmtree(full_path, ignore_errors=True)
            elif os.path.isfile(full_path):
                os.remove(full_path)
            logging.info(f"Deleted {full_path}")
        elif event_type == 'request':
            if os.path.exists(full_path):
                conn.sendall(b'SENDING')
                send_file(conn, relative_path)
                logging.info(f"File {relative_path} sent to {source_node}")
            else:
                conn.sendall(b'NOT_FOUND')
                logging.warning(f"File {relative_path} not found, requested by {source_node}")
    except Exception as e:
        logging.error(f"Error handling sync event: {e}")
    finally:
        conn.close()

def start_sync_server():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('', SERVER_PORT))
        s.listen()
        logging.info(f"Sync server started on port {SERVER_PORT}, waiting for connections...")
        while True:
            conn, addr = s.accept()
            Thread(target=handle_sync, args=(conn, addr)).start()

if __name__ == "__main__":
    start_sync_server()

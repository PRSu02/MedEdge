###File Synchronizer
import os
import shutil
import socket
import logging

KANISHKA_BASE_PATH = './Kanishka'

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def handle_sync(event_type, path):
    full_path = os.path.join(KANISHKA_BASE_PATH, path)
    logging.info(f"Handling {event_type} event for {full_path}")
    try:
        if event_type == 'created':
            if os.path.isdir(full_path):
                shutil.copytree(full_path, os.path.join(KANISHKA_BASE_PATH, os.path.basename(path)))
            else:
                shutil.copy2(full_path, KANISHKA_BASE_PATH)
        elif event_type == 'deleted':
            target_path = os.path.join(KANISHKA_BASE_PATH, os.path.basename(path))
            if os.path.isdir(target_path):
                shutil.rmtree(target_path)
            else:
                os.remove(target_path)
        elif event_type == 'modified':
            shutil.copy2(full_path, KANISHKA_BASE_PATH)
    except Exception as e:
        logging.error(f"Error handling {event_type} event for {full_path}: {e}")

def start_sync_server():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('', 9999))
        s.listen()
        logging.info("Sync server started, waiting for connections...")
        while True:
            conn, addr = s.accept()
            with conn:
                data = conn.recv(1024).decode()
                logging.info(f"Raw data received: {data}")
                if data:
                    try:
                        event_type, path = data.split(':', 1)  # Limit split to the first colon
                        logging.info(f"Received {event_type} event for {path} from {addr}")
                        handle_sync(event_type, path)
                    except ValueError:
                        logging.error(f"Error splitting data: {data}")

start_sync_server()
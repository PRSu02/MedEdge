import os
import shutil
import socket
import logging

KANISHKA_BASE_PATH = './Kanishka'

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def handle_sync(event_type, relative_path):
    full_path = os.path.join(KANISHKA_BASE_PATH, relative_path)
    logging.info(f"Handling {event_type} event for {full_path}")
    try:
        if event_type == 'created':
            if os.path.isdir(full_path):
                os.makedirs(full_path, exist_ok=True)
            else:
                # Create directories if they don't exist
                os.makedirs(os.path.dirname(full_path), exist_ok=True)
                open(full_path, 'a').close()  # Create an empty file
        elif event_type == 'deleted':
            if os.path.isdir(full_path):
                shutil.rmtree(full_path)
            else:
                if os.path.exists(full_path):
                    os.remove(full_path)
        elif event_type == 'modified':
            if not os.path.exists(full_path):
                # Handle the case where the file doesn't exist locally
                open(full_path, 'a').close()  # Create an empty file
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
                        event_type, relative_path = data.split(':', 1)
                        logging.info(f"Received {event_type} event for {relative_path} from {addr}")
                        handle_sync(event_type, relative_path)
                    except ValueError:
                        logging.error(f"Error parsing data: {data}")

start_sync_server()

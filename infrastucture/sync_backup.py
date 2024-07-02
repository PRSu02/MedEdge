# file_synchronizer.py

import os
import shutil
import socket
import logging
import requests  # This might be used to fetch files from other nodes

KANISHKA_FOLDER = 'Kanishka'

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def fetch_file_from_node(node, relative_path):
    # Placeholder for actual file fetch logic
    # Example using a simple HTTP request
    url = f'http://{node}:9999/download/{relative_path}'
    response = requests.get(url, stream=True)
    if response.status_code == 200:
        with open(os.path.join(KANISHKA_FOLDER, relative_path), 'wb') as file:
            shutil.copyfileobj(response.raw, file)

def handle_sync(event_type, relative_path):
    full_path = os.path.join(KANISHKA_FOLDER, relative_path)
    logging.info(f"Handling {event_type} event for {full_path}")
    try:
        if event_type == 'created':
            # Ensure parent directory exists
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            # Fetch the file from the originating node (Placeholder)
            fetch_file_from_node('source_node_ip', relative_path)  # Replace 'source_node_ip' with actual IP handling

        elif event_type == 'deleted':
            target_path = os.path.join(KANISHKA_FOLDER, relative_path)
            if os.path.isdir(target_path):
                shutil.rmtree(target_path)
            else:
                os.remove(target_path)
                
        elif event_type == 'modified':
            # Handle modification logic (may need to fetch file again or merge changes)
            fetch_file_from_node('source_node_ip', relative_path)  # Placeholder

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
                        logging.error(f"Error splitting data: {data}")

if __name__ == "__main__":
    start_sync_server()

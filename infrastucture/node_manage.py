import os
import logging

NODES_FILE = './nodes.txt'

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def read_nodes():
    if not os.path.exists(NODES_FILE):
        return []
    with open(NODES_FILE, 'r') as file:
        return [line.strip() for line in file if line.strip()]

def add_node(ip):
    nodes = read_nodes()
    if ip not in nodes:
        with open(NODES_FILE, 'a') as file:
            file.write(ip + '\n')
        logging.info(f"Added node: {ip}")
        return True
    logging.info(f"Node already exists: {ip}")
    return False

def remove_node(ip):
    nodes = read_nodes()
    if ip in nodes:
        nodes.remove(ip)
        with open(NODES_FILE, 'w') as file:
            file.write('\n'.join(nodes) + '\n')
        logging.info(f"Removed node: {ip}")
        return True
    logging.info(f"Node not found: {ip}")
    return False

def get_nodes():
    return read_nodes()

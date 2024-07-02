## Node Management

import os

NODES_FILE = 'nodes.txt'

def read_nodes():
    with open(NODES_FILE, 'r') as file:
        nodes = [line.strip() for line in file.readlines()]
    return nodes

def add_node(ip):
    with open(NODES_FILE, 'a') as file:
        file.write(ip + '\n')

def remove_node(ip):
    nodes = read_nodes()
    nodes = [node for node in nodes if node != ip]
    with open(NODES_FILE, 'w') as file:
        file.writelines('\n'.join(nodes) + '\n')

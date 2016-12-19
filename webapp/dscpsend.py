import socket
import sys
from random import randint

dscp_mapping = [
    {"name":"EF",   "value":0x2e, "index":0},
    {"name":"BE",   "value":0x00, "index":1},
    {"name":"AF11", "value":0x0a, "index":2},
    {"name":"AF12", "value":0x0c, "index":3},
    {"name":"AF13", "value":0x0e, "index":4},
    {"name":"AF21", "value":0x12, "index":5},
    {"name":"AF22", "value":0x14, "index":6},
    {"name":"AF23", "value":0x16, "index":7},
    {"name":"AF31", "value":0x1a, "index":8},
    {"name":"AF32", "value":0x1c, "index":9},
    {"name":"AF33", "value":0x1e, "index":10},
    {"name":"AF41", "value":0x22, "index":11},
    {"name":"AF42", "value":0x24, "index":12},
    {"name":"AF43", "value":0x26, "index":13},
    {"name":"Other","value":0x10, "index":14},
]

if __name__ == "__main__":
    count = 0
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    addr = ("10.10.0.2", 6969)

    while True:

        for mark in dscp_mapping:
            sock.setsockopt(socket.SOL_IP, socket.IP_TOS, mark['value'] << 2)

            pkts = randint(0, 128)

            for x in range(pkts):
                sock.sendto(bytes([x for x in range(0, 255)]), addr)
            if count > 100:
                count = 0
                sys.stdout.write('.')
                sys.stdout.flush()
            else:
                count = count + 1

import asyncio.subprocess
import sys
from collections import deque
from itertools import repeat

mode = 'rate'
interfaces = { 'interfaces':[], 'dscp':[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,]}

"""from wikipdia
DSCP value  Hex value   Decimal value   Meaning
101 110     0x2e        46              Expedited forwarding (EF)
000 000     0x00        0               Best effort
001 010     0x0a        10              AF11
001 100     0x0c        12              AF12
001 110     0x0e        14              AF13
010 010     0x12        18              AF21
010 100     0x14        20              AF22
010 110     0x16        22              AF23
011 010     0x1a        26              AF31
011 100     0x1c        28              AF32
011 110     0x1e        30              AF33
100 010     0x22        34              AF41
100 100     0x24        36              AF42
100 110     0x26        38              AF43
"""

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
    {"name":"Other","value":0xFF, "index":14},
]

def parse_ifstats(line):
    #csv output format: 
    #Type rate:
    #unix timestamp;iface_name;bytes_out/s;bytes_in/s;bytes_total/s;bytes_in;bytes_out;packets_out/s;packets_in/s;packets_total/s;packets_in;packets_out;errors_out/s;errors_in/s;errors_in;errors_out\n
    #Type svg, sum, max:
    #unix timestamp;iface_name;bytes_out;bytes_in;bytes_total;packets_out;packets_in;packets_total;errors_out;errors_in\n

    data = line.split(';')

    reading = {}

    if mode == 'rate':
        reading['timestamp']           = data[0]
        reading['iface_name']          = data[1]
        reading['bytes_out_s']         = data[2]
        reading['bytes_in_s']          = data[3]
        reading['bytes_total_s']       = data[4]
        reading['bytes_in']            = data[5]
        reading['bytes_out']           = data[6]
        reading['packets_out_s']       = data[7]
        reading['packets_in_s']        = data[8]
        reading['packets_total_s']     = data[9]
        reading['packets_in']          = data[10]
        reading['packets_out']         = data[11]
        reading['errors_out_s']        = data[12]
        reading['errors_in_s']         = data[13]
        reading['errors_in']           = data[14]
        reading['errors_out']          = data[15]

    if mode == 'svg':
        reading['timestamp']           = data[0]
        reading['iface_name']          = data[1]
        reading['bytes_in']            = data[2]
        reading['bytes_out']           = data[3]
        reading['packets_in']          = data[4]
        reading['packets_out']         = data[5]
        reading['errors_in']           = data[6]
        reading['errors_out']          = data[7]

    return reading

@asyncio.coroutine
def get_ifstats():
    global interfaces
    command = 'bwm-ng --output csv'

    # Create the subprocess, redirect the standard output into a pipe
    create = asyncio.create_subprocess_shell(command,
                                            stdout=asyncio.subprocess.PIPE)
    proc = yield from create

    while True:
        # Read one line of output
        data = yield from proc.stdout.readline()
        line = data.decode('ascii').rstrip()

        reading = parse_ifstats(line)

        if reading['iface_name'] in interfaces:
            interfaces[reading['iface_name']]['rx'].append(reading['bytes_in_s'])
            interfaces[reading['iface_name']]['tx'].append(reading['bytes_out_s'])
        else: 
            interfaces['interfaces'].append(reading['iface_name'])

            rx_deque = deque(repeat(0, 100), maxlen=100)
            rx_deque.append(reading['bytes_in_s'])
            tx_deque = deque(repeat(0, 100), maxlen=100)
            tx_deque.append(reading['bytes_out_s'])
                                                         
            interfaces[reading['iface_name']] = {
                'rx': rx_deque,
                'tx': tx_deque
            }

@asyncio.coroutine
def get_trace():
    global interfaces
    print("start packet tracing")
    command = 'python3.5 tracenetwork.py'

    # Create the subprocess, redirect the standard output into a pipe
    create = asyncio.create_subprocess_shell(command,
                                            stdout=asyncio.subprocess.PIPE)
    proc = yield from create

    while True:
        # Read one line of output
        data = yield from proc.stdout.readline()

        interfaces['dscp'] = [0] * len(interfaces['dscp'])

        line = data.decode('ascii').rstrip()
        print(line)
        line = line.replace("marks>", "")


        marks = line.split(',')
        packetstotal = 0
        dscp = {}
        for mark in marks:
            if not mark: continue
            mark = mark.split(':')
            dscpmark = mark[0].strip()
            count = int(mark[1])

            packetstotal = packetstotal + count
            dscp[dscpmark] = count

        #we can break down the packet counts to a percentage, we don't yet, but we should
        for mark,count in dscp.items():
            for d in dscp_mapping:
                if d['value'] == int(mark):
                    interfaces['dscp'][d['index']] = count
                    continue
                #interfaces['dscp'][-1] = interfaces['dscp'][-1] + int(count) #other dscp marks
        print(interfaces['dscp'])

async def start_monitoring(app):
    app.loop.create_task(get_ifstats())
    app.loop.create_task(get_trace())

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    date = loop.run_until_complete(get_ifstats())
    loop.close()

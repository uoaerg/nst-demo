import asyncio.subprocess
import sys
from collections import deque
from itertools import repeat

import pprint

pp = pprint.PrettyPrinter(indent=4)

import ipfwcontrol

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

ipproto_mapping = [
    {"name":"TCP",      "value":6,   "index":0},
    {"name":"UDP",      "value":17,  "index":1},
    {"name":"UDP-LITE", "value":136, "index":2},
    {"name":"SCTP",     "value":132, "index":3},
    {"name":"DCCP",     "value":33,  "index":4},
    {"name":"ICMP",     "value":1,   "index":5},
    {"name":"Other",    "value":255, "index":14},
]

mode = 'rate'
interfaces = { 
    'interfaces':[], 
    'dscp':[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,],
    'ipproto':[0, 0, 0, 0, 0, 0, 0,]
}

dscpmap = {
    "ef":"pass",
    "be":"pass",
    "af11":"pass",
    "af12":"pass",
    "af13":"pass",
    "af21":"pass",
    "af22":"pass",
    "af23":"pass",
    "af31":"pass",
    "af32":"pass",
    "af33":"pass",
    "af41":"pass",
    "af42":"pass",
    "af43":"pass",
}
oldmap = []
mapchange = False

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


        line = data.decode('ascii').rstrip()
        if "marks>" in line:
            interfaces['dscp'] = [0] * len(interfaces['dscp']) #zero out the marks 
            line = line.replace("marks>", "")

    #I think this can be a single function
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

            interfaces['dscp'][-1] = 0
            #we can break down the packet counts to a percentage, we don't yet, but we should
            for mark,count in dscp.items():
                used = False
                for d in dscp_mapping:
                    if d['value'] == int(mark):
                        interfaces['dscp'][d['index']] = count
                        used = True
                        break
                if not used: 
                    interfaces['dscp'][-1] = interfaces['dscp'][-1] + int(count) #other dscp marks


        if "protos>" in line:
            interfaces['ipproto'] = [0] * len(interfaces['ipproto']) #zero out the ipprotos 
            line = line.replace("protos>", "")

            values = line.split(',')
            packetstotal = 0
            protonums = {}
            for value in values:
                if not value: continue
                value = value.split(':')
                num = value[0].strip()
                count = int(value[1])

                packetstotal = packetstotal + count
                protonums[num] = count

            interfaces['ipproto'][-1] = 0
            for num,count in protonums.items():
                used = False
                for d in ipproto_mapping:
                    if d['value'] == int(num):
                        interfaces['ipproto'][d['index']] = count
                        used = True
                        break
                if not used: 
                    interfaces['ipproto'][-1] = interfaces['ipproto'][-1] + int(count) #other ip protocols 
@asyncio.coroutine
def control_firewall():
    global dscpmap
    global mapchange

    print("starting firewall controller")
    command = 'python3.5 ipfwcontrol.py'

    # Create the subprocess, redirect the standard output into a pipe
    create = asyncio.create_subprocess_shell(command,
                                            stdout=asyncio.subprocess.PIPE,
                                            stdin=asyncio.subprocess.PIPE)
    proc = yield from create

    while True:
        yield from asyncio.sleep(1)

        if mapchange:
            dscpcmd = "marks>"
            for mark, action in dscpmap.items():
                dscpcmd += " {}:{},".format(mark, action)
            dscpcmd += "\n"

            yield from ipfwcontrol.ipfw_add_with_cmd(dscpcmd, range(1000,2000))

def setdscpmap(newmap):
    global dscpmap
    global oldmap
    global mapchange

    if oldmap == newmap: 
        mapchange = False
        return
    else:
        mapchange = True
        oldmap = newmap

    dscp = {}
    for mark in dscpmap:
        for d in dscp_mapping:
            if d['name'].lower() == mark:
                if newmap[d['index']]:
                    dscp[mark] = 'pass'
                else:
                    dscp[mark] = 'drop'
    dscpmap = dscp

async def start_monitoring(app):
    app.loop.create_task(get_ifstats())
    app.loop.create_task(get_trace())
    app.loop.create_task(control_firewall())

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    date = loop.run_until_complete(get_ifstats())
    loop.close()

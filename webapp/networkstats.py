import asyncio.subprocess
import sys
from collections import deque

mode = 'rate'
interfaces = { 'interfaces':[]}

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

#            interfaces[reading['iface_name']] = { 
#                'rx': [reading['bytes_in_s']],
#                'tx': [reading['bytes_out_s']]
#            }

            rx_deque = deque(maxlen=100)
            rx_deque.append(reading['bytes_in_s'])
            tx_deque = deque(maxlen=100)
            tx_deque.append(reading['bytes_out_s'])
                                                         
            interfaces[reading['iface_name']] = {
                'rx': rx_deque,
                'tx': tx_deque
            }



async def start_monitoring(app):
    app.loop.create_task(get_ifstats())

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    date = loop.run_until_complete(get_ifstats())
    loop.close()

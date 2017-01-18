#!/usr/bin/evn python3.5

import asyncio.subprocess
import sys

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
]"""

dscp_mapping = {
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

queue = asyncio.Queue()

def _stdin():
    data = sys.stdin.readline()
    asyncio.async(queue.put(data))

# command string like:
# marks> af11:drop, ef:be, be:pass
def parse_dscp(line, dscp_mapping):
    if "marks>" not in line: return {}

    line = line.replace("marks>", "").strip()

    marks = line.split(',')
    dscp = dscp_mapping

    for mark in marks:
        if not mark: continue

        mark = mark.split(':')
        dscpmark = mark[0].strip().lower()
        action = mark[1].strip().lower()

        if dscpmark not in dscp_mapping:
            print("bad mark")
            continue

        if action not in ["pass", "drop"] and action not in dscp_mapping:
            continue
        else:
            for point,y in dscp_mapping.items():
                if dscpmark == point:
                    dscp[dscpmark] = action
    return dscp

async def clear_local_rules(rulerange):

    rules = await list_rules()

    deleted = []
    for rule in rules:
        if not rule['number']: continue

        rule = int(rule['number'])
        if rule not in deleted and rule in rulerange:
            await delete_rule(rule)
            deleted.append(rule)

@asyncio.coroutine
def list_rules():
    command = "sudo ipfw list"

    create = asyncio.create_subprocess_shell(command,
        stdout=asyncio.subprocess.PIPE)
    proc = yield from create

    rules = []
    while True:
        out, err = yield from proc.communicate()
        if not out: return rules

        out = out.decode('ascii')
        lines = out.split("\n")

        for line in lines:
            fields = line.split(" ")
            rules.append({'number':fields[0], 'rule':line})

    return rules

@asyncio.coroutine
def delete_rule(rule):
    command = "sudo ipfw -q delete {}".format(rule)

    create = asyncio.create_subprocess_shell(command,
        stdout=asyncio.subprocess.PIPE)
    proc = yield from create

@asyncio.coroutine
def add_dscp_rule(index, mark, action):
    # we can just add all of these at the same position for now
    command = ""

    #ipfw add setdscp be ip from any to any dscp af11,af21
    if action in "pass":
        command = "sudo ipfw -q {} add pass ip from any to any dscp {}".format(index, mark)
    elif action in "drop":
        command = "sudo ipfw -q {} add drop ip from any to any dscp {}".format(index, mark)
    elif action in dscp_mapping:
        command = "sudo ipfw -q {} add setdscp {} ip from any to any dscp {}".format(index, action, mark)
    else:
        return

    create = asyncio.create_subprocess_shell(command,
        stdout=asyncio.subprocess.PIPE)
    proc = yield from create

async def ipfw(rulerange):
    loop = asyncio.get_event_loop()
    loop.add_reader(sys.stdin, _stdin)
 
    global dscp_mapping
    dscpmap = dscp_mapping

    while True:
        data = await queue.get()
        data = data.rstrip()
       
        if "marks>" in data:
            dscpmap = parse_dscp(data, dscpmap)

            await clear_local_rules(rulerange)
            for mark, action in dscpmap.items():
                await add_dscp_rule(min(rulerange), mark, action)

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    date = loop.run_until_complete(ipfw(range(1000,2000)))
    loop.close()

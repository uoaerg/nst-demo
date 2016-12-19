import plt
import time
import sys

def tracedscp(interfaces):
    trace = plt.trace('bpf:re0')
    trace.start()

    INTERVAL = 1

    dscp = {}
    start = time.time()

    try:
        for pkt in trace:
            ip = pkt.ip
            if not ip:
                continue

            dscpvalue = ip.traffic_class >> 2

            if dscpvalue in dscp:
                dscp[dscpvalue] = dscp[dscpvalue] + 1
            else:
                dscp[dscpvalue] = 1

            done = time.time()

            if done - start > INTERVAL:
                print("marks>".format(len(dscp)), end="")
                for mark,count in dscp.items():
                    print(" {}:{},".format(mark, count), end="")
                print("")
                sys.stdout.flush()
                dscp = {}
                start = done

    except KeyboardInterrupt:
        trace.close()
        sys.exit()

if __name__ == "__main__":
    tracedscp("interfaces")

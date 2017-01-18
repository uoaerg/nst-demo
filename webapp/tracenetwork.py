import plt
import time
import sys

def tracedscp(interfaces):
    trace = plt.trace('bpf:{}'.format(interfaces))
    trace.start()

    INTERVAL = 1

    dscp = {}
    proto = {}
    start = time.time()

    try:
        for pkt in trace:
            ip = pkt.ip
            if not ip:
                continue

            protonum = ip.proto
            dscpvalue = ip.traffic_class >> 2

            if dscpvalue in dscp:
                dscp[dscpvalue] = dscp[dscpvalue] + 1
            else:
                dscp[dscpvalue] = 1

            if protonum in proto:
                proto[protonum] = proto[protonum] + 1
            else:
                proto[protonum] = 1

            done = time.time()

            if done - start > INTERVAL:
                print("marks>", end="")
                for mark,count in dscp.items():
                    print(" {}:{},".format(mark, count), end="")
                print("")
                sys.stdout.flush()

                print("protos>", end="")
                for num,count in proto.items():
                    print(" {}:{},".format(num, count), end="")
                print("")

                sys.stdout.flush()
                dscp = {}
                proto = {}
                start = done

    except KeyboardInterrupt:
        trace.close()
        sys.exit()

if __name__ == "__main__":
    tracedscp("re1")

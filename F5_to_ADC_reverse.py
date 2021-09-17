#   Date: 8/16/2021
#   Version: 0.1
#   Author: Mike

import sys
import os
import re


def usage():
    print("This program takes in a F5 zone file and processes it for ADC")
    print("python F5_to_ADC_reverse <file> [-e]")
    print("-e for single line entries in bind")
    sys.exit(1)


def ends_with_dot(unchecked_name):
    if unchecked_name[-1] == '.':
        return unchecked_name[:-1]
    else:
        return unchecked_name


def dns_zone():
    commands.append(f"add dns zone {soa['domain']} -proxyMode NO")


def dns_soa():
    commands.append(
        f"add dns soaRec {soa['domain']} -originServer {soa['originServer']} -contact {soa['contact']} -serial "
        f"{soa['serial']} -refresh {soa['refresh']} -retry {soa['retry']} -expire {soa['expire']} -minimum "
        f"{soa['minimum']} -TTL {soa['TTL']}")


def dns_nsRec():
    for value in ns:
        commands.append(f"add dns nsRec {value[0]} {value[2]} -TTL {value[1]}")


def dns_ptrRec():
    for value in ptr:
        commands.append(f"add dns ptrRec {value[0]} {value[2]} -TTL {value[1]}")


def print_commands():
    for comm in commands:
        print(comm)


def write_to_file():
    with open(filename_out, 'w') as fout:
        for item in commands:
            fout.write(item + "\n")

in_soa = False
soa_done = False

soa = {}
ns = []
ptr = []

temp_ns = []
temp_ptr = []

commands = []

try:
    filename_orig = os.path.basename(sys.argv[1])
    filename_in = sys.argv[1]
    filename_out = filename_in + "_processed"
except IndexError:
    usage()

try:
    reverse = sys.argv[2]
except:
    reverse = ""

with open(filename_in, 'r') as filein:
    print(f"---- {filename_orig} ---- ")
    for line in filein:
        if reverse == "-e":
            if re.search("IN SOA", line):
                soa['domain'] = (ends_with_dot(line.split()[0]))
                soa['TTL'] = (line.split()[1])
                soa['originServer'] = (ends_with_dot(line.split()[4]))
                soa['contact'] = (ends_with_dot(line.split()[5]))
                soa['serial'] = (line.split()[6])
                soa['refresh'] = (line.split()[7])
                soa['retry'] = (line.split()[8])
                soa['expire'] = (line.split()[9])
                soa['minimum'] = (line.split()[10])

            if re.search("\sNS\s", line):
                temp_ns.append(ends_with_dot(line.split()[0]))
                temp_ns.append(ends_with_dot(line.split()[1]))
                temp_ns.append(ends_with_dot(line.split()[4]))
                ns.append(list.copy(temp_ns))
                temp_ns.clear()

            if re.search("\sPTR\s", line):
                temp_ptr.append(ends_with_dot(line.split()[0]))
                temp_ptr.append(ends_with_dot(line.split()[1]))
                temp_ptr.append(ends_with_dot(line.split()[4]))
                ptr.append(list.copy(temp_ptr))
                temp_ptr.clear()
        else:
            if re.search("\$ORIGIN", line):
                ORIGIN = line.split()[1]

            if re.search("\$TTL", line):
                temp_TTL = line.split()[1]

            if re.search("IN SOA.*\(", line):
                in_soa = True
                soa["domain"] = ends_with_dot(line.split()[0])
                soa["originServer"] = ends_with_dot(line.split()[3])
                soa["contact"] = ends_with_dot(line.split()[4])

            if in_soa:
                if re.search("serial", line):
                    soa['serial'] = line.split()[0].strip()
                if re.search("refresh", line):
                    soa['refresh'] = line.split()[0].strip()
                if re.search("retry", line):
                    soa['retry'] = line.split()[0].strip()
                if re.search("expire", line):
                    soa['expire'] = line.split()[0].strip()
                if re.search("minimum", line):
                    soa['minimum'] = line.split()[0].strip()
                soa['TTL'] = temp_TTL
                if re.search('\)', line):
                    x = re.split("\b\)", line)
                    if x[0].strip() == ')':
                        in_soa = False

            if re.search("\sNS\s", line):
                temp_ns.append(soa['domain'])
                temp_ns.append(temp_TTL)
                temp_ns.append(ends_with_dot(line.split()[1]))
                ns.append(list.copy(temp_ns))
                temp_ns.clear()

            if re.search("\sPTR\s", line):
                temp_ptr.append(line.split()[0] + "." + ends_with_dot(ORIGIN))
                temp_ptr.append(temp_TTL)
                temp_ptr.append(ends_with_dot(line.split()[2]))
                ptr.append(list.copy(temp_ptr))
                temp_ptr.clear()

if __name__ == '__main__':
    dns_soa()
    dns_nsRec()
    dns_zone()    
    dns_ptrRec()

    print_commands()

    write_to_file()


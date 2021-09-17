#   Date: 8/14/2021
#   Version: 0.1
#   Author: Mike

import sys
import os
import re


def usage():
    print("This program takes in a F5 zone file and processes it for ADC")
    print("python F5_to_ADC <file>")
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
        ns1 = ends_with_dot(value[0])
        ns2 = ends_with_dot(value[1])
        commands.append(f"add dns nsRec {ns1} {ns2}")


def dns_aRec():
    for value in a:
        temp_host = ends_with_dot(value[0])
        commands.append(f"add dns addRec {temp_host} {value[1]} -TTL {value[2]}")


def dns_mxRec():
    for value in mx:
        temp_host = ends_with_dot(value[0])
        commands.append(f"add dns mxRec {soa['domain']} -mx {temp_host} -pref {value[1]} -TTL {value[2]}")


def dns_srvRec():
    for value in srv:
        temp_host = ends_with_dot(value[0])
        commands.append(
            f"add dns srvRec {soa['domain']} {temp_host} -priority {value[1]} -weight {value[2]} -port {value[3]}")


def dns_txtRec():
    for value in txt:
        if len(value) == 2:
            commands.append(f"add dns txtRec {value[0]} -TTL {value[1]}")
        if len(value) == 3:
            commands.append(f"add dns txtRec {value[0]} {value[2]} -TTL {value[1]}")
        if len(value) == 4:
            commands.append(f"add dns txtRec {value[0]} {value[2]} {value[3]} -TTL {value[1]}")
        if len(value) == 5:
            commands.append(f"add dns txtRec {value[0]} {value[2]} {value[3]} {value[4]} -TTL {value[1]}")


def dns_cnameRec():
    for value in cname:
        temp_host = ends_with_dot(value[0])
        temp_host2 = ends_with_dot(value[1])
        commands.append(f"add dns cnameRec {temp_host} {temp_host2} -TTL {value[2]}")


def print_commands():
    for comm in commands:
        print(comm)


def write_to_file():
    with open(filename_out, 'w') as fout:
        for item in commands:
            fout.write(item + "\n")


try:
    filename_orig = os.path.basename(sys.argv[1])
    filename_in = sys.argv[1]
    filename_out = filename_in + "_processed"
except IndexError:
    usage()

# ORIGIN = ''
in_soa = False
soa_done = False
temp_host_rec = ""

addr_count = 0
temp_NS_list = []
temp_A_list = []
temp_MX_list = []
temp_SRV_list = []
temp_TXT_list = []
temp_CNAME_list = []
temp_A_hostname = ""
temp_NS_hostname = ""

soa = {
    "domain": "",
    "originServer": "",
    "contact": "",
    "serial": 100,
    "refresh": 3600,
    "retry": 3,
    "expire": 3600,
    "minimum": 5,
    "TTL": 3600,
}
ns = []
a = []
mx = []
ptr = []
srv = []
cname = []
txt = []

commands = []

with open(filename_in, 'r') as filein:
    print(f"---- {filename_orig} ---- ")
    for line in filein:
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
            if len(line.split()) == 2:
                if ORIGIN == ".":
                    temp_NS_list.append(soa['domain'])
                else:
                    temp_NS_list.append(temp_NS_hostname + "." + ORIGIN)
                temp_NS_list.append(line.split()[1])
            if len(line.split()) == 3:
                temp_NS_list.append(line.split()[0] + "." + ORIGIN)
                temp_NS_hostname = line.split()[0]
                temp_NS_list.append(line.split()[2])
            ns.append(list.copy(temp_NS_list))
            temp_NS_list.clear()

        if re.search("\sA\s", line):
            if len(line.split()) == 3:
                temp_host_rec = line.split()[0]
                temp_A_list.append(line.split()[0] + "." + ORIGIN)
                temp_A_hostname = line.split()[0]
                temp_A_list.append(line.split()[2])
                temp_A_list.append(temp_TTL)
            if len(line.split()) == 2:
                if ORIGIN == '.':
                    temp_A_list.append(soa['domain'])
                else:
                    temp_A_list.append(temp_host_rec + "." + ORIGIN)
                temp_A_list.append(line.split()[1])
                temp_A_list.append(temp_TTL)
            a.append(list.copy(temp_A_list))
            temp_A_list.clear()

        if re.search("\sMX\s", line):
            temp_MX_list.append(line.split()[2])
            temp_MX_list.append(line.split()[1])
            temp_MX_list.append(temp_TTL)
            mx.append(list.copy(temp_MX_list))
            temp_MX_list.clear()

        if re.search("\sSRV\s", line):
            temp_SRV_list.append(line.split()[0] + "." + ORIGIN)
            temp_SRV_list.append(line.split()[2])
            temp_SRV_list.append(line.split()[3])
            temp_SRV_list.append(line.split()[4])
            temp_SRV_list.append(line.split()[5])
            srv.append(list.copy(temp_SRV_list))
            temp_SRV_list.clear()

        if re.search("\sTXT\s", line):
            if len(line.split()) == 2:
                temp_TXT_list.append(ends_with_dot(soa['domain']))
                temp_TXT_list.append(temp_TTL)
                temp_TXT_list.append((re.findall('\".*?\"', line))[0])
            elif len(line.split()) == 3:
                temp_TXT_list.append(ends_with_dot(line.split()[0] + "." + ORIGIN))
                temp_TXT_list.append(temp_TTL)
                temp_TXT_list.append((re.findall('\".*?\"', line))[0])
            elif len(line.split()) == 4:
                temp_TXT_list.append(ends_with_dot(line.split()[0] + "." + ORIGIN))
                temp_TXT_list.append(temp_TTL)
                temp_TXT_list.append((re.findall('\".*?\"', line))[0])
                temp_TXT_list.append((re.findall('\".*?\"', line))[1])
            else:
                temp_TXT_list.append(ends_with_dot(line.split()[0] + "." + ORIGIN))
                temp_TXT_list.append(temp_TTL)
                temp_TXT_list.append((re.findall('\".*?\"', line))[0])
                try:
                    temp_TXT_list.append((re.findall('\".*?\"', line))[1])
                except:
                    pass
                try:
                    temp_TXT_list.append((re.findall('\".*?\"', line))[2])
                except:
                    pass
            txt.append(list.copy(temp_TXT_list))
            temp_TXT_list.clear()

        if re.search("\sCNAME\s", line):
            temp_CNAME_list.append(line.split()[0] + "." + ORIGIN)
            temp_CNAME_list.append(line.split()[2])
            temp_CNAME_list.append(temp_TTL)
            cname.append(list.copy(temp_CNAME_list))
            temp_CNAME_list.clear()

if __name__ == '__main__':
    dns_soa()
    dns_nsRec()
    dns_zone()    
    dns_aRec()
    dns_mxRec()
    dns_srvRec()
    dns_cnameRec()
    dns_txtRec()

    print_commands()

    write_to_file()

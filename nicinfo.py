import sys, os, getopt, subprocess
from os.path import exists, abspath, dirname, basename
import json
import re

# The PCI device class for ETHERNET devices
ETHERNET_CLASS = "0200"

# global dict ethernet devices present. Dictionary indexed by PCI address.
# Each device within this is itself a dictionary of device properties
devices = {}

# This is roughly compatible with check_output function in subprocess module
# which is only available in python 2.7.
def check_output(args, stderr=None):
    '''Run a command and capture its output'''
    return subprocess.Popen(args, stdout=subprocess.PIPE,
                            stderr=stderr, universal_newlines = True).communicate()[0]

def get_pci_device_details(dev_id):
    '''This function gets additional details for a PCI device'''
    device = {}

    extra_info = check_output(["lspci", "-vmmks", dev_id]).splitlines()

    # parse lspci details
    for line in extra_info:
        if len(line) == 0:
            continue
        name, value = line.split("\t", 1)
        name = name.strip(":") + "_str"
        device[name] = value
    # check for a unix interface name
    sys_path = "/sys/bus/pci/devices/%s/net/" % dev_id
    if exists(sys_path):
        device["Interface"] = ",".join(os.listdir(sys_path))
    else:
        device["Interface"] = ""
    # check if a port is used for ssh connection
    device["Ssh_if"] = False
    device["Active"] = ""

    return device

def get_nic_details():
    '''This function populates the "devices" dictionary. The keys used are
    the pci addresses (domain:bus:slot.func). The values are themselves
    dictionaries - one for each NIC.'''
    global devices
    devinfos = []
    # clear any old data
    devices = {}
    # first loop through and read details for all devices
    # request machine readable format, with numeric IDs
    dev = {};
    dev_lines = check_output(["lspci", "-Dvmmn"]).splitlines()
    for dev_line in dev_lines:
        if (len(dev_line) == 0):
            if dev["Class"] == ETHERNET_CLASS:
                #convert device and vendor ids to numbers, then add to global
                dev["Vendor"] = int(dev["Vendor"],16)
                dev["Device"] = int(dev["Device"],16)
                devices[dev["Slot"]] = dict(dev) # use dict to make copy of dev
        else:
            #values = re.split(r'\t+', str(dev_line))
            #name, value = dev_line.split(b'\t')
            name, value = dev_line.split("\t", 1)
            dev[name.rstrip(":")] = value

    # based on the basic info, get extended text details
    for d in devices.keys():
        # get additional info and add it to existing data

        #devices[d] = dict(devices[d].items() +
        #                  get_pci_device_details(d).items())
        devices[d].update(get_pci_device_details(d).items())
        devinfos.append(devices[d])
    return devinfos


def dev_id_from_dev_name(dev_name):
    '''Take a device "name" - a string passed in by user to identify a NIC
    device, and determine the device id - i.e. the domain:bus:slot.func - for
    it, which can then be used to index into the devices array'''
    dev = None
    # check if it's already a suitable index
    if dev_name in devices:
        return dev_name
    # check if it's an index just missing the domain part
    elif "0000:" + dev_name in devices:
        return "0000:" + dev_name
    else:
        # check if it's an interface name, e.g. eth1
        for d in devices.keys():
            if dev_name in devices[d]["Interface"].split(","):
                return devices[d]["Slot"]
    # if nothing else matches - error
    print ("Unknown device: %s. " \
        "Please specify device in \"bus:slot.func\" format" % dev_name)
    sys.exit(1)

def main():
    '''program main function'''
    global devices
    dev_list = get_nic_details()
    for dev in dev_list:
        print(dev["Slot"])
        print(dev["Interface"])


if __name__ == "__main__":
    main()

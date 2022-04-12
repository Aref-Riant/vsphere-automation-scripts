import requests
import urllib3
import argparse
import configparser

from vmware.vapi.vsphere.client import create_vsphere_client
from com.vmware.vcenter_client import VM
from com.vmware.vcenter_client import (Folder)

session = requests.session()

# Disable cert verification for demo purpose. 
# This is not recommended in a production environment.
session.verify = False

# Disable the secure connection warning for demo purpose.
# This is not recommended in a production environment.
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

## Read configs from 'config.ini' file
## Config file is like:
# [CRED]
# server = 172.16.0.100
# username = Administrator@vcenter-domain.com
# password = 123456789

config = configparser.ConfigParser()
config.read('config.ini')

# Connect to a vCenter Server using username and password
vsphere_client = create_vsphere_client(server=config['CRED']['server'], username=config['CRED']['username'], password=config['CRED']['password'], session=session)

# Define parser to get arguments
parser = argparse.ArgumentParser(description='Arguments to run folderwise operations')
required_args = parser.add_argument_group('required arguments')
required_args.add_argument('-f', '--folder',
                        action='store',
                        required=False,
                        help='folder_name')
required_args.add_argument('-o', '--operation',
                        action='store',
                        required=False,
                        help='operation to run',
                        default='start')
args = parser.parse_args()

# Get all virtual machine folders from vsphere
folder_summaries = vsphere_client.vcenter.Folder.list(Folder.FilterSpec(type=Folder.Type.VIRTUAL_MACHINE))
folder_names = []

# if not folder id is defined, print list of folders
if not args.folder:
    print("List of folders: ")
    print("FolderID  FolderName")
    print("----")
for f in folder_summaries:
    folder_names.append((f.folder,f.name))
    if not args.folder:
      print(f.folder, f.name)

# if no folder id defined, show help and exit the script
if not args.folder:
  print("----\n\nRun script with -f <folderID> -o <operation>")
  print("Operations: start, suspend, reset, stop")
  exit()

# Get list of VMs in specified folder
vm_filter = VM.FilterSpec(folders=set([args.folder]))
folder_vms = vsphere_client.vcenter.VM.list(vm_filter)

# Run speciefied operation on all VMs in folder
for vm in folder_vms:
  if args.operation == "start":
    if not vm.power_state == "POWERED_ON":
      vsphere_client.vcenter.vm.Power.start(vm.vm)
      print("Powering on ", vm.name, "from state: ", vm.power_state)
  elif args.operation == "suspend":
      if vm.power_state == "POWERED_ON":
          vsphere_client.vcenter.vm.Power.suspend(vm.vm)
          print("Suspending ", vm.name, "from state: ", vm.power_state)
  elif args.operation == "reset":
      if vm.power_state == "POWERED_ON":
        vsphere_client.vcenter.vm.Power.reset(vm.vm)
      print("Restarting ", vm.name, "from state: ", vm.power_state)
  elif args.operation == "stop":
      if not vm.power_state == "POWERED_OFF":
          vsphere_client.vcenter.vm.Power.stop(vm.vm)
          print("Powering off ", vm.name, "from state: ", vm.power_state)

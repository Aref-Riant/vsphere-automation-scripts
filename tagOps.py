import requests
import urllib3
import argparse
import configparser

from vmware.vapi.vsphere.client import create_vsphere_client
from com.vmware.vcenter_client import VM
from com.vmware.vcenter_client import (Folder)
from com.vmware.cis.tagging_client import (Category, CategoryModel, Tag,
                                           TagAssociation)

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
required_args.add_argument('-t', '--tagname',
                        action='store',
                        required=False,
                        help='tag_name')
required_args.add_argument('-o', '--operation',
                        action='store',
                        required=False,
                        help='operation to run',
                        default='start')

args = parser.parse_args()

# Get all virtual machine folders from vsphere

tag_ids = vsphere_client.tagging.Tag.list()


# if no tag id is defined, print list of tags
if not args.tagname:
    print("List of tags: ")
    print("TagID  TagName")
    print("----")
    for t in tag_ids:
      tag_model = vsphere_client.tagging.Tag.get(t)
      print(tag_model.id, tag_model.name)

# if no tag id defined, show help and exit the script
if not args.tagname:
  print("----\n\nRun script with -t <tagName> -o <operation>")
  print("use command below for auto approval: ")
  print("echo 'y' | python3 tagops.py -t critical -o start")
  print("Operations: start, suspend, reset, stop")
  exit()

op_tag_id = ""

for tag_id in tag_ids:
    tag_model = vsphere_client.tagging.Tag.get(tag_id)
    if tag_model.name == args.tagname:
        op_tag_id = tag_model.id

op_vm_models = vsphere_client.tagging.TagAssociation.list_attached_objects(op_tag_id)
op_vm_ids = []
for vmm in op_vm_models:
    op_vm_ids.append(vmm.id)

op_vm_ids = set(op_vm_ids)
op_vms = vsphere_client.vcenter.VM.list(VM.FilterSpec(vms=(op_vm_ids)))

# print effected VMs and ask for approval

print("This is list of VMs effected by operation: ", args.operation)
for opvm in op_vms:
  print(opvm.name, opvm.power_state)

approval = input("Type y or yes if you approve: ")
if approval.lower() == "y" or approval.lower() == "yes" :
  print("Starting operation...")
else:
  print("Approval failed, exiting...")
  exit()


# Run speciefied operation on all VMs in folder
for vm in op_vms:
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

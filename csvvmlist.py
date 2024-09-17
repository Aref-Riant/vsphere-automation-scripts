import atexit
import ssl
import urllib3
from pyVmomi import vim, vmodl
from pyVim.connect import SmartConnect, Disconnect

## first install: pip install pyvmomi
## run: python csvvmlist.py
## output: vmreport.csv


VCENTER_USERNAME = "user@company.com"
VCENTER_PASSWORD = "*******"
VCENTER_URL =      "vcenter.company.com"


def list_vms_and_folders(service_instance):
    """Lists all VMs and their folders in the vCenter."""

    content = service_instance.RetrieveServiceContent()
    container = content.rootFolder
    view_manager = content.viewManager
    child_entity_view = view_manager.CreateContainerView(container, [vim.VirtualMachine], True)

    for vm in child_entity_view.view:
        folder_path = get_vm_folder_path(vm, content)
        #print(f"VM Name: {vm.name}, Folder: {folder_path}")

        cpuNum = vm.config.hardware.numCPU
        memoryGB = int(vm.config.hardware.memoryMB)/1024
        disks = []
        Nics = 0

        for device in vm.config.hardware.device:
            if isinstance(device, vim.vm.device.VirtualDisk):
                disks.append(str(device.capacityInKB/1024/1024))
            if isinstance(device, vim.vm.device.VirtualEthernetCard):
                Nics += 1

        diskList = ';'.join(disks)
        yield(f"{ vm.name }, { folder_path }, { cpuNum }, { memoryGB }, { Nics }, { diskList }")



    child_entity_view.Destroy()

def get_vm_folder_path(vm, content):
    """Gets the folder path of a VM."""

    folder_path = []
    current_folder = vm.parent
    while current_folder:
        folder_path.insert(0, current_folder.name)
        current_folder = current_folder.parent

    return "/".join(folder_path)

def main():
    """Main function to connect to vCenter and list VMs."""

    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE  # Disable certificate verification for self-signed certs
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    service_instance = SmartConnect(host=VCENTER_URL, user=VCENTER_USERNAME, pwd=VCENTER_PASSWORD, sslContext=ssl_context)
    atexit.register(Disconnect, service_instance)

    outfile = open('vmreport.csv', 'w')
    outfile.write("Name,Folder,#CPU,RamGB,#NIC,DISKsGB" + "\n")
    #print("Name,Folder,#CPU,RamGB,#NIC,DISKsGB")


    for line in list_vms_and_folders(service_instance):
        outfile.write(line + "\n")
    outfile.close()

if __name__ == '__main__':
    main()

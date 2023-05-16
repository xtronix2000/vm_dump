import ssl
from configparser import ConfigParser
from pyVmomi import vim
from pyVim.connect import SmartConnect, Disconnect
import datetime
import json


#  ------------------------------File_import------------------------------
config = ConfigParser()
config.read('credentials.ini')
#  ------------------------------Connection------------------------------
s = ssl.create_default_context(purpose=ssl.Purpose.CLIENT_AUTH)
s.verify_mode = ssl.CERT_NONE
c = SmartConnect(**config['VSphere'], sslContext=s)


#  --------------------------------------------Get basic information of all VMs---------------------------------------
def get_all_info():
    managed_objects = c.content.viewManager.CreateContainerView(c.content.rootFolder, [vim.VirtualMachine], True).view
    vm_list = [
        {'vmName': j.name,
         'ipAddress': j.summary.guest.ipAddress,
         'host': j.summary.runtime.host.name,
         'storageUsageGB': str(round(j.summary.storage.committed / 1024 ** 3, 2)),  # float
         'memorySizeGB': str(j.config.hardware.memoryMB // 1024),  # int
         'numCPU': str(j.config.hardware.numCPU),  # int
         'corePerSocket': str(j.config.hardware.numCoresPerSocket),  # int
         'guestFullName': j.summary.config.guestFullName,
         'powerState': j.summary.runtime.powerState,
         'uptime': str(datetime.timedelta(seconds=j.summary.quickStats.uptimeSeconds))
         } for j in managed_objects]
    return vm_list


vm_info_list = get_all_info()


with open(f'results/dump_{datetime.datetime.now().strftime("%d.%m.%Y_%H.%M.%S")}.json', 'w') as f:
    f.write(json.dumps(vm_info_list, ensure_ascii=False, indent=4))


Disconnect(c)  # important

import ssl
import json
import datetime
from pyVmomi import vim
from configparser import ConfigParser
from pyVim.connect import SmartConnect, Disconnect


config = ConfigParser()
config.read('credentials.ini')


s = ssl.create_default_context(purpose=ssl.Purpose.CLIENT_AUTH)
s.verify_mode = ssl.CERT_NONE
c = SmartConnect(**config['VSphere'], sslContext=s)


def get_all_info():
    managed_objects = c.content.viewManager.CreateContainerView(c.content.rootFolder, [vim.VirtualMachine], True).view
    vm_list = [
        {'vmName': j.name,
         'ipAddress': j.summary.guest.ipAddress,
         'host': j.summary.runtime.host.name,
         'storageUsageGB': round(j.summary.storage.committed / 1024 ** 3, 2),
         'memorySizeGB': j.config.hardware.memoryMB // 1024,
         'numCPU': j.config.hardware.numCPU,
         'corePerSocket': j.config.hardware.numCoresPerSocket,
         'guestFullName': j.summary.config.guestFullName,
         'powerState': j.summary.runtime.powerState,
         'uptime': datetime.timedelta(seconds=j.summary.quickStats.uptimeSeconds)
         } for j in managed_objects]
    return vm_list


vm_info_list = get_all_info()


with open(f'results/dump_{datetime.datetime.now().strftime("%d.%m.%Y_%H.%M.%S")}.json', 'w') as f:
    f.write(json.dumps(vm_info_list, ensure_ascii=False, indent=4))


Disconnect(c)

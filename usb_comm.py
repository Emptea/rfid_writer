import usb
import struct
import time
import sys

def usb_write(device, msg):
    r = b'\xcb'
    dx = msg.replace(r, r*(65 - len(msg)))
    device.write(0x01,dx,1000) # bulk out

def usb_read(device):
    data = device.read(0x81,64,1000) # bulk in
    b = bytes(bytearray(data))
    prot, rx_sz, tx_sz = struct.unpack('>3xc2h', data[0:8])
    print('0x'+prot.hex(), rx_sz, tx_sz)
    resp = data[8:8+tx_sz]
    return(resp)

def read_reg_x23 (device):
    msg = bytearray([0x00, 0x06, 0x00, 0x69, 0x00, 0x01, 0x00, 0x01, 0x23, 0xcb])
    usb_write(device, msg)
    return usb_read(device)

def rfid_on(device):
    msg = bytearray([0x03, 0x07, 0x00, 0x44, 0x00, 0x02, 0x00, 0x00, 0x22, 0x01, 0xcb])
    usb_write(device, msg)
    return usb_read(device)

def rfid_off(device):
    msg = bytearray([0x05, 0x07, 0x00, 0x44, 0x00, 0x02, 0x00, 0x00, 0x22, 0x00, 0xcb])
    usb_write(device, msg)
    return usb_read(device)

def rfid_read(device):
    msg = bytearray([0x03, 0x08, 0x00, 0x44, 0x00, 0x03, 0x00, 0x11, 0xa1, 0x26, 0x01, 0xcb])
    usb_write(device, msg)
    return usb_read(device)

def iso14443a_on(device):
    msg = bytearray([0x02, 0x06, 0x00, 0x44, 0x00, 0x01, 0x00, 0x00, 0xa0, 0xcb])
    usb_write(device, msg)
    return usb_read(device)

def iso14443a_off(device):
    msg = bytearray([0x04, 0x06, 0x00, 0x44, 0x00, 0x01, 0x00, 0x00, 0xaf, 0x00, 0xcb])
    usb_write(device, msg)
    return usb_read(device)


dev = usb.core.find(idProduct = 0x3721)
i = dev[0].interfaces()[0].bInterfaceNumber

if dev is None:
    raise ValueError('Our device is not connected')
else:
    print("Device connected")

## SECTION: this should be on Ubuntu; not required for Windows
if dev.is_kernel_driver_active(i):
    try:
        dev.detach_kernel_driver(i)
    except usb.core.USBError as e:
        sys.exit("Could not detatch kernel driver from interface({0}): {1}".format(i, str(e)))
##

dev.set_configuration()
cfg = dev.get_active_configuration()
intf = cfg[(0,0)]

ep_in = intf[0]
ep_out = intf[1]
print(ep_out)

for i in range(10):
    iso14443a_on(dev)
    ids =  rfid_read(dev)
    print(' '.join(hex(x) for x in ids))
    iso14443a_off(dev)
    time.sleep(1)
# -*- coding: utf-8 -*-

from ctypes import (
    CDLL, CFUNCTYPE, POINTER,
    c_int, c_void_p,
    c_uint, c_ubyte,
    pointer, create_string_buffer
)


# load the kdriveExpress (kdriveExpress.so)
kdrive = CDLL('/home/pi/knx/testar/libkdriveExpress.so')

# The KNX Group Address (destination address) we use to send with
address = 0x1001

# Logging levels (not available from the library)
KDRIVE_LOGGER_FATAL = 1
KDRIVE_LOGGER_INFORMATION = 6

# defines from kdrive (not available from the library)
KDRIVE_INVALID_DESCRIPTOR = -1
KDRIVE_ERROR_NONE = 0
SERIAL_NUMBER_LENGTH = 6

def main():
    # Configure the logging level and console logger
    kdrive.kdrive_logger_set_level(KDRIVE_LOGGER_INFORMATION)
    kdrive.kdrive_logger_console()

    # We create a Access Port descriptor. This descriptor is then used for
    # all calls to that specific access port.
    ap = open_access_port()

    if ap == -1:
        kdrive.kdrive_logger(KDRIVE_LOGGER_FATAL, 'Unable to create access port. This is a terminal failure')
        while 1:
            pass
    
    lightSwitch = 0

    while (lightSwitch = 1 or lightSwitch = 0):
        
        # send a 1-Bit boolean GroupValueWrite telegram: on
        buffer = (c_ubyte * 1)(lightSwitch)
        kdrive.kdrive_ap_group_write(ap, address, buffer, 1)
        kdrive.kdrive_logger(KDRIVE_LOGGER_INFORMATION, "Send Group {0}, Value{1} ".format(hex(address), lightSwitch))

        kdrive.kdrive_logger(KDRIVE_LOGGER_INFORMATION, "Press 0 to turn off light and 1 to turn on light")
        lightSwitch = raw_input('')
        print lightSwitch
    else:
        print 'Statement not fullfilled: {0}'.format(lightSwitch)
    

    # close and release the access port
    kdrive.kdrive_ap_close(ap)
    kdrive.kdrive_ap_release(ap)


def open_access_port():
    ap = kdrive.kdrive_ap_create()
   
    if (ap != KDRIVE_INVALID_DESCRIPTOR):
        
        if kdrive.kdrive_ap_open_serial_ft12(ap, "/dev/ttyAMA0") != KDRIVE_ERROR_NONE:
            kdrive.kdrive_ap_release(ap)
            ap = KDRIVE_INVALID_DESCRIPTOR
    return ap

if __name__ == '__main__':
    main()

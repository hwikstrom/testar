# -*- coding: utf-8 -*-

from ctypes import (
    CDLL, CFUNCTYPE, POINTER,
    c_int, c_void_p,
    c_uint, c_ubyte,
    pointer, create_string_buffer
)


# load the kdriveExpress (kdriveExpress.so)
kdrive = CDLL('/home/pi/knx/testar/libkdriveExpress.so')

# Enable to use the kdrive access packet trace
kdrive_packet_trace = False

# The KNX Group Address (destination address) we use to send with
address = 0x1001

# the error, event and telegram callback pointer to function type
ERROR_CALLBACK = CFUNCTYPE(None, c_int, c_void_p)
EVENT_CALLBACK = CFUNCTYPE(None, c_int, c_uint, c_void_p)
TELEGRAM_CALLBACK = CFUNCTYPE(None, POINTER(c_ubyte), c_uint, c_void_p)

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

    # We register an error callback as a convenience logger function to
    # print out the error message when an error occurs.
    error_callback = ERROR_CALLBACK(on_error_callback)
    kdrive.kdrive_register_error_callback(error_callback, None)

    # We create a Access Port descriptor. This descriptor is then used for
    # all calls to that specific access port.
    ap = open_access_port()

    if ap == -1:
        kdrive.kdrive_logger(KDRIVE_LOGGER_FATAL, 'Unable to create access port. This is a terminal failure')
        while 1:
            pass

    # We register an event callback to notify of the Access Port Events
    # For example: KDRIVE_EVENT_TERMINATED
    event_callback = EVENT_CALLBACK(on_event_callback)
    kdrive.kdrive_set_event_callback(ap, event_callback, None)

    if kdrive_packet_trace:
        kdrive.kdrive_ap_packet_trace_connect(ap)

    # send a 1-Bit boolean GroupValueWrite telegram: on
    buffer = (c_ubyte * 1)(1)
    kdrive.kdrive_ap_group_write(ap, address, buffer, 1)

    # now we simply go into bus monitor mode, and display received telegrams
    key = c_int(0)
    telegram_callback = TELEGRAM_CALLBACK(on_telegram_callback)
    kdrive.kdrive_ap_register_telegram_callback(ap, telegram_callback, None, pointer(key))

    kdrive.kdrive_logger(KDRIVE_LOGGER_INFORMATION, "Entering BusMonitor Mode")
    kdrive.kdrive_logger(KDRIVE_LOGGER_INFORMATION, "Press [Enter] to exit the application ...")
    i = raw_input('')

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


def on_error_callback(e, user_data):
    len = 1024
    str = create_string_buffer(len)
    kdrive.kdrive_get_error_message(e, str, len)
    print 'kdrive error {0} {1}'.format(hex(e), str.value)


def on_event_callback(ap, e, user_data):
    print 'kdrive event {0}'.format(hex(e))
    print 'User Data: : : '
    print e


def on_telegram_callback(telegram, telegram_len, user_data):
    l = list(telegram_len, telegram)
    hex = ' '.join('0x%02x' % b for b in l)
    print hex


def list(count, p_items):
    """Returns a python list for the given times represented by a pointer and the number of items"""
    items = []
    for i in range(count):
        items.append(p_items[i])
    return items


if __name__ == '__main__':
    main()

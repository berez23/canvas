#!/usr/bin/env python
##ImmunityHeader v1
###############################################################################
## File       :  svcctl.py
## Description:
##            :
## Created_On :  Tue Dec 23 2014
## Created_By :  X.
##
## (c) Copyright 2010, Immunity, Inc. all rights reserved.
###############################################################################


import sys
import logging
from struct import pack, unpack

if '.' not in sys.path:
    sys.path.append('.')

from libs.newsmb.libdcerpc import DCERPC, DCERPCString, DCERPCSid
from libs.newsmb.libdcerpc import RPC_C_AUTHN_WINNT, RPC_C_AUTHN_LEVEL_PKT_INTEGRITY
from libs.newsmb.Struct import Struct

###
# Constants
###

SVCCTL_COM_CLOSESERVICEHANDLE = 0
SVCCTL_COM_CONTROLSERVICE = 1
SVCCTL_COM_DELETESERVICE = 2
SVCCTL_COM_QUERYSERVICESTATUS = 6
SVCCTL_COM_CREATESERVICE_W = 12
SVCCTL_COM_OPENSCMANAGER = 15
SVCCTL_COM_OPENSERVICE_A = 18
SVCCTL_COM_OPENSERVICE_W = 16
SVCCTL_COM_STARTSERVICE_A = 31
SVCCTL_COM_STARTSERVICE_W = 19
SVCCTL_COM_ENUMSERVICESSTATUS = 14
SVCCTL_COM_ENUMSERVICESSTATUSEX = 42

# Service state (filter for enumeration)
SVCCTL_SERVICE_ACTIVE = 0x00000001
SVCCTL_SERVICE_INACTIVE = 0x00000002
SVCCTL_SERVICE_STATE_ALL = 0x00000003

# Service type
SVCCTL_SERVICE_DRIVER = 0x0B
SVCCTL_SERVICE_FILE_SYSTEM_DRIVER = 0x02
SVCCTL_SERVICE_KERNEL_DRIVER = 0x01
SVCCTL_SERVICE_WIN32 = 0x30
SVCCTL_SERVICE_WIN32_OWN_PROCESS = 0x10
SVCCTL_SERVICE_WIN32_SHARE_PROCESS = 0x20
SVCCTL_SERVICE_ALL_DRIVERS = SVCCTL_SERVICE_DRIVER|SVCCTL_SERVICE_FILE_SYSTEM_DRIVER|SVCCTL_SERVICE_KERNEL_DRIVER
SVCCTL_SERVICE_ALL_PROCESS = SVCCTL_SERVICE_WIN32|SVCCTL_SERVICE_WIN32_OWN_PROCESS|SVCCTL_SERVICE_WIN32_SHARE_PROCESS
SVCCTL_SERVICE_ALL = SVCCTL_SERVICE_ALL_DRIVERS|SVCCTL_SERVICE_ALL_PROCESS

# Current state of the service
SVCCTL_SERVICE_CONTINUE_PENDING =0x00000005
SVCCTL_SERVICE_PAUSE_PENDING = 0x00000006
SVCCTL_SERVICE_PAUSED = 0x00000007
SVCCTL_SERVICE_RUNNING = 0x00000004
SVCCTL_SERVICE_START_PENDING = 0x00000002
SVCCTL_SERVICE_STOP_PENDING = 0x00000003
SVCCTL_SERVICE_STOPPED = 0x00000001

# Info Level
SVCCTL_ENUM_PROCESS_INFO = 0

# Start Type
SVCCTL_SERVICE_BOOT_START = 0x00
SVCCTL_SERVICE_SYSTEM_START = 0x01
SVCCTL_SERVICE_AUTO_START = 0x02
SVCCTL_SERVICE_DEMAND_START = 0x03
SVCCTL_SERVICE_DISABLED = 0x04

# Error control
SVCCTL_SERVICE_ERROR_IGNORE = 0
SVCCTL_SERVICE_ERROR_NORMAL = 1
SVCCTL_SERVICE_ERROR_SEVERE = 2
SVCCTL_SERVICE_ERROR_CRITICAL = 3

# AccessMask
SVCCTL_SERVICE_ALL_ACCESS = 0xF01FF
SVCCTL_SERVICE_CHANGE_CONFIG = 0x02
SVCCTL_SERVICE_ENUMERATE_DEPENDENTS = 0x08
SVCCTL_SERVICE_INTERROGATE = 0x80
SVCCTL_SERVICE_PAUSE_CONTINUE = 0x40
SVCCTL_SERVICE_QUERY_CONFIG = 0x01
SVCCTL_SERVICE_QUERY_STATUS = 0x04
SVCCTL_SERVICE_START = 0x10
SVCCTL_SERVICE_STOP = 0x20
SVCCTL_SERVICE_USER_DEFINED_CONTROL = 0x100
SVCCTL_SERVICE_SET_STATUS = 0x8000

# Control
SVCCTL_SERVICE_CONTROL_CONTINUE = 0x00000003
SVCCTL_SERVICE_CONTROL_INTERROGATE = 0x00000004
SVCCTL_SERVICE_CONTROL_NETBINDADD = 0x00000007
SVCCTL_SERVICE_CONTROL_NETBINDDISABLE = 0x0000000A
SVCCTL_SERVICE_CONTROL_NETBINDENABLE = 0x00000009
SVCCTL_SERVICE_CONTROL_NETBINDREMOVE = 0x00000008
SVCCTL_SERVICE_CONTROL_PARAMCHANGE = 0x00000006
SVCCTL_SERVICE_CONTROL_PAUSE = 0x00000002
SVCCTL_SERVICE_CONTROL_STOP = 0x00000001

# Controls Accepted
SVCCTL_SERVICE_ACCEPT_NETBINDCHANGE = 0x00000010
SVCCTL_SERVICE_ACCEPT_PARAMCHANGE = 0x00000008
SVCCTL_SERVICE_ACCEPT_PAUSE_CONTINUE = 0x00000002
SVCCTL_SERVICE_ACCEPT_PRESHUTDOWN = 0x00000100
SVCCTL_SERVICE_ACCEPT_SHUTDOWN = 0x00000004
SVCCTL_SERVICE_ACCEPT_STOP = 0x00000001
SVCCTL_SERVICE_ACCEPT_HARDWAREPROFILECHANGE = 0x00000020
SVCCTL_SERVICE_ACCEPT_POWEREVENT = 0x00000040
SVCCTL_SERVICE_ACCEPT_SESSIONCHANGE = 0x00000080
SVCCTL_SERVICE_ACCEPT_TIMECHANGE = 0x00000200
SVCCTL_SERVICE_ACCEPT_TRIGGEREVENT = 0x00000400
SVCCTL_SERVICE_ACCEPT_USERMODEREBOOT = 0x00000800


###
# SVCCTL objects
# No exception handling for these objects.
###

#http://msdn.microsoft.com/en-us/library/windows/desktop/ms685996(v=vs.85).aspx
class SVCCTLServiceStatus(Struct):
    st = [
        ['ServiceType', '<L', SVCCTL_SERVICE_WIN32],
        ['CurrentState', '<L', SVCCTL_SERVICE_PAUSED],
        ['ControlsAccepted', '<L', 0],
        ['Win32ExitCode', '<L', 0],
        ['ServiceSpecificExitCode', '<L', 0],
        ['CheckPoint', '<L', 0],
        ['WaitHint', '<L', 0],
    ]

    def __init__(self, data=None,
                       type=SVCCTL_SERVICE_WIN32,
                       state=SVCCTL_SERVICE_PAUSED,
                       is_unicode=True):
        Struct.__init__(self, data)

        if not data:
            self['ServiceType'] = type
            self['CurrentState'] = state

    def pack(self):
        return Struct.pack(self)

    def get_type(self):
        return self['ServiceType']

    def get_state(self):
        return self['CurrentState']

###
# Handlers
# No exception handling for these objects.
###


# Opnum 0
class SVCCTLCloseServiceHandleRequest(Struct):
    st = [
        ['ServiceHandle', '20s', '\x00'*20],
    ]

    def __init__(self, data=None, service_handle='', is_unicode=True):
        Struct.__init__(self, data)

        if not data:
            self['ServiceHandle'] = service_handle

    def pack(self):
        return Struct.pack(self)

# Opnum 1
class SVCCTLControlServiceRequest(Struct):
    st = [
        ['ServiceHandle', '20s', '\x00'*20],
        ['Control', '<L', 0]
    ]

    def __init__(self, data=None, service_handle='', control=SVCCTL_SERVICE_CONTROL_STOP, is_unicode=True):
        Struct.__init__(self, data)

        if not data:
            self['ServiceHandle'] = service_handle
            self['Control'] = control

    def pack(self):
        return Struct.pack(self)

class SVCCTLCloseServiceHandleResponse(Struct):
    st = [
        ['ServiceHandle', '20s', '\x00'*20],
        ['retvalue', '<L', 0 ]
    ]

    def __init__(self, data=None, service_handle='\x00'*20, is_unicode=True):
        Struct.__init__(self, data)

        if not data:
            self['ServiceHandle'] = service_handle

    def pack(self):
        return Struct.pack(self)

# Opnum 2
class SVCCTLDeleteServiceRequest(Struct):
    st = [
        ['ServiceHandle', '20s', '\x00'*20],
    ]

    def __init__(self, data=None, service_handle='\x00'*20, is_unicode=True):
        Struct.__init__(self, data)

        if not data:
            self['ServiceHandle'] = service_handle

    def pack(self):
        return Struct.pack(self)


# Opnum 6
class SVCCTLQueryServiceStatusRequest(Struct):
    st = [
        ['ServiceHandle', '20s', '\x00'*20],
    ]

    def __init__(self, data=None, service_handle='\x00'*20, is_unicode=True):
        Struct.__init__(self, data)

        if not data:
            self['ServiceHandle'] = service_handle

    def pack(self):
        return Struct.pack(self)

class SVCCTLQueryServiceStatusResponse(Struct):
    st = [
        ['ServiceStatus', '0s', ''],
        ['retvalue', '<L', 0 ]
    ]

    def __init__(self, data=None, service_status=None, retvalue=0, is_unicode=True):
        Struct.__init__(self, data)

        if not data:
            self['ServiceStatus'] = service_status
            self['retvalue'] = retvalue
        else:
            self['ServiceStatus'] = SVCCTLServiceStatus(data=data)
            pos=self['ServiceStatus'].calcsize()
            self['retvalue'] = unpack('<L', data[pos:pos+4])[0]

    def pack(self):
        data = self['ServiceStatus'].pack()
        data += pack('<L', self['retvalue'])
        return data

    def get_service_type(self):
        return self['ServiceStatus'].get_type()

    def get_service_state(self):
        return self['ServiceStatus'].get_state()


# Opnum 12
class SVCCTLCreateServiceRequest(Struct):
    st = [
        ['ManagerHandle', '20s', '\x00'*20],
        ['ServiceName', '0s', ''],
        ['DisplayNamePtr', '<L', 0],
        ['DisplayName', '0s', ''],
        ['AccessMask', '<L', SVCCTL_SERVICE_ALL_ACCESS],
        ['ServiceType', '<L', SVCCTL_SERVICE_WIN32_OWN_PROCESS],
        ['ServiceStartType', '<L', SVCCTL_SERVICE_DEMAND_START],
        ['ServiceErrorControl', '<L', SVCCTL_SERVICE_ERROR_IGNORE],
        ['BinaryPathName', '0s', ''],
        ['LoadOrderGroupPtr', '<L', 0],
        ['TagId', '<L', 0],
        ['DependenciesPtr', '<L', 0],
        ['DependSize', '<L', 0],
        ['ServiceStartNamePtr', '<L', 0],
        ['PasswordPtr', '<L', 0],
        ['PasswordSize', '<L', 0],
    ]

    def __init__(self, data=None, manager_handle='\x00'*20,
                                  service_name='',
                                  binary_pathname='',
                                  display_name='',
                                  start_type=SVCCTL_SERVICE_DEMAND_START,
                                  is_unicode=True):
        Struct.__init__(self, data)

        if data is not None:
            pos = 0
            self['ManagerHandle'] = data[pos:pos+20]
            pos += 20
            self['ServiceName'] = DCERPCString(data=data[pos:])
            pos += len(self['ServiceName'].pack())
            self['DisplayNamePtr'] = data[pos:pos+4]
            self['DisplayName'] = DCERPCString(data=data[pos:])
            pos += len(self['DisplayName'].pack())
            self['AccessMask'] = data[pos:pos+4]
            pos += 4
            self['ServiceType'] = data[pos:pos+4]
            pos += 4
            self['ServiceStartType'] = data[pos:pos+4]
            pos += 4
            self['ServiceErrorControl'] = data[pos:pos+4]
            pos += 4
            self['BinaryPathName'] = DCERPCString(data=data[pos:])
            pos += len(self['BinaryPathName'].pack())
            self['LoadOrderGroupPtr'] = data[pos:pos+4]
            pos += 4
            self['TagId'] = data[pos:pos+4]
            pos += 4
            self['DependenciesPtr'] = data[pos:pos+4]
            if self['DependenciesPtr']:
                logging.eror('SVCCTL_ERROR: DependenciesPtr != 0')
                return
            pos += 4
            self['DependSize'] = data[pos:pos+4]
            pos += 4
            self['ServiceStartNamePtr'] = data[pos:pos+4]
            if self['ServiceStartNamePtr']:
                logging.eror('SVCCTL_ERROR: DependenciesPtr != 0')
                return
            pos += 4
            self['PasswordPtr'] = data[pos:pos+4]
            if self['PasswordPtr']:
                logging.eror('SVCCTL_ERROR: DependenciesPtr != 0')
                return
            pos += 4
            self['PasswordSize'] = data[pos:pos+4]
        else:
            self['ManagerHandle'] = manager_handle
            self['ServiceName'] = DCERPCString(string=service_name.encode('UTF-16LE'))
            self['BinaryPathName'] = DCERPCString(string=binary_pathname.encode('UTF-16LE'))
            if len(display_name):
                self['DisplayName'] = DCERPCString(string=display_name.encode('UTF-16LE'))
                self['DisplayNamePtr'] = 0x20004
            else:
                self['DisplayNamePtr'] = 0
            self['ServiceStartType'] = start_type

    def pack(self):
        data = pack('20s', self['ManagerHandle'])
        data += self['ServiceName'].pack()
        data += pack('<L', self['DisplayNamePtr'])
        if self['DisplayNamePtr']:
            data += self['DisplayName'].pack()
        data += pack('<L', self['AccessMask'])
        data += pack('<L', self['ServiceType'])
        data += pack('<L', self['ServiceStartType'])
        data += pack('<L', self['ServiceErrorControl'])
        data += self['BinaryPathName'].pack()
        data += pack('<L', self['LoadOrderGroupPtr'])
        data += pack('<L', self['TagId'])
        data += pack('<L', self['DependenciesPtr'])
        data += pack('<L', self['DependSize'])
        data += pack('<L', self['ServiceStartNamePtr'])
        data += pack('<L', self['PasswordPtr'])
        data += pack('<L', self['PasswordSize'])
        return data

class SVCCTLCreateServiceResponse(Struct):
    st = [
        ['TagId', '<L', 0 ],
        ['ServiceHandle', '20s', '\x00'*20],
        ['retvalue', '<L', 0 ]
    ]

    def __init__(self, data=None, TagId=0, service_handle='\x00'*20, retvalue=0, is_unicode=True):
        Struct.__init__(self, data)

        if data is not None:
            Struct.__init__(self, data)
        else:
            self['TagId'] = TagId
            self['ServiceHandle'] = service_handle
            self['retvalue'] = retvalue

    def pack(self):
        return Struct.pack(self)

    def get_return_value(self):
        return self['retvalue']

    def get_handle(self):
        return self['ServiceHandle']

# Opnum 14
class SVCCTLEnumServicesStatusRequest(Struct):
    st = [
        ['ManagerHandle', '20s', '\x00'*20],
        ['ServiceType', '<L', SVCCTL_SERVICE_WIN32|SVCCTL_SERVICE_KERNEL_DRIVER],
        ['ServiceState', '<L', SVCCTL_SERVICE_STATE_ALL],
        ['ServicesSize', '<L', 0],
        ['ResumeIndexPtr', '<L', 0]
    ]

    def __init__(self, data=None, manager_handle='',
                                  type=SVCCTL_SERVICE_WIN32,
                                  size=0,
                                  is_unicode=True):
        Struct.__init__(self, data)

        if not data:
            self['ManagerHandle'] = manager_handle
            self['ServicesSize'] = size
            self['ServiceType'] = type

    def pack(self):
        return Struct.pack(self)

def extract_unicode_str(data):
    pos = 0
    s = ''
    while 1:
        b = data[pos:pos+2]
        s += b
        if b == '\x00\x00':
            return s.decode('UTF-16LE')
        pos += 2

# Very poor parsing currently
class SVCCTLEnumServicesStatusResponse(Struct):
    st = [
        ['ServicesSize', '<L', 0],
        ['Services', '0s', ''],
        ['RequiredBytes', '<L', 0],
        ['NbrOfServices', '<L', 0],
        ['Unknown2', '<L', 0],
        ['retvalue', '<L', 0 ]
    ]

    def __init__(self, data=None, is_unicode=True):
        Struct.__init__(self, data)

        if data:
            self['Services'] = []
            # case 1: No buffer included, nothing to do.
            if not self['ServicesSize']:
                return
            # case 2: There is a buffer to extract
            else:
                howmuch = self['ServicesSize']
                buff = data[4:]
                self['retvalue'] = unpack('<L', data[-4:])[0]
                self['Unknown2'] = unpack('<L', data[-8:-4])[0]
                self['NbrOfServices'] = unpack('<L', data[-12:-8])[0]
                pos = 0
                for i in xrange(self['NbrOfServices']):
                    srv_name_off = unpack('<L', buff[pos:pos+4])[0]
                    pos+=4
                    display_name_off = unpack('<L', buff[pos:pos+4])[0]
                    pos += 4
                    service_status = SVCCTLServiceStatus(data=buff[pos:])
                    service_type = service_status.get_type()
                    service_state = service_status.get_state()
                    srv_name = extract_unicode_str(data[4+srv_name_off:])
                    display_name = extract_unicode_str(data[4+display_name_off:])
                    pos += service_status.calcsize()
                    self['Services'].append({'ServiceName':srv_name,
                                             'DisplayName':display_name,
                                             'Type':service_type,
                                             'CurrentState': service_state})
        ## else TODO

    def pack(self):
        return Struct.pack(self)

    def get_services(self):
        return self['Services']

# Opnum 15
class SVCCTLOpenSCManagerRequest(Struct):
    st = [
        ['MachineNamePtr', '<L', 0],
        ['MachineName', '0s', ''],
        ['DatabaseNamePtr', '<L', 0],
        ['DatabaseName', '0s', ''],
        ['DesiredAccess' , '<L', 0xf003f]
    ]

    def __init__(self, data=None, machine_name='', database_name='', desired_access=0, is_unicode=True):
        Struct.__init__(self, data)

        if data is not None:
            pos = 0
            self['MachineNamePtr'] = unpack('<L', data[pos:pos+4])
            pos += 4
            self['MachineName'] = DCERPCString(data=data[pos:])
            pos += len(self['MachineName'].pack())
            self['DatabaseNamePtr'] = unpack('<L', data[pos:pos+4])
            pos += 4
            self['DatabaseName'] = DCERPCString(data=data[pos:])
            pos += len(self['DatabaseName'].pack())
            self['DesiredAccess'] = unpack('<L', data[pos:pos+4])
        else:
            if len(machine_name):
                self['MachineName'] = DCERPCString(string=machine_name.encode('UTF-16LE'))
                self['MachineNamePtr'] = 0x20004
            if len(database_name):
                self['DatabaseName'] = DCERPCString(string=database_name.encode('UTF-16LE'))
                self['DatabaseNamePtr'] = 0x20008
            self['DesiredAccess'] = desired_access

    def pack(self):

        data = ''
        if self['MachineName']:
            data += pack('<L', 0x20000)
            data += self['MachineName'].pack()
        else:
            data += pack('<L', 0)
        if self['DatabaseName']:
            data += pack('<L', 0x20008)
            data += self['DatabaseName'].pack()
        else:
            data += pack('<L', 0)
        data += pack('<L', self['DesiredAccess'])
        return data

class SVCCTLOpenSCManagerResponse(Struct):
    st = [
        ['ManagerHandle', '20s', '\x00'*20],
        ['retvalue', '<L', 0 ]
    ]

    def __init__(self, data=None, manager_handle='\x00'*20, retvalue=0, is_unicode=True):
        Struct.__init__(self, data)

        if data is not None:
            Struct.__init__(self, data)
        else:
            self['ManagerHandle'] = manager_handle
            self['retvalue'] = retvalue

    def pack(self):
        return Struct.pack(self)

    def get_return_value(self):
        return self['retvalue']

    def get_handle(self):
        return self['ManagerHandle']


# Opnum 16
class SVCCTLOpenServiceRequest(Struct):
    st = [
        ['ManagerHandle', '20s', '\x00'*20],
        ['ServiceName', '0s', ''],
        ['AccessMask', '<L', SVCCTL_SERVICE_ALL_ACCESS],
    ]

    def __init__(self, data=None, manager_handle='', service_name='', is_unicode=True):
        Struct.__init__(self, data)

        if data is not None:
            pos = 0
            self['ManagerHandle'] = unpack('20s', data[pos:pos+20])
            pos += 20
            self['ServiceName'] = DCERPCString(data=data[pos:])
            pos += len(self['ServiceName'].pack())
            self['AccessMask'] = unpack('<L', data[pos:pos+4])
        else:
            self['ManagerHandle'] = manager_handle
            self['ServiceName'] = DCERPCString(string=service_name.encode('UTF-16LE'))

    def pack(self):

        data = pack('20s', self['ManagerHandle'])
        data += self['ServiceName'].pack()
        data += pack('<L', self['AccessMask'])
        return data

class SVCCTLOpenServiceResponse(Struct):
    st = [
        ['ServiceHandle', '20s', '\x00'*20],
        ['retvalue', '<L', 0 ]
    ]

    def __init__(self, data=None, service_handle='\x00'*20, retvalue=0, is_unicode=True):
        Struct.__init__(self, data)

        if data is not None:
            Struct.__init__(self, data)
        else:
            self['ServiceHandle'] = service_handle
            self['retvalue'] = retvalue

    def pack(self):
        return Struct.pack(self)

    def get_return_value(self):
        return self['retvalue']

    def get_handle(self):
        return self['ServiceHandle']

# Opnum 31
class SVCCTLStartServiceRequest(Struct):
    st = [
        ['ServiceHandle', '20s', '\x00'*20],
        ['argc', '<L', 0],
        ['UnknownFlags', '<L', 0x20000],
        ['argv', '0s', '']
    ]

    def __init__(self, data=None, service_handle='', args=[], is_unicode=True):
        Struct.__init__(self, data)

        if not data:
            self['ServiceHandle'] = service_handle
            self['argc'] = len(args)
            self['argv'] = [ DCERPCString(string=arg.encode('ASCII'), is_unicode=False) for arg in args ]
        else:
            pos = 28
            self['argc'] = len(args)
            self['argv'] = []
            for i in xrange(self['argc']):
                arg = DCERPCString(data=data[pos:])
                self['argv'].append(arg)
                pos += len(arg.pack())

    def pack(self):
        data = Struct.pack(self)
        if not len(self['argv']):
            data += pack('<L',0)
        else:
            data += pack('<L',len(self['argv']))
            for i in xrange(len(self['argv'])):
                data += pack('<L', 0x20000 + 4*(i+1))
            for arg in self['argv']:
                data += arg.pack(without_padding=0)
        return data

# Opnum 42
class SVCCTLEnumServicesStatusExRequest(Struct):
    st = [
        ['ManagerHandle', '20s', '\x00'*20],
        ['InfoLevel', '<L', SVCCTL_ENUM_PROCESS_INFO],
        ['ServiceType', '<L', SVCCTL_SERVICE_WIN32|SVCCTL_SERVICE_KERNEL_DRIVER],
        ['ServiceState', '<L', SVCCTL_SERVICE_STATE_ALL],
        ['ServicesPtr', '<L', 0],
        ['ServicesSize', '<L', 0],
        ['ResumeIndexPtr', '<L', 0],
        ['GroupNamePtr', '<L', 0]
    ]

    def __init__(self, data=None, manager_handle='\x00'*20, size=0, is_unicode=True):
        Struct.__init__(self, data)

        if not data:
            self['ManagerHandle'] = manager_handle
            self['ServicesSize'] = size

    def pack(self):
        return Struct.pack(self)

#######################################################################
#####
##### Exception classes
#####
#######################################################################

class SVCCTLException(Exception):
    """
    Base class for all SVCCTL-specific exceptions.
    """
    def __init__(self, message=''):
        self.message = message

    def __str__(self):
        return '[ SVCCTL_ERROR: %s ]' % (self.message)

class SVCCTLException2(Exception):
    """
    Improved version of the base class to track errors.
    """
    def __init__(self, message='', status=None):
        self.message = message
        self.status = status

    def __str__(self):
        if not self.status:
            return '[ SVCCTL_ERROR: %s ]' % (self.message)
        else:
            return '[ SVCCTL_ERROR: %s (0x%x) ]' % (self.message, self.status)

class SVCCTLOpenException(SVCCTLException2):
    """
    Raised when open fails.
    """
    pass

class SVCCTLCloseException(SVCCTLException2):
    """
    Raised when the cnx is already closed or was never open.
    """
    pass

class SVCCTLEnumServicesStatusException(SVCCTLException2):
    """
    Raised when EnumServicesStatus() fails.
    """
    pass

class SVCCTLOpenServiceException(SVCCTLException2):
    """
    Raised when opening a specific service didn't work.
    """
    pass


class SVCCTLCreateServiceException(SVCCTLException2):
    """
    Raised when a service creation request didn't work.
    """
    pass

class SVCCTLDeleteServiceException(SVCCTLException2):
    """
    Raised when the service deletion didn't work.
    """
    pass

class SVCCTLQueryStatusException(SVCCTLException2):
    """
    Raised when querying a service didn't work.
    """
    pass

class SVCCTLStartServiceException(SVCCTLException2):
    """
    Raised when starting a service didn't work.
    """
    pass

class SVCCTLStopServiceException(SVCCTLException2):
    """
    Raised when stopping a service didn't work.
    """
    pass

#######################################################################
#####
##### Main classes: SVCCTL, SVCCTLClient (SVCCTLServer will not be implemented)
#####
#######################################################################

class SVCCTL():
    def __init__(self, host, port):
        self.host              = host
        self.port              = port
        self.is_unicode        = True
        self.policy_handle     = None
        self.manager_handle    = None
        self.uuid              = (u'367abb81-9844-35f1-ad32-98f038001003', u'2.0')

class SVCCTLClient(SVCCTL):

    def __init__(self, host, port=445, dce=None):
        SVCCTL.__init__(self, host, port)
        self.username = None
        self.password = None
        self.domain = None
        self.kerberos_db = None
        self.use_krb5 = False
        self.dce = None
        if dce:
            self.dce = dce

    def set_credentials(self, username=None, password=None, domain=None, kerberos_db=None, use_krb5=False):
        if username:
            self.username = username
        if password:
            self.password = password
        if domain:
            self.domain = domain
        if kerberos_db:
            self.kerberos_db = kerberos_db
            self.use_krb5 = True
        else:
            if use_krb5:
                self.use_krb5 = use_krb5

    def __bind_krb5(self, connector):
        try:
            self.dce = DCERPC(connector,
                              getsock=None,
                              username=self.username,
                              password=self.password,
                              domain=self.domain,
                              kerberos_db=self.kerberos_db,
                              use_krb5=True)

            return self.dce.bind(self.uuid[0], self.uuid[1])
        except Exception as e:
            return 0

    def __bind_ntlm(self, connector):
        try:
            self.dce = DCERPC(connector,
                              getsock=None,
                              username=self.username,
                              password=self.password,
                              domain=self.domain)

            return self.dce.bind(self.uuid[0], self.uuid[1])
        except Exception as e:
            return 0

    def __bind(self, connector):

        if self.use_krb5:
            ret = self.__bind_krb5(connector)
            if not ret:
                return self.__bind_ntlm(connector)
        else:
            ret = self.__bind_ntlm(connector)
            if not ret:
                return self.__bind_krb5(connector)
        return 1

    def bind(self):
        """
        Perform a binding with the server.
        0 is returned on failure.
        """

        # If we already have it set up, no need to go over it again
        if self.dce:
            return 1

        connectionlist = []
        connectionlist.append(u'ncacn_np:%s[\\browser]' % self.host)
        connectionlist.append(u'ncacn_np:%s[\\pipe\\svcctl]' % self.host)

        for connector in connectionlist:
            ret = self.__bind(connector)
            if ret:
                return 1

        return 0

    def get_reply(self):
        """
        Provides the answer to a request.
        """
        return self.dce.reassembled_data

    def _close(self, handle=None, manager=0):
        """
        Destroy the manager handle.
        SVCCTLCloseException is raised on failure.
        """

        # We do not accept manager=1 without open manager lock
        if manager and not self.manager_handle:
            raise SVCCTLCloseException('close() failed because no valid manager handle could be found.')

        if not handle:
            handle = self.manager_handle
        try:
            data = SVCCTLCloseServiceHandleRequest(service_handle=handle).pack()
        except Exception as e:
            raise SVCCTLCloseException('close() failed to build the request.')

        self.dce.call(SVCCTL_COM_CLOSESERVICEHANDLE, data, response=True)
        if len(self.get_reply()) < 4:
            raise SVCCTLCloseException('close() call was not correct.')

        status = unpack('<L', self.get_reply()[-4:])[0]

        if status == 0:
            try:
                resp = SVCCTLCloseServiceHandleResponse(self.get_reply())
                if manager:
                    self.manager_handle = None
            except Exception as e:
                raise SVCCTLCloseException('close() failed: parsing error in the answer.')
        else:
            raise SVCCTLCloseException('close() failed.', status=status)


    def open_manager(self):
        """
        Gets a handle on the Manager to perform other calls.
        SVCCTLOpenException is raised on failure.
        """

        # Let's avoid unnecessary traffic
        if self.manager_handle:
            return self.manager_handle

        try:
            data = SVCCTLOpenSCManagerRequest(machine_name='WhatEverBro',
                                              database_name='ServicesActive',
                                              desired_access=0x3f).pack()
        except Exception as e:
            raise SVCCTLOpenException('open_manager() failed to build the request.')

        self.dce.call(SVCCTL_COM_OPENSCMANAGER, data, response=True)
        if len(self.get_reply()) < 4:
            raise SVCCTLOpenException('open_manager() call was not correct.')

        status = unpack('<L', self.get_reply()[-4:])[0]
        if status == 0:
            try:
                resp = SVCCTLOpenSCManagerResponse(self.get_reply())
                self.manager_handle = resp.get_handle()
                return self.manager_handle
            except Exception as e:
                raise SVCCTLOpenException('open_manager() failed: parsing error in the answer.')
        else:
            raise SVCCTLOpenException('open_manager() failed.', status=status)

    def close_manager(self, handle=None):
        return self._close(handle, manager=1)

    def get_services(self, service_type=SVCCTL_SERVICE_ALL):
        """
        Gets the list of services
        SVCCTLEnumServicesStatusException is raised on failure.
        """

        manager_handle = self.open_manager()

        try:
            data = SVCCTLEnumServicesStatusRequest(manager_handle=manager_handle, type=service_type, size=0).pack()
        except Exception as e:
            raise SVCCTLEnumServicesStatusException('get_services() failed to build the request.')


        self.dce.call(SVCCTL_COM_ENUMSERVICESSTATUS, data, response=True)

        if len(self.get_reply()) < 4:
            raise SVCCTLEnumServicesStatusException('get_services() call was not correct.')

        status = unpack('<L', self.get_reply()[-4:])[0]
        needed_bytes = 0

        # If it ever happens, it probably means nothing is running.
        # Okay that is quite unlikely but you never know
        if status == 0:
            return []

        if status != 0xea:
            raise SVCCTLEnumServicesStatusException('get_services() failed.', status=status)

        try:
            resp = SVCCTLEnumServicesStatusResponse(self.get_reply())
            needed_bytes = resp['RequiredBytes']
        except Exception as e:
            raise SVCCTLEnumServicesStatusException('get_services() failed: parsing error in the answer.')

        if needed_bytes:
            try:
                data = SVCCTLEnumServicesStatusRequest(manager_handle=self.manager_handle, type=service_type, size=needed_bytes).pack()
            except Exception as e:
                raise SVCCTLEnumServicesStatusException('get_services() failed to build the request.')

            self.dce.call(SVCCTL_COM_ENUMSERVICESSTATUS, data, response=True)
            if len(self.get_reply()) < 4:
                raise SVCCTLEnumServicesStatusException('get_services() call was not correct.')

            status = unpack('<L', self.get_reply()[-4:])[0]
            if status == 0:
                try:
                    resp = SVCCTLEnumServicesStatusResponse(self.get_reply())
                    return resp.get_services()
                except Exception as e:
                    raise SVCCTLEnumServicesStatusException('get_services() failed: parsing error in the answer.')
            else:
                raise SVCCTLEnumServicesStatusException('get_services() failed.', status=status)


    def open_service(self, service_name):
        """
        Gets a policy handle to perform other calls.
        SVCCTLOpenServiceException is raised on failure.
        """

        manager_handle = self.open_manager()

        try:
            data = SVCCTLOpenServiceRequest(manager_handle=manager_handle, service_name=service_name).pack()
        except Exception as e:
            raise SVCCTLOpenServiceException('open_service() failed to build the request.')

        # Unicode version only for now.
        self.dce.call(SVCCTL_COM_OPENSERVICE_W, data, response=True)
        if len(self.get_reply()) < 4:
            raise SVCCTLOpenServiceException('open_service() call was not correct.')

        status = unpack('<L', self.get_reply()[-4:])[0]

        if status == 0x424:
            raise SVCCTLOpenServiceException('open_service() failed: service does not exist.', status=status)

        if status != 0:
            raise SVCCTLOpenServiceException('open_service() failed.', status=status)

        # Parsing the answer
        try:
            resp = SVCCTLOpenServiceResponse(self.get_reply())
            service_handle = resp.get_handle()
            return service_handle
        except Exception as e:
            raise SVCCTLOpenServiceException('open_service() failed: Parsing error in the answer.')

    def close_service(self, handle=None):
        """
        Closes a specific service by handle
        """
        return self._close(handle, manager=0)

    def create_service(self, handle,
                             service_name='IMMUSVC',
                             binary_pathname='%SystemRoot%\\IMMUSVC.EXE',
                             display_name='',
                             start_type=SVCCTL_SERVICE_DEMAND_START):
        """
        Creates a new service.
        SVCCTLCreateServiceException is raised on failure.
        """

        if not display_name:
            display_name = service_name

        try:
            data = SVCCTLCreateServiceRequest(manager_handle=handle,
                                       service_name=service_name,
                                       binary_pathname=binary_pathname,
                                       display_name=display_name,
                                       start_type=start_type).pack()
        except Exception as e:
            raise SVCCTLCreateServiceException('create_service() failed to build the request.')

        self.dce.call(SVCCTL_COM_CREATESERVICE_W, data, response=True)
        if len(self.get_reply()) < 4:
            raise SVCCTLCreateServiceException('create_service() call was not correct.')

        status = unpack('<L', self.get_reply()[-4:])[0]

        # ERROR_SERVICE_EXISTS
        if status == 0x431:
            raise SVCCTLCreateServiceException('create_service() failed: service already exists.', status=status)

        if status != 0:
            raise SVCCTLCreateServiceException('create_service() failed.', status=status)

        try:
            resp = SVCCTLCreateServiceResponse(self.get_reply())
            service_handle = resp.get_handle()
            return service_handle
        except Exception as e:
            raise SVCCTLCreateServiceException('create_service() failed: parsing error in the answer.')

    def _delete_service_by_handle(self, service_handle):

        try:
            data = SVCCTLDeleteServiceRequest(service_handle=service_handle).pack()
        except Exception as e:
            raise SVCCTLDeleteServiceException('delete_service() failed to build the request.')

        self.dce.call(SVCCTL_COM_DELETESERVICE, data, response=True)

        if len(self.get_reply()) < 4:
            raise SVCCTLDeleteServiceException('delete_service() call was not correct.')

        status = unpack('<L', self.get_reply()[-4:])[0]

        # ERROR_SERVICE_MARKED_FOR_DELETE
        if status == 0x430:
            raise SVCCTLDeleteServiceException('delete_service() failed: service already marked for delete.', status=status)

        if status != 0:
            raise SVCCTLDeleteServiceException('delete_service() failed.', status=status)


    def delete_service(self, service_handle=None, service_name=None):
        """
        Deletes a service either using its name or its handle
        SVCCTLDeleteServiceException is raised on failure.
        """

        # Sanity check
        if not service_handle and not service_name:
            raise SVCCTLDeleteServiceException('delete_service() failed: invalid parameters.')

        # If we have a valid handle, we don't care about the service name
        if service_handle:
            return self._delete_service_by_handle(service_handle)

        # But if we don't then it means that we first have to retrieve the
        # handle

        self.open_manager()
        services = self.get_services()
        self.close_manager()

        # Is the service registered under the name?
        for service in services:
            name = service['ServiceName'][:-1]
            if name == service_name:
                handle = self.open_service(name)
                return self._delete_service_by_handle(handle)

        # Service was not found!
        raise SVCCTLDeleteServiceException('delete_service() failed: Invalid service name.')

    def query_service(self, service_handle):
        """
        Gets the status corresponding to a specific service
        SVCCTLQueryServiceStatusException is raised on failure.
        """

        if not service_handle:
            raise SVCCTLQueryServiceStatusException('query_service() failed: Invalid parameter.')

        try:
            data = SVCCTLQueryServiceStatusRequest(service_handle=service_handle).pack()
        except Exception as e:
            raise SVCCTLQueryServiceStatusException('query_service() failed to build the request.')



        self.dce.call(SVCCTL_COM_QUERYSERVICESTATUS, data, response=True)

        if len(self.get_reply()) < 4:
            raise SVCCTLQueryServiceStatusException('query_service() call was not correct.')

        status = unpack('<L', self.get_reply()[-4:])[0]

        if status != 0:
            raise SVCCTLQueryServiceStatusException('query_service() failed.', status=status)

        try:
            resp = SVCCTLQueryServiceStatusResponse(self.get_reply())
            service_type = resp.get_service_type()
            service_state = resp.get_service_state()
            return {'Type':service_type, 'CurrentState':service_state}
        except Exception as e:
            raise SVCCTLQueryServiceStatusException('query_service() failed: parsing error in the answer.')

    def start_service(self, service_handle, args=[]):
        """
        Starts a service
        SVCCTLStartServiceException is raised on failure.
        """

        if not service_handle:
            raise SVCCTLStartServiceException('start_service() failed: invalid parameter.')

        try:
            data = SVCCTLStartServiceRequest(service_handle=service_handle, args=args).pack()
        except Exception as e:
            raise SVCCTLStartServiceException('start_service() failed to build the request.')


        # There are 2 possible methods. For now, we only handle the one without Unicode as
        # it is much easier.
        self.dce.call(SVCCTL_COM_STARTSERVICE_A, data, response=True)
        if len(self.get_reply()) < 4:
            raise SVCCTLStartServiceException('start_service() call was not correct.')

        status = unpack('<L', self.get_reply()[-4:])[0]

        # ERROR_SERVICE_DISABLED
        if status == 0x422:
            raise SVCCTLStartServiceException('start_service() failed: service is disabled.', status=status)

        # ERROR_SERVICE_ALREADY_RUNNING
        if status == 0x420:
            raise SVCCTLStartServiceException('start_service() failed: service is already running.', status=status)

        # ERROR_INVALID_PARAMETER
        if status == 0x57:
            raise SVCCTLStartServiceException('start_service() failed: invalid parameter.', status=status)

        if status != 0:
            raise SVCCTLStartServiceException('start_service() failed.', status=status)


    def stop_service(self, service_handle):
        """
        Stop a service
        SVCCTLStopServiceException is raised on failure.
        """

        if not service_handle:
            raise SVCCTLStopServiceException('stop_service(): invalid parameter.')

        try:
            data = SVCCTLControlServiceRequest(service_handle=service_handle, control=SVCCTL_SERVICE_CONTROL_STOP).pack()
        except Exception as e:
            raise SVCCTLStopServiceException('stop_service() failed to build the request.')

        self.dce.call(SVCCTL_COM_CONTROLSERVICE, data, response=True)
        if len(self.get_reply()) < 4:
            raise SVCCTLStopServiceException('stop_service() call was not correct.')

        status = unpack('<L', self.get_reply()[-4:])[0]

        # ERROR_DEPENDENT_SERVICES_RUNNING
        if status == 0x41b:
            raise SVCCTLStopServiceException('stop_service() failed: cannot stop this service while others are running.', status=status)

        # ERROR_SERVICE_NOT_ACTIVE
        if status == 0x426:
            raise SVCCTLStopServiceException('stop_service() failed: this service is not active.', status=status)

        if status != 0:
            raise SVCCTLStopServiceException('stop_service() failed.', status=status)

#######################################################################
#####
##### A couple of useful functions for other parts of CANVAS
#####
#######################################################################

def SVCCTL_ServiceType2Str(service_type):
    a = {
        SVCCTL_SERVICE_DRIVER: '(Generic) driver',
        SVCCTL_SERVICE_FILE_SYSTEM_DRIVER: 'FS driver',
        SVCCTL_SERVICE_KERNEL_DRIVER: 'Kernel driver',
        SVCCTL_SERVICE_WIN32: 'Service',
        SVCCTL_SERVICE_WIN32_OWN_PROCESS: 'Own process',
        SVCCTL_SERVICE_WIN32_SHARE_PROCESS: 'Shared process'
    }

    if not a.has_key(service_type):
        return 'Unknown type'
    else:
        return a[service_type]

def SVCCTL_ServiceState2Str(service_state):
    a = {
        SVCCTL_SERVICE_CONTINUE_PENDING: 'Continue pending',
        SVCCTL_SERVICE_PAUSE_PENDING: 'Pause pending',
        SVCCTL_SERVICE_PAUSED: 'Paused',
        SVCCTL_SERVICE_RUNNING: 'Running',
        SVCCTL_SERVICE_START_PENDING: 'Start pending',
        SVCCTL_SERVICE_STOP_PENDING: 'Stop pending',
        SVCCTL_SERVICE_STOPPED: 'Stopped',
    }

    if not a.has_key(service_state):
        return 'Unknown type'
    else:
        return a[service_state]

# This function returns 0 in case of error or 1 if the service is installed
def SVCCTL_IsServiceInstalled(target, username, pwd, domain, service_name, use_krb5=False, kerberos_db=None):
    try:
        svc = SVCCTLClient(target)
        svc.set_credentials(username,
                            pwd,
                            domain,
                            use_krb5=use_krb5,
                            kerberos_db=kerberos_db)
        if not svc.bind():
            return 0
        hsc = svc.open_manager()
        handle = svc.open_service(service_name)
        svc.close_service(handle)
        svc.close_manager(hsc)
        return 1
    except Exception as e:
        return 0

# This function returns 0 in case of error or 1 if the service is really
# in running state
def SVCCTL_IsServiceRunning(target, username, pwd, domain, service_name, use_krb5=False, kerberos_db=None):
    try:
        svc = SVCCTLClient(target)
        svc.set_credentials(username,
                            pwd,
                            domain,
                            use_krb5=use_krb5,
                            kerberos_db=kerberos_db)
        if not svc.bind():
            return 0
        svc.open_manager()
        handle = svc.open_service(service_name)
        res = svc.query_service(handle)
        svc.close_service(handle)
        svc.close_manager()
        if res['CurrentState'] == SVCCTL_SERVICE_RUNNING:
            return 1
        else:
            return 0
    except Exception as e:
        return 0

#######################################################################
#####
##### Well, the main :D
#####
#######################################################################

def main():

    if len(sys.argv) > 1 and sys.argv[1] == '-v':
        logger = logging.getLogger()
        logger.setLevel(logging.DEBUG)

    svc = SVCCTLClient('10.0.0.1')
    svc.set_credentials('administrator', 'foobar123!', 'immu5.lab')
    if not svc.bind():
        print "[-] bind() failed."
        sys.exit(0)
    sys.exit(1)

if __name__ == "__main__":
    main()

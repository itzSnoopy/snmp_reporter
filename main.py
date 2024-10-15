import daemon
import time
import logging
import argparse
import os
import sys
import asyncio

from daemon import pidfile
from pysnmp.hlapi.v3arch.asyncio import *

def start_daemon(pidFile, logFile):
    '''
    try:

        with daemon.DaemonContext(working_directory='/app/daemon', umask=0o002, pidfile=pidfile.TimeoutPIDLockFile(filePid)) as context:
            run_monitor(fileLog)
    except Exception as err:
        print(f"Unexpected {err=}, {type(err)=}")
    '''
    run_monitor(logFile)



async def run_monitor(logFile):
    logger = logging.getLogger('monitor')
    logger.setLevel(logging.DEBUG)
    

    fileHandler = logging.FileHandler(logFile)
    
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    fileHandler.setLevel(logging.DEBUG)
    fileHandler.setFormatter(formatter)

    consoleHandler = logging.StreamHandler(sys.stdout)
    consoleHandler.setFormatter(formatter)

    logger.addHandler(fileHandler)
    logger.addHandler(consoleHandler)

    while True:
        deviceAddress = os.environ['ENV_DEVICE_ADDRESS']
        devicePort = os.environ['ENV_DEVICE_PORT']
        snmpEngine = SnmpEngine()

        iterator = get_cmd(
            snmpEngine,
            CommunityData("public", mpModel=0),
            await UdpTransportTarget.create((deviceAddress, 161)),
            ContextData(),
            ObjectType(ObjectIdentity("SNMPv2-MIB", "sysDescr", 0))
        )

        errorIndication, errorStatus, errorIndex, varBinds = await iterator

        if errorIndication:
            logger.error(errorIndication)
        
        elif errorStatus:
            logger.error("{} at {}".format(
                errorStatus.prettyPrint(),
                errorIndex and varBinds[int(errorIndex) - 1][0] or "?"
            ))
        
        else:
            for varBind in varBinds:
                logger.info("=".join([x.prettyPrint() for x in varBind]))

        snmpEngine.close_dispatcher()

        time.sleep(int(os.environ['ENV_RUN_INTERVAL']))

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="SNMP Monitor in Python")
    parser.add_argument('-a', '--address', help='IP Address of Device to Monitor')
    parser.add_argument('-c', '--config', help='Location of the configuration file', default='/opt/data')

    args = parser.parse_args()

    pidFile = '/opt/data/daemon.pid'
    logFile = '/opt/data/daemon.log'

    ''' start_daemon(pidFile, logFile) '''
    asyncio.run(run_monitor(logFile))
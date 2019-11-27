#
#  Copyright (c) 2011 * - 2019 Draegerwerk AG & Co. KGaA. All rights reserved.
#  This program and the accompanying materials are made available under the terms
#  of the Eclipse Public License v2.0 which is available at http://www.eclipse.org/legal/epl-v20.html
#

import threading
from PCD04Message import PCD04Message
from readchar import readkey
import socket
import uuid

stopEvent = threading.Event()
sendHeartbeat = True
deviceId = "uuid:df041f5c-a3c9-11e9-8d8a-0050b612afeb"
deviceLocation = "POC^Room^Bed^fac^^^building^floor"

outSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
outAddress = "127.0.0.1"
outPort = 9999


def sendAlert():
    print ("**** Sending Example Alert ****")
    msg = PCD04Message()
    msg.createPCD04Message(AssignedPatientLocation=deviceLocation,
                            EquipII="{}^^{}^URN".format(deviceId, deviceId),
                            PatientIdList="HO2009001^^^Hospital^PI",
                            PatientName="Hon^Albert^^^^^L",
                            PatientDoB="18991230",
                            PatientSex="M",
                            UniqueAlertUuid=deviceId,
                            AlertType="196670^MDC_EVT_LO^MDC",
                            AlertText="Low Alert",
                            SrcContainmentTreeId="1.1.1",
                            AlertPhase="start",
                            AlertKindPrioStr="PM",
                            AlertKind="SP",
                            AlertCounter=0,
                            ObsType="150456^MDC_PULS_OXIM_SAT_O2^MDC",
                            ObsValueType="NM",
                            ObsValue="42",
                            ObsUnit=None,
                            MdsType="69837^MDC_DEV_METER_PHYSIO_MULTI_PARAM_MDS^MDC",
                            VmdType="69686^MDC_DEV_ANALY_BLD_CHEM_MULTI_PARAM_VMD^MDC"
                            )
    outSocket.sendall(msg.getMessage().to_mllp().encode('UTF-8'))


def createHeartbeatMsg():
    msg = PCD04Message()
    msg.createPCD04Message(AssignedPatientLocation=deviceLocation,
                            EquipII="{}^^{}^URN".format(deviceId, deviceId),
                            PatientIdList="HO2009001^^^Hospital^PI",
                            PatientName="Hon^Albert^^^^^L",
                            PatientDoB="18991230",
                            PatientSex="M",
                            UniqueAlertUuid=deviceId,
                            AlertType=PCD04Message.HeartbeatAlarmType,
                            AlertText="",
                            SrcContainmentTreeId="1.1.1",  # this refers to the first MDS
                            AlertPhase="start",
                            AlertKindPrioStr="PN",  # not indicated, heartbeat only
                            AlertKind="SA",
                            AlertCounter=0,
                            ObsType="68480^MDC_ATTR_ALERT_SOURCE^MDC",
                            ObsValueType="ST",
                            ObsValue="",
                            ObsUnit=None
                            )
    msg.addWatchdogObxSegment(5, "1.0.0")
    return msg


def mainLoop():
    print ("Opening socket to {}:{}".format(outAddress, outPort))
    outSocket.connect ((outAddress, outPort))
    print ("Socket open, sending alive every 5 sec")
    msg = createHeartbeatMsg()
    while True:
        if sendHeartbeat:
            msgId = str(uuid.uuid4())
            msg.setControlId(msgId)
            print ("Sending msg with ID {}".format(msgId))
            outSocket.sendall(msg.getMessage().to_mllp().encode('UTF-8'))
        if stopEvent.wait(5):
            break


def receiveLoop():
    while not stopEvent.wait(5):
        if outSocket:
            received = outSocket.recv (1024 * 1024)
            print ("Received message: \n{}\n".format(received[1:-2].decode('UTF-8')))
        else:
            print ("Socket not open, next time...")


if __name__ == '__main__':
    thread1 = threading.Thread(target=mainLoop, args=())
    thread1.start()
    thread2 = threading.Thread (target=receiveLoop, args=())
    thread2.start()
    try:
        print ("Mock IHE-PCD-ACM AR")
        print ("Press a to send alert ")
        print ("Press t to toggle hearbeat sending")
        print ("Press q to quit")
        keepGoing = True
        while keepGoing:
            key = readkey()
            print ("Got " + key)
            if (key == 'q'):
                keepGoing = False
                stopEvent.set()
                thread1
            elif (key == 'a'):
                sendAlert()
            elif (key == 't'):
                print ("Toggling heartbeat from " + str(sendHeartbeat))
                sendHeartbeat = not sendHeartbeat
            else:
                print ("Unknown key: " + key)
        print ("Good bye...")
    except KeyboardInterrupt:
        print ("Interrupted...")
        stopEvent.set()

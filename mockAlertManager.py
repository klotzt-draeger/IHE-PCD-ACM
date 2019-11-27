#
#  Copyright (c) 2011 * - 2019 Draegerwerk AG & Co. KGaA. All rights reserved.
#  This program and the accompanying materials are made available under the terms
#  of the Eclipse Public License v2.0 which is available at http://www.eclipse.org/legal/epl-v20.html
#

import socket
from hl7apy.parser import parse_message
from hl7apy.exceptions import HL7apyException
from datetime import datetime
from hl7apy.core import Message
import traceback
import time

def _getObxSegment (msg, id):
    # iterate over obx segments
    obx = msg.children.get("OBX")
    retVal = None
    for oneObx in obx:
        if oneObx.children.get("OBX_4").value.split(".")[3] == str(id):
            retVal = oneObx
        # for obxChild in oneObx.children:
            # print ("OBX Child: {}".format(obxChild.value))
        # print("------")
    return retVal

def pretty (msg):
    retVal=""
    for oneLine in msg.to_er7().splitlines():
        retVal=retVal+oneLine+"\n"
    return retVal

def receiveOneMsg (sock):
    startMark=b"\x0b"
    endMark = b"\x1c" + b"\x0d"

    # receive char by char, check for start and end char

    while sock.recv(1)!=startMark:
        time.sleep(1)

    buff=sock.recv(2)
    # read rest of message until 2 end chars are found
    while buff[-2:]!=endMark:
        buff+=sock.recv(1)
    return buff[:-2].decode()

if __name__ == '__main__':
    listenerSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    listenerSocket.bind(('', 9999))
    print ("listening on socket")
    listenerSocket.listen(1)
    inSock, addr = listenerSocket.accept()
    #inSock.settimeout(5.0)
    print ("Got inbound connection from {}".format(addr))
    while True:
        oneMsg = receiveOneMsg (inSock)
        try:
            m = parse_message(oneMsg)
            try:
                msgType = m.children.get("MSH").children.get("MSH_9").value
                if msgType == "ACK^R41":
                    print ("Got ACK {}".format(pretty(m)))
                elif msgType == "ORU^R40^ORU_R40":
                    seg1 = _getObxSegment(m, 1)
                    alarmTypeTxt = seg1.children.get("OBX_3").value
                    answer = Message(version="2.7")
                    if alarmTypeTxt == "196614^MDC_EVT_ACTIVE^MDC":
                        # answer with ack
                        print ("************ Got Heartbeat ************")
                        print ("Full message {}: \n{}".format(datetime.now(), pretty(m)))
                        answer.msh.children.get("MSH_9").value = "ACK^R40"
                        answer.msa.children.get("MSA_1").value = "CA"
                        corId=m.msh.children.get("MSH_10").value
                        answer.msa.children.get("MSA_2").value = corId
                    else:
                        # answer with pcd-05 message
                        print ("************ Got Alarm {} ************".format(alarmTypeTxt))
                        print ("Full message {}: \n{}".format(datetime.now(), pretty(m)))
                        counter = m.children.get("OBR").children.get("OBR_3").children[0].value
                        alarmId = m.children.get("OBR").children.get("OBR_3").children[1].value
                        answer.msh.children.get("MSH_9").value = "ORA^R41^ORA_R41"
                        answer.msh.children.get("MSH_4").value = "MockAM"
                        answer.add_segment("OBR").children.get("OBR_3").value = "{}^{}".format(counter, alarmId)
                        answer.add_segment("PRT").children.get("PRT_3").value = "Delivered"
                        answer.msh.children.get("MSH_10").value = m.msh.children.get("MSH_10").value
                    print ("Answering {}: \n{}".format(datetime.now(), pretty(answer)))
                    inSock.sendall(answer.to_mllp().encode('UTF-8'))
                    print ("*******************************")
                else:
                    print ("Got unknown message type: {}".format(msgType))
            except:
                traceback.print_exc()
        except HL7apyException as e:
            traceback.print_exc()
    print ("This is the end...")

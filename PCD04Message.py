#
#  Copyright (c) 2011 * - 2019 Draegerwerk AG & Co. KGaA. All rights reserved.
#  This program and the accompanying materials are made available under the terms
#  of the Eclipse Public License v2.0 which is available at http://www.eclipse.org/legal/epl-v20.html
#

from hl7apy.core import Message
from hl7apy.core import Segment
from datetime import datetime
from hl7apy.parser import parse_message


ActorEui64 = "0000000000000001^EUI-64"
ActorEui64Sub = "0000000000000001&EUI-64"
AcceptAckTypeAcm = "AL"  # In [PCD-01], [PCD-04], and [PCD-05] transactions, this field shall be valued as AL.
ApplicationAckType = "NE"  # The PCD TF requires that this field be valued as NE for [PCD-01], [PCD-04], and [PCD-05] transactions.


class PCD04Message:
    HeartbeatAlarmType = "258047^MDC_EVT_ACTIVE^MDC"

    def getMessage(self):
        return self._ORU_R40

    def __init__(self):
        self._myMsgControlIdIter=0
        self._ORU_R40 = Message(version="2.6")

    def createPCD04Message(self,
                        AssignedPatientLocation,
                        EquipII,
                        PatientIdList,
                        PatientName,
                        PatientDoB,
                        PatientSex,
                        AlertType,
                        AlertText,
                        AlertPhase,
                        AlertKindPrioStr,
                        SrcContainmentTreeId,
                        ObsType,
                        ObsValue,
                        ObsValueType,
                        ObsUnit,
                        UniqueAlertUuid,
                        AlertKind,
                        ObsDetTime=None,
                        AlertCounter=0,
                        AlertState="active",
                        AlertInactivationState="enabled",
                        SendingFacility="IHE_AR",
                        ReceivingApplication = None,
                        ProcessingId="D"):
        messageTime = datetime.now().astimezone()
        messageTimeStr = messageTime.strftime("%Y%m%d%H%M%S%z")

        self.createMshSegmentAcm(messageTimeStr, SendingFacility, ReceivingApplication, ProcessingId)
        self.createPidSegmentAcm(PatientIdList, PatientName, PatientDoB, PatientSex)
        self.createPv1SegmentAcm(AssignedPatientLocation)
        self._CTP = SrcContainmentTreeId
        self._EquipII = EquipII
        self.createObrSegmentAcm(messageTimeStr, UniqueAlertUuid, AlertCounter)

        self.createObxSegmentAcm(1, AlertType, AlertText)
        self.createObxSegmentAcm(2, ObsType, ObsValue, ObsValueType=ObsValueType, ObsUnit=ObsUnit, ObsTimeStr=ObsDetTime)
        self.createObxSegmentAcm(3, "68165^MDC_ATTR_EVENT_PHASE^MDC", AlertPhase)
        self.createObxSegmentAcm(4, "68166^MDC_ATTR_ALARM_STATE^MDC", AlertState)
        self.createObxSegmentAcm(5, "68167^MDC_ATTR_ALARM_INACTIVATION_STATE^MDC", AlertInactivationState)
        self.createObxSegmentAcm(6, "68168^MDC_ATTR_ALARM_PRIORITY^MDC", AlertKindPrioStr)
        self.createObxSegmentAcm(7, "68485^MDC_ATTR_ALERT_TYPE^MDC", AlertKind)

    def addWatchdogObxSegment (self, timeoutPeriod, timeoutUnit="264320^MDC_DIM_SEC^MDC"):
        self.createObxSegmentAcm (8, "67860^MDC_ATTR_CONFIRM_TIMEOUT^MDC", ObsValue=timeoutPeriod, ObsUnit=timeoutUnit, ObsValueType="NM")

    def createMshSegmentAcm(self, messageTimeStr, SendingFacility, ReceivingApplication, ProcessingId):
        MsgControlIdVal = str(self._myMsgControlIdIter)
        self._myMsgControlIdIter += 1

        self._ORU_R40.msh.children.get("MSH_3").value = ActorEui64  # Sending Application
        self._ORU_R40.msh.children.get("MSH_4").value = SendingFacility  # Sending Facility
        if (ReceivingApplication is not None):
            self._ORU_R40.msh.children.get("MSH_5").value = ReceivingApplication  # Receiving Application
        self._ORU_R40.msh.children.get("MSH_7").value = messageTimeStr  # Date/Time Of Message
        self._ORU_R40.msh.children.get("MSH_9").value = "ORU^R40^ORU_R40"  # Message Type
        self._ORU_R40.msh.children.get("MSH_10").value = MsgControlIdVal  # Message Control ID
        self._ORU_R40.msh.children.get("MSH_11").value = ProcessingId  # Processing ID
        self._ORU_R40.msh.children.get("MSH_15").value = AcceptAckTypeAcm  # Accept Acknowledgment Type
        self._ORU_R40.msh.children.get("MSH_16").value = ApplicationAckType  # Application Acknowledgment Type
        self._ORU_R40.msh.children.get("MSH_20").value = "IHE_PCD_ACM_001^IHE PCD^1.3.6.1.4.1.19376.1.6.4.4^ISO"  # IHE_PCD_ACM_001^IHE PCD^1.3.6.1.4.1.19376.1.6.4.4^ISO

    def createPidSegmentAcm(self, PatientIdList, PatientName, PatientDoB, PatientSex) :
        pid = self._ORU_R40.add_segment("PID")
        pid.children.get("PID_3").value = PatientIdList  # Patient Identifier List
        pid.children.get("PID_5").value = PatientName  # Patient Name
        pid.children.get("PID_7").value = PatientDoB
        pid.children.get("PID_8").value = PatientSex

    def createPv1SegmentAcm(self, AssignedPatientLocation):
        # PV1|||CU1^^9042^HOSP1
        pv1 = self._ORU_R40.add_segment("PV1")
        pv1.children.get("PV1_3").value = AssignedPatientLocation  # Assigned Patient Location

    def incAlertCounter (self):
        obr = self._ORU_R40.children.get("OBR")
        oldCountStr = obr.children.get("OBR_3").value.split ('^')
        oldCount = int(oldCountStr[0])
        FillerOrderNumber = str(oldCount + 1) + "^" + oldCountStr[1] + "^" + oldCountStr[2]
        obr.children.get("OBR_3").value = FillerOrderNumber  # Filler Order Number
        self._ORU_R40.children.get("OBX")[2].children.get("OBX_5").value = "continue"

    def setControlId(self, id):
        self._ORU_R40.msh.children.get("MSH_10").value=id

    def setAlarmTypeAndText (self, alarmType, alarmText):
        seg1 = self._getObxSegment(1)
        seg1.children.get("OBX_3").value = alarmType
        seg1.children.get("OBX_5").value = alarmText

    def setAlarmValue (self, value, obsType, unit, time):
        seg2 = self._getObxSegment(2)
        seg2.children.get("OBX_6").value = unit
        seg2.children.get("OBX_2").value = obsType
        seg2.children.get("OBX_5").value = str(value)
        seg2.children.get("OBX_14").value = time

    def setAlarmCTP (self, CTP):
        self._CTP = CTP

    def setAlarmId (self, alarmId):
        obr = self._ORU_R40.children.get("OBR")
        obr.children.get("OBR_1").value = "1"
        old = obr.children.get("OBR_3").value.split('^')  # Set ID - OBR
        FillerOrderNumber = str(old[0]) + "^" + alarmId + "^" + old[2]
        parentAlert = "^0&" + alarmId + "&" + old[2]
        obr.children.get("OBR_3").value = FillerOrderNumber  # Filler Order Number

    def setAlarmPhase (self, AlertPhase):
        seg = self._getObxSegment(3)
        seg.children.get("OBX_5").value=AlertPhase

    def setAlarmState (self, AlertState):
        seg = self._getObxSegment(4)
        seg.children.get("OBX_5").value=AlertState

    def setAlarmInactivationState (self, AlertState):
        seg = self._getObxSegment(5)
        seg.children.get("OBX_5").value=AlertState

    def setAlarmPrio (self, AlertPrio):
        seg = self._getObxSegment(6)
        seg.children.get("OBX_5").value=AlertPrio

    def setAlarmKind (self, AlertKind):
        seg = self._getObxSegment(7)
        seg.children.get("OBX_5").value=AlertKind

    def getDeviceId(self):
        return self._ORU_R40.children.get("OBX").children.get("OBX_18").value

    def getLocation(self):
        pv1 = self._ORU_R40.children.get("PV1")
        return pv1.children.get("PV1_3").value

    def getEquip(self):
        seg=self._ORU_R40.children.get("OBX")
        return seg.children.get("OBX_18").value

    def getPatientId(self):
        pid = self._ORU_R40.children.get("PID")
        return pid.children.get("PID_3").value

    def getPatientName(self):
        pid = self._ORU_R40.children.get("PID")
        return pid.children.get("PID_5").value

    def getPatientDoB(self):
        pid = self._ORU_R40.children.get("PID")
        return pid.children.get("PID_7").value

    def getPatientSex(self):
        pid = self._ORU_R40.children.get("PID")
        return pid.children.get("PID_8").value

    def _getObxSegment (self, nr):
        # iterate over obx segments
        obx = self._ORU_R40.children.get("OBX")
        retVal = None
        for oneObx in obx:
            if oneObx.children.get("OBX_1").value == str(nr):
                retVal = oneObx
        return retVal

    def createObrSegmentAcm(self, messageTimeStr, UniqueAlertUuid, AlertUpdate):
        obr = self._ORU_R40.add_segment("OBR")
        obr.children.get("OBR_1").value = "1"  # Set ID - OBR
        FillerOrderNumber = str(AlertUpdate) + "^" + UniqueAlertUuid + "^" + ActorEui64
        parentAlert = "^0&" + UniqueAlertUuid + "&" + ActorEui64Sub
        obr.children.get("OBR_3").value = FillerOrderNumber  # Filler Order Number
        obr.children.get("OBR_4").value = "196616^MDC_EVT_ALARM^MDC"  # Universal Service Identifier
        obr.children.get("OBR_7").value = messageTimeStr  # Observation Date/Time
        if (AlertUpdate > 0):
            obr.children.get("OBR_29").value = parentAlert  # Parent

    def createObxSegmentAcm(self, Set_ID, ObsId, ObsValue, ObsUnit=None, ObsTimeStr=None, ObsSite=None, ObsValueType="ST"):
        obx = self._ORU_R40.add_segment("OBX")
        obx.children.get("OBX_1").value = str(Set_ID)  # Set ID
        obx.children.get("OBX_2").value = ObsValueType

        obx.children.get("OBX_3").value = ObsId  # Observation Identifier
        obx.children.get("OBX_4").value = self._CTP + "." + str(Set_ID)  # Observation Sub-ID
        obx.children.get("OBX_5").value = str(ObsValue)  # Observation Value
        if ObsUnit is not None:
            obx.children.get("OBX_6").value = ObsUnit  # Units

        obx.children.get("OBX_11").value = "F"  # Observation Result Status

        if (ObsTimeStr is not None):
            obx.children.get("OBX_14").value = ObsTimeStr  # Date/Time of the Observation

        obx.children.get("OBX_18").value = self._EquipII  # Equipment Instance Identifier

        if (ObsSite is not None):
            obx.children.get("OBX_20").value = ObsSite  # Observation Site

import time

from gui import softkeys
from sccptest.sccptest import *

from sccp.sccpmessagetype import SCCPMessageType
from sccp.sccpcallstate import SCCPCallState
from sccp.sccpstarttone import SCCPStartTone


@client(device='SEP000000000000', serverAddress=('127.0.0.1', 2000), bindAddress=('127.0.0.2', 0))
@client(device='SEP000000000001', serverAddress=('127.0.0.1', 2000), bindAddress=('127.0.0.3', 0))
def testCallOperator(client, operator):
    OPERATOR_NUMBER = '1102'
    expectSoftkey(client, softkeys.SKINNY_LBL_NEWCALL)
    pushSoftKey(client, softkeys.SKINNY_LBL_NEWCALL)
    call = getCallInfo(expectCallState(client, SCCPCallState.SCCP_CHANNELSTATE_OFFHOOK))
    expectTone(client, SCCPStartTone.SCCP_TONE_INSIDE, call=call)
    dial(client, OPERATOR_NUMBER)
    expectTone(client, SCCPStartTone.SCCP_TONE_INSIDE, call=call)
    expectTone(client, SCCPStartTone.SCCP_TONE_ALERTING, call=call)
    expectSoftkey(operator, softkeys.SKINNY_LBL_ANSWER)
    pushSoftKey(operator, softkeys.SKINNY_LBL_ANSWER)
    time.sleep(1)

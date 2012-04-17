from gui import softkeys
from sccptest.sccptest import *
from sccp.sccpmessagetype import SCCPMessageType
from sccp.sccpcallstate import SCCPCallState
from sccp.sccpstarttone import SCCPStartTone
import time

@client(device='SEP000000000000', serverAddress=('127.0.0.1', 2000), bindAddress=('127.0.0.2', 0))
def testClient(client):
    NUMBER = '1002'
    expectSoftkey(client, softkeys.SKINNY_LBL_NEWCALL)
    pushSoftKey(client, softkeys.SKINNY_LBL_NEWCALL, NO_CALL)
    call = getCallInfo(expectCallState(client, SCCPCallState.SCCP_CHANNELSTATE_OFFHOOK))
    expectTone(client, SCCPStartTone.SCCP_TONE_INSIDE, call=call)
    dial(client, NUMBER)
    expectTone(client, SCCPStartTone.SCCP_TONE_INSIDE, call=call)
    expectTone(client, SCCPStartTone.SCCP_TONE_ALERTING, call=call)
    time.sleep(1)

@client(device='SEP000000000001', serverAddress=('127.0.0.1', 2000), bindAddress=('127.0.0.3', 0))
def testClient2(client):
    time.sleep(2)
    expectSoftkey(client, softkeys.SKINNY_LBL_ANSWER)
    pushSoftKey(client, softkeys.SKINNY_LBL_ANSWER, NO_CALL)
    expectSoftkey(client, softkeys.SKINNY_LBL_ENDCALL)
    pushSoftKey(client, softkeys.SKINNY_LBL_ENDCALL, NO_CALL)

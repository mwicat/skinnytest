from gui import softkeys
from sccptest import *
from sccp.sccpmessagetype import SCCPMessageType
from sccp.sccpcallstate import SCCPCallState
from sccp.sccpstarttone import SCCPStartTone
import time

@client(device='SEP001120AABBCC', serverAddress=['127.0.0.1', 2000])
@client(device='SEP001120AABBAA', serverAddress=['127.0.0.1', 2000])
def testClient(client, client2):
    NUMBER_TO_CALL = '1102'
    expectSoftkey(client, softkeys.SKINNY_LBL_NEWCALL)
    pushSoftKey(client, softkeys.SKINNY_LBL_NEWCALL)
    call = getCallInfo(expectCallState(client, SCCPCallState.SCCP_CHANNELSTATE_OFFHOOK))
    expectTone(client, SCCPStartTone.SCCP_TONE_INSIDE, call=call)
    dial(client, NUMBER_TO_CALL)
    expectTone(client, SCCPStartTone.SCCP_TONE_INSIDE, call=call)
    expectTone(client, SCCPStartTone.SCCP_TONE_ALERTING, call=call)
    expectSoftkey(client2, softkeys.SKINNY_LBL_ANSWER)
    pushSoftKey(client2, softkeys.SKINNY_LBL_ANSWER)
    time.sleep(1)


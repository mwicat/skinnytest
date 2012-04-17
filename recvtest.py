from gui import softkeys
from sccptest import *
from sccp.sccpmessagetype import SCCPMessageType
from sccp.sccpcallstate import SCCPCallState
from sccp.sccpstarttone import SCCPStartTone
import time

@client(device='SEP001120AABBAA', serverAddress=['127.0.0.1', 2000])
def testClient2(client):
    call = getCallInfo(expectCallState(client, SCCPCallState.SCCP_CHANNELSTATE_RINGING))
    try:
        call2 = getCallInfo(expectCallState(client, SCCPCallState.SCCP_CHANNELSTATE_RINGING))
        expectSoftkey(client, softkeys.SKINNY_LBL_ANSWER, call=call2)
        pushSoftKey(client, softkeys.SKINNY_LBL_ANSWER, call=call2)
        raise Exception('bad')
    except AssertionError:
        pass
    finally:
        expectSoftkey(client, softkeys.SKINNY_LBL_ANSWER, call=call)
        pushSoftKey(client, softkeys.SKINNY_LBL_ANSWER, call=call)
        time.sleep(2)

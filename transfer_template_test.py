import time

from gui import softkeys
from sccptest.sccptest import *

from sccp.sccpmessagetype import SCCPMessageType
from sccp.sccpcallstate import SCCPCallState
from sccp.sccpstarttone import SCCPStartTone



@client(device='SEP000000000000', serverAddress=('127.0.0.1', 2000), bindAddress=('127.0.0.2', 0))
@client(device='SEP000000000001', serverAddress=('127.0.0.1', 2000), bindAddress=('127.0.0.3', 0))
@client(device='SEP000000000002', serverAddress=('127.0.0.1', 2000), bindAddress=('127.0.0.4', 0))
def testTransferTemplate(customer, operator, operator2):
    try:
        for i in range(20):
            print 'running test #%d' % i
            _test(customer, operator, operator2)
    except AssertionError:
        print 'test failed'
        raw_input()

def _test(customer, operator, operator2):
    OPERATOR_NUMBER = '1101'
    OPERATOR2_NUMBER = '1102'

    expectSoftkey(customer, softkeys.SKINNY_LBL_NEWCALL)
    pushSoftKey(customer, softkeys.SKINNY_LBL_NEWCALL)

    call = getCallInfo(expectCallState(customer, SCCPCallState.SCCP_CHANNELSTATE_OFFHOOK))
    expectTone(customer, SCCPStartTone.SCCP_TONE_INSIDE, call=call)
    dial(customer, OPERATOR_NUMBER)

    call_in = getCallInfo(expectCallState(operator, SCCPCallState.SCCP_CHANNELSTATE_RINGING))

    expectSoftkey(operator, softkeys.SKINNY_LBL_ANSWER, call=call_in)
    pushSoftKey(operator, softkeys.SKINNY_LBL_ANSWER, call=call_in)

    expectCallState(operator, SCCPCallState.SCCP_CHANNELSTATE_OFFHOOK, call=call_in)
    expectCallState(operator, SCCPCallState.SCCP_CHANNELSTATE_CONNECTED, call=call_in)

    expectSoftkey(operator, softkeys.SKINNY_LBL_TRANSFER, call=call_in)
    pushSoftKey(operator, softkeys.SKINNY_LBL_TRANSFER, call=call_in)

    call2 = getCallInfo(expectCallState(operator, SCCPCallState.SCCP_CHANNELSTATE_OFFHOOK))

    expectTone(operator, SCCPStartTone.SCCP_TONE_INSIDE, call=call2)
    dial(operator, OPERATOR2_NUMBER)

    call2_in = getCallInfo(expectCallState(operator2, SCCPCallState.SCCP_CHANNELSTATE_RINGING))

    expectSoftkey(operator2, softkeys.SKINNY_LBL_ANSWER, call=call2_in)
    pushSoftKey(operator2, softkeys.SKINNY_LBL_ANSWER, call=call2_in)

    expectCallState(operator, SCCPCallState.SCCP_CHANNELSTATE_CONNECTED, call=call2)
    expectCallState(operator2, SCCPCallState.SCCP_CHANNELSTATE_CONNECTED, call=call2_in)

    pushSoftKey(operator, softkeys.SKINNY_LBL_TRANSFER, call=call2)
    expectCallState(operator, SCCPCallState.SCCP_CHANNELSTATE_ONHOOK, call=call2)

    pushSoftKey(customer, softkeys.SKINNY_LBL_ENDCALL, call=call)

    time.sleep(1)


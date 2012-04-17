#!/usr/bin/env python

import sys; sys.path.append('../skinnygen/src')

from Queue import Queue

import time
from collections import namedtuple
from sccpdumbphone import SCCPDumbPhone

from sccp.sccpmessage import SCCPMessage
from sccp.sccpmessagetype import SCCPMessageType
from sccp.sccpcallstate import SCCPCallState
from sccp.sccpkeypadbutton import SCCPKeyPadButton
from sccp.sccpsoftkeyevent import SCCPSoftKeyEvent

from gui import softkeys

import inspect_util

from threading import Thread

import imp


SKS_ONHOOK, SKS_CONNECTED, SKS_ONHOLD, \
SKS_RINGIN, SKS_OFFHOOK, SKS_CONNTRANS, SKS_DIGOFF, \
SKS_CONNCONF, SKS_DIAL, SKS_OFFHOOKFEAT = range(10)


KEYSETS_SOFTKEYS = {
    SKS_ONHOOK: [softkeys.SKINNY_LBL_NEWCALL],
    SKS_DIGOFF: [],
    SKS_RINGIN: [softkeys.SKINNY_LBL_ANSWER, softkeys.SKINNY_LBL_ENDCALL],
    SKS_ONHOLD: [softkeys.SKINNY_LBL_TRANSFER],
    SKS_CONNTRANS: [softkeys.SKINNY_LBL_TRANSFER, softkeys.SKINNY_LBL_ENDCALL],
    SKS_CONNECTED: [softkeys.SKINNY_LBL_TRANSFER, softkeys.SKINNY_LBL_ENDCALL],
}

Client = namedtuple('Client', 'queue phone messages reactor keyset')
CallInfo = namedtuple('CallInfo', 'line id')

NO_CALL = CallInfo(0, 0)

QUEUE_SLEEP = 1
QUEUE_RETRY = 3

succStatus = 0

def client(**kwargs):
    def decorator(target):
        if not hasattr(target, 'configs'):
            target.configs = []
        target.configs.insert(0, kwargs)
        target.client = True
        return target
    return decorator

def clearQueue(queue):
    elements = []
    while not queue.empty():
        elements.append(queue.get_nowait())
    return elements

def getMessage(client):
    return client.queue.get()

def findMessage(pred, client):
    newMessages = clearQueue(client.queue)
    client.messages.extend(newMessages)
    found_elem = None
    for i in range(len(client.messages)):
        elem = client.messages[i]
        if pred(elem):
            del client.messages[i]
            found_elem = elem
            break
    print 'element not found when messages =', client.messages
    return found_elem

def findMessageLoop(pred, client, retries, sleep):
    elem = None
    for i in range(retries):
        elem = findMessage(pred, client)
        if elem is not None:
            break
        else:
            time.sleep(sleep)
    return elem

def callEquals(call, message):
    return call is None or hasattr(message, 'line') and hasattr(message, 'callId') and getCallInfo(message)

def match(messageType):
    def decorator(target):
        def f(client, *args, **kw):
            wait = kw.pop('wait', QUEUE_SLEEP)
            def pred(message):
                call = kw.pop('call', None)
                message_type_ok = messageType == message.sccpmessageType
                return message_type_ok and callEquals(call, message) and target(message, *args, **kw)
            message = findMessageLoop(pred, client, QUEUE_RETRY, wait)
            assert message is not None
            return message
        return f
    return decorator
        
def getCallInfo(message):
    return CallInfo(line=message.line, id=message.callId)

@match(SCCPMessageType.SelectSoftKeysMessage)
def expectSoftkey(message, softkey):
    return softkey in KEYSETS_SOFTKEYS[message.softKeySet]

@match(SCCPMessageType.SetRingerMessage)
def expectRinger(message, ringType):
    return message.ringType == ringType

@match(SCCPMessageType.CallStateMessage)
def expectCallState(message, state):
    return message.callState == state

@match(SCCPMessageType.StartToneMessage)
def expectTone(message, tone):
    return message.tone == tone

def pushSoftKey(client, softkey, call=NO_CALL):
    sk_event = SCCPSoftKeyEvent(softkey, call.line, call.id)
    sendMessage(client, sk_event)

def dial(client, number):
    messages = [SCCPKeyPadButton(int(digit)) for digit in number]
    for message in messages:
        sendMessage(client, message)

def clearMessages(client):
    clearQueue(client.queue)
    client.messages[:] = []

def sendMessage(client, message):
    client.reactor.callFromThread(client.phone.client.sendSccpMessage, message)


def setupClientSession(client):
    softKeySetMessage = SCCPMessage(SCCPMessageType.SoftKeySetReqMessage)
    softKeyTemplateMessage = SCCPMessage(SCCPMessageType.SoftKeyTemplateReqMessage)
    sendMessage(client, softKeyTemplateMessage)
    sendMessage(client, softKeySetMessage)


def connectClient(reactor, config, onClient):
    addr, port = config['serverAddress']
    bindAddress = config['bindAddress']

    sccpPhone = SCCPDumbPhone(addr, config['device'])
    sccpPhone.createClient()

    queue = Queue()

    def queueMessage(message):
        queue.put(message)
    sccpPhone.client.handleUnknownMessage(queueMessage)

    def createTimer(intervalSecs,timerCallback):
        reactor.callLater(intervalSecs, timerCallback)
    sccpPhone.createTimer = createTimer

    def onRegistered():
        client = Client(queue, sccpPhone, [], reactor, None)
        onClient(client)
    sccpPhone.onRegistered = onRegistered

    connection = reactor.connectTCP(addr, port, sccpPhone.client, bindAddress=bindAddress)
    return connection

def runTestCase(reactor, configs, func, superviseFunc):        
    clients = []
    connections = []

    def runTestFunc():
        no_errors = False
        try:
            func(*clients)
            no_errors = True
        finally:
            reactor.callFromThread(superviseFunc, connections, no_errors)

    for config in configs:
        def onClient(client):
            setupClientSession(client)
            clients.append(client)
            got_all_clients = len(clients) == len(configs)
            if got_all_clients:
                Thread(target=runTestFunc).start()
        connection = connectClient(reactor, config, onClient)
        connections.append(connection)



def findTestCases(mod):
    functions = inspect_util.get_functions(mod)
    tests = [f for f in functions if hasattr(f, 'client')]
    testCases = [(test.configs, test) for test in tests]
    return testCases

def load_test_module(fname):
    return imp.load_source('test_module', fname)
    
def main():
    from twisted.internet import reactor

    import sys
    fname = sys.argv[1]

    mod = load_test_module(fname)
    testCases = findTestCases(mod)

    threadCount = [len(testCases)]

    def supervise(connections, succ):
        for connection in connections:
            connection.disconnect()
        threadCount[0] = threadCount[0]-1
        if threadCount[0] == 0 or not succ:
            if not succ:
                global succStatus
                succStatus = 1
            reactor.callLater(0.01, reactor.stop)

    for testConfigs, testFunc in testCases:
        runTestCase(reactor, testConfigs, testFunc, supervise)

    reactor.run()
    sys.exit(succStatus)

if __name__ == "__main__":
    main()

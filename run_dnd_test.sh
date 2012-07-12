#!/bin/bash

echo "running FS..."
run-freeswitch.sh -conf conf_dnd -log $FREESWITCH_HOME/log -db $FREESWITCH_HOME/db #-nc -nf
fs_pid=$!
sleep 2
echo "killing FS"
#kill "$fs_pid"

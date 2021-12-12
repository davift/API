#!/bin/bash

if [ $1 == 'on' ]
then
        sudo /etc/init.d/windscribe-cli start
        windscribe connect
elif [ $1 == 'off' ]
then
        windscribe disconnect
elif [ $1 == 'status' ]
then
        windscribe account
        windscribe status
else
        echo ''
        echo 'Missing parameter [on/off/status]'
        echo ''
fi

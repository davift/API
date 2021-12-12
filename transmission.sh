#!/bin/bash

if [ $1 == 'on' ]
then
        sudo /bin/systemctl start transmission-daemon.service
elif [ $1 == 'off' ]
then
        sudo /bin/systemctl stop transmission-daemon.service
else
        echo ''
        echo 'Missing parameter [on/off]'
        echo ''
fi

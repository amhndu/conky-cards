#!/bin/bash
sleep 10
conky -dq -c /home/amish/Projects/conky-cards/time_rc
conky -dq -c /home/amish/Projects/conky-cards/system_rc
conky -dq -c /home/amish/Projects/conky-cards/processes_rc
conky -dq -c /home/amish/Projects/conky-cards/memory_rc
conky -dq -c /home/amish/Projects/conky-cards/filesystem_rc
conky -dq -c /home/amish/Projects/conky-cards/network_rc
conky -dq -c /home/amish/Projects/conky-cards/fortune_rc
conky -dq -c /home/amish/Projects/conky-cards/mediaplayer_rc

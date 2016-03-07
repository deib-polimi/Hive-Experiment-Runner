#!/bin/bash
# Flexiant fault injection tool

customerEmail="eugenio.gianniti@polimi.it"
customerUUID="e50bfd1b-253a-3290-85ff-95e218398b7e"
AuthenticationToken="${customerEmail}/${customerUUID}" # from My account > Account details
rest_service_url="https://cp.sd1.flexiant.net"
# UUIDs array from Clusterone_NodeManager_Slave1 to 9, from slave7 to 15
HOST=('58c0b142-cdb2-3915-a91c-3bd1d2d31216' '480a1db2-20fe-3c50-8227-377e5842dd6c' 'a8bd6ccf-8c77-3592-9660-5b52aa115ff6' \
'5f0ad883-d2a9-3bee-9a89-f77491c8f5c9' '80d4c645-8b12-3806-a374-87e50d1ce837' '34ab54b2-9239-3c31-9fc9-dded3830e5f2' \
'1fc80e40-0d8d-3b0c-82b3-ddf2b4def055' 'ad3c660a-3076-3c5a-a3c2-4741f7bcd390')

# SETUP
serverUUID=${HOST[5]}
STATUS=('STOPPED' 'RUNNING') # STOPPED, RUNNING, REBOOTING
newStatus=${STATUS[1]}
authToken="adeced99-bc1f-3beb-88ac-735928a94a6a:" # renew when no-auth-fails occur

function action () {
  curl -k -X PUT $rest_service_url/rest/user/current/resources/server/$serverUUID/change_status \
  -u $authToken -d "newStatus=$newStatus" -d "safe=TRUE"
}

### MAIN ###

echo ">> UUID: $serverUUID"

if [ ${newStatus} = 'STOPPED' ]; then
  if [[ ! -z $(echo `action` | grep "STOPPED") ]]; then
    echo "Server is already STOPPED."
  else
    echo "Server is SHUTTING DOWN."
  fi
elif [ ${newStatus} = 'RUNNING' ]; then
  if [[ ! -z $(echo `action` | grep "RUNNING") ]]; then
    echo "Server is already RUNNING."
  else
    echo "Server is STARTING."
  fi
else
  echo 'Retry in a few seconds...' # httpErrorCode:503
fi

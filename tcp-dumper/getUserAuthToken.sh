#!/bin/bash
# Flexiant token renewer

EXPIRY='15552000' # seconds, 6 months

curl -X GET https://cp.sd1.flexiant.net/rest/user/current/authentication \
  -u eugenio.gianniti@polimi.it/e50bfd1b-253a-3290-85ff-95e218398b7e \
  -d "automaticallyRenew=TRUE" -d "expiry=$EXPIRY" | tee flexiant_auth_token.txt

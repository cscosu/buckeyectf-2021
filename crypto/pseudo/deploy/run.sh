#!/usr/bin/env sh

set -eu

bits=24
nonce=$(head -c12 /dev/urandom | base64)

cat <<EOF
Send the output of: hashcash -mb${bits} ${nonce}
EOF

if head -n1 | hashcash -cqb${bits} -df /dev/null -r "${nonce}"; then
    exec timeout 60 python3 -u /app/chall.py
else
    echo Stamp verification failed
fi


#!/usr/bin/env python
import json
with open('src/transfer.json', 'r') as f:
    j = json.load(f)
    raw = [bytes.fromhex(x['_source']['layers']['usb.capdata'].replace(':', '')) for x in j]
    single = b''.join(raw)
    with open('decoded.zip', 'wb') as g:
        g.write(single)


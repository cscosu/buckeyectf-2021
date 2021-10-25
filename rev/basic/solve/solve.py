#!/usr/bin/env python
enc = "F4X67ENQPK0{MTJRHL}O3G59UB-ZAWV8S2YI1CD"
indices = [26,25,38,10,6,35,6,12,13,2,14,17,27,38,18,29,23,23,27,30,2,33,27,26,11,16,37,7,22,19]
flag = [enc[x - 1] for x in indices]
print(''.join(flag))

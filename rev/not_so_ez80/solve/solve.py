#!/usr/bin/env python
enc = "WFRSBQAQVWFSVLXJOJHCQOBKRVJLCPUGLJKMJ"
idx = [3,8,20,2,24,23,6,12,19,0,22,5,15,17,11,16,9,13,18,1,4,10,14,7,21]
grid = [9, 19, 3, 0, 20, 11, 6, 23, 1, 16, 21, 14, 7, 17, 22, 12, 15, 13, 18, 8, 2, 24, 10, 5, 4]
flag = [chr(grid[(idx[ord(x)-ord('A')]-(11*(i+1)))%25]+ord('A')) for i,x in enumerate(enc)]
print('BUCKEYE{' + ''.join(flag) + '}')

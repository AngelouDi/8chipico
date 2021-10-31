from random import random
import time
import keyboard

# 0x000 to 0xFFF
# 0x000 to 0x1FF cant be used by programs
# 0xF00 to 0xFFF display refresh
# 0xEA0 to 0xEFF stack, variables, internal
# Most programs start at 0x200 [512] but some 0x600 [1536]
SCREEN_WIDTH = 64
SCREEN_HEIGHT = 32


MEMORY = [None]*4096

#16 Vx registers 8bits each
#0x0 to 0xF, 0xF should not be used by programs

V_REG = [None]*16
#Ix regster 16 bits each
#Usually the 12 most rightmost bits are used
I_REG = None

#Decrement 60Hz/s
TIMER = None
SOUND = None

#Program counter 16 bit
PC = 0
#Stack pointer 8 bit, upmost of stack
SP = 0xEFF
#STACK is 16x16-bit

#Display
DISPLAY = []


#All_keys

AVAILABLE_KEYS = list(range(0x30, 0x3A)) + list(range(0x41, 0x47))
print(AVAILABLE_KEYS)
#Keyboard_map
KEYBOARD_MAP = {
    0x31: '1', 0x32: '2', 0x33: '3', 0x43: '4',
    0x34: 'Q', 0x35: 'W', 0x36: 'E', 0x44: 'R',
    0x37: 'A', 0x38: 'S', 0x39: 'D', 0x45: 'F',
    0x41: 'Z', 0x30: 'X', 0x42: 'C', 0x46: 'V'
}


for x_screen in range(SCREEN_WIDTH):
    new_column = []
    for y_screen in range(SCREEN_HEIGHT):
        new_column.append(0)
    DISPLAY.append(new_column)


def show_display(display):
    for y in range(SCREEN_HEIGHT):
        for x in range(SCREEN_WIDTH):
            print(DISPLAY[x][y], end="")
        print()


def display_clear():
    for x in DISPLAY:
        for y in DISPLAY[x]:
            y = 0


def check_key(key):
    return keyboard.is_pressed(KEYBOARD_MAP[key])

def dec_to_bin(x):
    return int(bin(int(x))[2:])

# Return from subroutine
# 00EE
# PC = address at top of stack
# SP -= 1
def RET():
    global SP
    global PC
    global MEMORY
    PC = MEMORY[SP]
    SP -= 1


# Jump 1nnn
# PC = address nnn
def JMP(addr):
    global PC
    PC = addr


# Call 2nnn
# Calls subroutine at nnn
def CALL(addr):
    global SP
    global PC
    global MEMORY
    SP += 1
    MEMORY[SP] = PC
    PC = addr


# SE 3xkk
def SEB(x, byte):
    global V_REG
    if V_REG[x] == byte:
        global PC
        PC += 2


# SNE 4xkk
def SNEB(x, byte):
    global V_REG
    if V_REG[x] != byte:
        global PC
        PC += 2


# SE 5xy0
def SER(x, y):
    global V_REG
    if V_REG[x] == V_REG[y]:
        global PC
        PC += 2


# LD 6xkk
def LDB(x, byte):
    global V_REG
    V_REG[x] = byte


# ADD 7xkk
def ADDB(x, byte):
    global V_REG
    V_REG[x] = V_REG[x] + byte
    V_REG[x] &= 0x11


# LD 8xy0
def LDRR(x, y):
    global V_REG
    V_REG[y] = V_REG[x]


# OR 8xy1
def ORR(x,y):
    global V_REG
    V_REG[x] = V_REG[x] | V_REG[y]


# AND 8xy2
def ANDR(x, y):
    global V_REG
    V_REG[x] &= V_REG[y]


# XOR 8xy3
def XORR(x, y):
    global V_REG
    V_REG[x] ^= V_REG[y]


# ADD 8xy4
def ADDR(x, y):
    global V_REG
    sum = V_REG[x] + V_REG[y]
    if sum >> 8 == 1:
        V_REG[0xF] = 1
        sum &= 0x11
    V_REG[x] = sum

# SUB 8xy5 #Underflow how it works we do not
def SUBR(x, y):
    global V_REG
    dif = V_REG[x] - V_REG[y]
    if dif < 0:
        V_REG[0xF] = 0
        dif += 256
    else:
        V_REG[0xF] = 1
    V_REG[x] = dif


# SHR 8xy6
def SHR(x):
    V_REG[0xF] = V_REG[x] & 0x01
    V_REG[x] >>= 1


# SUBN 8xy7
def SUBNR(x, y):
    global V_REG
    dif = V_REG[y] - V_REG[x]
    if dif < 0:
        V_REG[0xF] = 0
        dif += 256
    else:
        V_REG[0xF] = 1
    V_REG[x] = dif


# SHL 8xyE
def SHLR(x):
    global V_REG
    V_REG[0xF] = (V_REG[x] >> 7) & 0x01
    V_REG[x] = V_REG[x] << 1 & 0xFF


# SNE 9xy0
def SNER(x, y):
    global V_REG
    if V_REG[x] != V_REG[y]:
        global PC
        PC += 2


# LD Annn
def LDRI(addr):
    global V_REG
    global I_REG
    I_REG = addr


# JP Bnnn
def JMPI(addr):
    global V_REG
    global PC
    PC = addr + V_REG[0x00]


# RND Cxkk
def RNDB(x, byte):
    global V_REG
    V_REG[x] = int(random()*256) & byte


#TODO: Dxyn - DRW

# SKP Ex9E
def SKP(x):
    global V_REG
    if check_key(V_REG[x]):
        global PC
        PC += 2


# SKNP ExA1
def SKNP(x):
    global V_REG
    if not check_key(V_REG[x]):
        global PC
        PC += 2


# LD Fx07
def LDRT(x):
    global V_REG
    global TIMER
    V_REG[x] = TIMER


# LD Fx0A
def LDWFK(x):
    global V_REG
    while True:
        for key in AVAILABLE_KEYS:
            if check_key(key):
                V_REG[x] = key
                return


# LD Fx15
def LDTR(x):
    global V_REG
    global TIMER
    TIMER = V_REG[x]


# LD Fx18
def LDSR(x):
    global V_REG
    global SOUND

    SOUND = V_REG[x]



# ADD Fx1E
def ADDIR(x):
    global V_REG
    global I_REG

    I_REG = (I_REG + V_REG[x]) & 0xFF


#LD Fx29
def LDSPRI(x):
    global I_REG
    global V_REG
    I_REG = V_REG[x] << 8 #CHECK MSB LSB
    I_REG |= V_REG[x+1]


# LD Fx33
def BCD(x):
    global I_REG
    global MEMORY
    global V_REG
    MEMORY[I_REG] = dec_to_bin(V_REG[x] // 100)
    MEMORY[I_REG + 1] = dec_to_bin((V_REG[x] % 100 - V_REG[x] % 10) / 10)
    MEMORY[I_REG + 2] = dec_to_bin(V_REG[x] % 10)



#Fx55
def LDMR(x):
    global I_REG
    global V_REG
    global MEMORY
    for i in range(x+1):
        MEMORY[I_REG + i] = V_REG[i]
        # Maybe increement I

#Fx65
def LDRM(x):
    global I_REG
    global V_REG
    global MEMORY
    for i in range(x+1): # Maybe increment I
        V_REG[i] = MEMORY[I_REG + i]






V_REG[0] = 393
V_REG[1] = 2
V_REG[2] = 4
V_REG[3] = 4

I_REG = 2
BCD(0x00)
print(MEMORY[0], MEMORY[1], MEMORY[2], MEMORY[3], MEMORY[4], MEMORY[5])

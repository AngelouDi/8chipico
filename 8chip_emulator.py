from random import random
import time
import keyboard
import os
VERBOSE = False
# 0x000 to 0xFFF
# 0x000 to 0x1FF cant be used by programs
# 0xF00 to 0xFFF display refresh
# 0xEA0 to 0xEFF stack, variables, internal
# Most programs start at 0x200 [512] but some 0x600 [1536]
SCREEN_WIDTH = 64
SCREEN_HEIGHT = 32

BEGGIN_ROM_ADDRESS = 0x200

MEMORY = [None] * 4096
for i in range(4096):
    MEMORY[i] = 0

# 16 Vx registers 8bits each
# 0x0 to 0xF, 0xF should not be used by programs

V_REG = [0] * 16
# Ix regster 16 bits each
# Usually the 12 most rightmost bits are used
I_REG = 0

# Decrement 60Hz/s
TIMER = 0
SOUND = 0

# Program counter 16 bit
PC = 0
# Stack pointer 8 bit, upmost of stack
SP = 0xEFF
# STACK is 16x16-bit

# Display
DISPLAY = []

# All_keys

AVAILABLE_KEYS = list(range(0x30, 0x3A)) + list(range(0x41, 0x47))
# Keyboard_map
KEYBOARD_MAP = {
    0x31: '1', 0x32: '2', 0x33: '3', 0x43: '4',
    0x34: 'Q', 0x35: 'W', 0x36: 'E', 0x44: 'R',
    0x37: 'A', 0x38: 'S', 0x39: 'D', 0x45: 'F',
    0x41: 'Z', 0x30: 'X', 0x42: 'C', 0x46: 'V',
    0x1: '1', 0x2: '2', 0x3: '3', 0x4: '4',
    0x5: 'Q', 0x6: 'W', 0x7: 'E', 0x8: 'R',
    0x9: 'A', 0xA: 'S', 0xB: 'D', 0xC: 'F',
    0xD: 'Z', 0xE: 'X', 0xF: 'C', 0x10: 'V'
}

# Number sprites
NUMBER_SPRITES = [0xF0, 0x90, 0x90, 0x90, 0xF0,  # 0
                  0x20, 0x60, 0x20, 0x20, 0x70,  # 1
                  0xF0, 0x10, 0xF0, 0x80, 0xF0,  # 2
                  0xF0, 0x10, 0xF0, 0x10, 0xF0,  # 3
                  0x90, 0x90, 0xF0, 0x10, 0x10,  # 4
                  0xF0, 0x80, 0xF0, 0x10, 0xF0,  # 5
                  0xF0, 0x80, 0xF0, 0x90, 0xF0,  # 6
                  0xF0, 0x10, 0x20, 0x40, 0x40,  # 7
                  0xF0, 0x90, 0xF0, 0x90, 0xF0,  # 8
                  0xF0, 0x90, 0xF0, 0x10, 0xF0,  # 9
                  0xF0, 0x90, 0xf0, 0x90, 0x90,  # A
                  0xE0, 0x90, 0xE0, 0x90, 0xE0,  # B
                  0xF0, 0x80, 0x80, 0x80, 0xF0,  # C
                  0xE0, 0x90, 0x90, 0x90, 0xE0,  # D
                  0xF0, 0x80, 0xF0, 0x80, 0xF0,  # E
                  0xF0, 0x80, 0xF0, 0x80, 0x80]  # F

MEMORY[0x00:0x50] = NUMBER_SPRITES

for x_screen in range(SCREEN_WIDTH):
    new_column = []
    for y_screen in range(SCREEN_HEIGHT):
        new_column.append(0)
    DISPLAY.append(new_column)


def show_display(display):
    display_buffer = ""
    display_buffer += "."
    for x in range(SCREEN_WIDTH):
        display_buffer += '_'
    display_buffer += '\n'
    for y in range(SCREEN_HEIGHT):
        display_buffer += '|'
        for x in range(SCREEN_WIDTH):
            if DISPLAY[x][y] == 1:
                display_buffer += '▓'
            else:
                display_buffer += ' '

        display_buffer += '\n'

    clearConsole = lambda: os.system('cls' if os.name in ('nt', 'dos') else 'clear')
    clearConsole()
    print(display_buffer)


def display_clear():
    for x in range(SCREEN_WIDTH):
        for y in range(SCREEN_HEIGHT):
            DISPLAY[x][y] = 0


def check_key(key):
    return keyboard.is_pressed(KEYBOARD_MAP[key])


def dec_to_bin(x):
    return int(bin(int(x))[2:])


# Return from subroutine
# 00EE
# PC = address at top of stack
# SP -= 2
def RET():
    if VERBOSE:
        print("0033")
    global SP
    global PC
    global MEMORY
    PC = MEMORY[SP] << 8
    PC |= MEMORY[SP - 1]
    SP -= 2


# Jump 1nnn
# PC = address nnn
def JMP(addr):
    if VERBOSE:
        print("1nnn")
    global PC
    PC = addr


# Call 2nnn
# Calls subroutine at nnn
def CALL(addr):
    if VERBOSE:
        print("2nnn")
    global SP
    global PC
    global MEMORY
    SP += 2
    MEMORY[SP] = PC >> 8
    MEMORY[SP - 1] = PC & 0xFF
    PC = addr


# SE 3xkk
def SEB(x, byte):
    if VERBOSE:
        print("4xkk")
    global V_REG
    if V_REG[x] == byte:
        global PC
        PC += 2


# SNE 4xkk
def SNEB(x, byte):
    if VERBOSE:
        print("4xkkk")
    global V_REG
    if V_REG[x] != byte:
        global PC
        PC += 2


# SE 5xy0
def SER(x, y):
    if VERBOSE:
        print("5xy0")
    global V_REG
    if V_REG[x] == V_REG[y]:
        global PC
        PC += 2


# LD 6xkk
def LDB(x, byte):
    if VERBOSE:
        print("6xkk")
    global V_REG
    V_REG[x] = byte


# ADD 7xkk
def ADDB(x, byte):
    if VERBOSE:
        print("7xkk")
    global V_REG
    V_REG[x] = V_REG[x] + byte
    V_REG[x] &= 0xFF


# LD 8xy0
def LDRR(x, y):
    if VERBOSE:
        print("8xy0")
    global V_REG
    V_REG[x] = V_REG[y]


# OR 8xy1
def ORR(x, y):
    if VERBOSE:
        print("8xy1")
    global V_REG
    V_REG[x] = V_REG[x] | V_REG[y]


# AND 8xy2
def ANDR(x, y):
    if VERBOSE:
        print("8xy2")
    global V_REG
    V_REG[x] &= V_REG[y]


# XOR 8xy3
def XORR(x, y):
    if VERBOSE:
        print("8xy3")
    global V_REG
    V_REG[x] ^= V_REG[y]


# ADD 8xy4
def ADDR(x, y):
    if VERBOSE:
        print("8xy4")
    global V_REG
    sum = V_REG[x] + V_REG[y]
    if sum >> 8 == 1:
        V_REG[0xF] = 1
        sum &= 0xFF
    else:
        V_REG[0xF] = 0
    V_REG[x] = sum


# SUB 8xy5 #Underflow how it works we do not
def SUBR(x, y):
    if VERBOSE:
        print("8xy5")
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
    if VERBOSE:
        print("8xy6")
    global V_REG
    V_REG[0xF] = V_REG[x] & 0x01
    V_REG[x] >>= 1


# SUBN 8xy7
def SUBNR(x, y):
    if VERBOSE:
        print("8xy7")
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
    if VERBOSE:
        print("8xyE")
    global V_REG
    V_REG[0xF] = (V_REG[x] >> 7) & 0x01
    V_REG[x] = V_REG[x] << 1 & 0xFF


# SNE 9xy0
def SNER(x, y):
    if VERBOSE:
        print("9xy0")
    global V_REG
    if V_REG[x] != V_REG[y]:
        global PC
        PC += 2


# LD Annn
def LDRI(addr):
    if VERBOSE:
        print("Annn")
    global I_REG
    I_REG = addr


# JP Bnnn
def JMPI(addr):
    if VERBOSE:
        print("Bnnn")
    global V_REG
    global PC
    PC = addr + V_REG[0x00]


# RND Cxkk
def RNDB(x, byte):
    if VERBOSE:
        print("Cnnn")
    global V_REG
    V_REG[x] = int(random() * 256) & byte


# TODO: Dxyn - DRW
def DRW(x, y, n):
    if VERBOSE:
        print("Dxyn")
    global MEMORY
    global DISPLAY
    global I_REG
    global V_REG
    erased = 0
    for i in range(n):
        sprite_line = MEMORY[I_REG + i]
        for j in range(8):
            DISPLAY[(V_REG[x] + j) % SCREEN_WIDTH][(V_REG[y] + i) % SCREEN_HEIGHT]
            (V_REG[y] + i) % SCREEN_WIDTH
            original_pixel = DISPLAY[(V_REG[x] + j) % SCREEN_WIDTH][(V_REG[y] + i) % SCREEN_HEIGHT]
            sprite_pixel = sprite_line >> (7 - j) & 0x1
            new_pixel = original_pixel ^ sprite_pixel
            if original_pixel & sprite_pixel == 0x1:
                erased = 0x1
            DISPLAY[(V_REG[x] + j) % SCREEN_WIDTH][(V_REG[y] + i) % SCREEN_HEIGHT] = new_pixel
    V_REG[0xF] = erased
    show_display(DISPLAY)



# SKP Ex9E
def SKP(x):
    if VERBOSE:
        print("Wz9E")
    global V_REG
    if check_key(V_REG[x]):
        global PC
        PC += 2


# SKNP ExA1
def SKNP(x):
    if VERBOSE:
        print("ExA1")
    global V_REG
    if not check_key(V_REG[x]):
        global PC
        PC += 2


# LD Fx07
def LDRT(x):
    if VERBOSE:
        print("Fx07")
    global V_REG
    global TIMER
    V_REG[x] = TIMER


# LD Fx0A
def LDWFK(x):
    if VERBOSE:
        print("Fx0A")
    global V_REG
    while True:
        for key in AVAILABLE_KEYS:
            if check_key(key):
                V_REG[x] = key
                return


# LD Fx15
def LDTR(x):
    if VERBOSE:
        print("Fx15")
    global V_REG
    global TIMER
    TIMER = V_REG[x]


# LD Fx18
def LDSR(x):
    if VERBOSE:
        print("Fx18")
    global V_REG
    global SOUND

    SOUND = V_REG[x]


# ADD Fx1E
def ADDIR(x):
    if VERBOSE:
        print("Fx1E")
    global V_REG
    global I_REG

    I_REG = I_REG + V_REG[x]


# LD Fx29
def LDSPRI(x):
    if VERBOSE:
        print("Fx29")
    global I_REG
    global V_REG
    I_REG = int(V_REG[x]) * 5

# LD Fx33
def BCD(x):
    if VERBOSE:
        print("Fx33")
    global I_REG
    global MEMORY
    global V_REG


    MEMORY[I_REG] = (V_REG[x] // 100) % 10
    MEMORY[I_REG + 1] = (V_REG[x] // 10 ) % 10
    MEMORY[I_REG + 2] = V_REG[x]  % 10


# Fx55
def LDMR(x):
    if VERBOSE:
        print("Fx55")
    global I_REG
    global V_REG
    global MEMORY
    for i in range(x + 1):
        MEMORY[I_REG + i] = V_REG[i]
        # Maybe increement I


# Fx65
def LDRM(x):
    if VERBOSE:
        print("Fx65")
    global I_REG
    global V_REG
    global MEMORY
    for i in range(x + 1):  # Maybe increment I
        V_REG[i] = MEMORY[I_REG + i]


def print_mem(start, end):
    for address in range(start, end):
        print("ADDRESS {}: {} {}".format(hex(address), hex(MEMORY[address]), dec_to_bin(MEMORY[address])))


def read_pc():
    global PC
    b0 = MEMORY[PC] >> 4 & 0xF
    b1 = MEMORY[PC] & 0xF
    b2 = MEMORY[PC + 1] >> 4 & 0xF
    b3 = MEMORY[PC + 1] & 0xF
    PC += 2
    interpret_command(b0, b1, b2, b3)

def interpret_command(b0, b1, b2, b3):
    addr = 0
    byte = 0

    x = b1
    y = b2

    addr |= b1
    addr <<= 4
    addr |= b2  # nnn
    addr <<= 4
    addr |= b3

    byte |= b2
    byte <<= 4  # kk
    byte |= b3

    if b0 == 0x0 and b1 == 0x0 and b2 == 0xE and b3 == 0x0:
        display_clear()
    elif b0 == 0x0 and b1 == 0x0 and b2 == 0xE and b3 == 0xE:
        RET()
    elif b0 == 0x1:
        JMP(addr)
    elif b0 == 0x2:
        CALL(addr)
    elif b0 == 0x3:
        SEB(x, byte)
    elif b0 == 0x4:
        SNEB(x, byte)
    elif b0 == 0x5 and b3 == 0x0:
        SER(x, y)
    elif b0 == 0x6:
        LDB(x, byte)
    elif b0 == 0x7:
        ADDB(x, byte)
    elif b0 == 0x8 and b3 == 0x0:
        LDRR(x, y)
    elif b0 == 0x8 and b3 == 0x1:
        ORR(x, y)
    elif b0 == 0x8 and b3 == 0x2:
        ANDR(x, y)
    elif b0 == 0x8 and b3 == 0x3:
        XORR(x, y)
    elif b0 == 0x8 and b3 == 0x4:
        ADDR(x, y)
    elif b0 == 0x8 and b3 == 0x5:
        SUBR(x, y)
    elif b0 == 0x8 and b3 == 0x6:
        SHR(x)
    elif b0 == 0x8 and b3 == 0x7:
        SUBNR(x, y)
    elif b0 == 0x8 and b3 == 0xE:
        SHLR(x)
    elif b0 == 0x9 and b3 == 0x0:
        SNER(x, y)
    elif b0 == 0xA:
        LDRI(addr)
    elif b0 == 0xB:
        JMPI(addr)
    elif b0 == 0xC:
        RNDB(x, byte)
    elif b0 == 0xD:
        DRW(x, y, b3)
    elif b0 == 0xE and b2 == 0x9 and b3 == 0xE:
        SKP(x)
    elif b0 == 0xE and b2 == 0xA and b3 == 0x1:
        SKNP(x)
    elif b0 == 0xF and b2 == 0x0 and b3 == 0x7:
        LDRT(x)
    elif b0 == 0xF and b2 == 0x0 and b3 == 0xA:
        LDWFK(x)
    elif b0 == 0xF and b2 == 0x1 and b3 == 0x5:
        LDTR(x)
    elif b0 == 0xF and b2 == 0x1 and b3 == 0x8:
        LDSR(x)
    elif b0 == 0xF and b2 == 0x1 and b3 == 0xE:
        ADDIR(x)
    elif b0 == 0xF and b2 == 0x2 and b3 == 0x9:
        LDSPRI(x)
    elif b0 == 0xF and b2 == 0x3 and b3 == 0x3:
        BCD(x)
    elif b0 == 0xF and b2 == 0x5 and b3 == 0x5:
        LDMR(x)
    elif b0 == 0xF and b2 == 0x6 and b3 == 0x5:
        LDRM(x)
    else:
        print("UNKNOWN")
        print("{} {} {} {} ".format(hex(b0), hex(b1), hex(b2),hex(b3)))
        input("")


def load_rom(filename):
    with open(filename, "rb") as rom:
        byte = rom.read(1)
        address = BEGGIN_ROM_ADDRESS
        while byte:
            MEMORY[address] = int.from_bytes(byte, 'little')
            address += 1
            byte = rom.read(1)


load_rom("")
PC = 0x200
SP = 0xEFF
while True:
    if TIMER > 0:
        TIMER -= 1
    if SOUND > 0:
        SOUND -= 1
    time.sleep(0.002)
    read_pc()

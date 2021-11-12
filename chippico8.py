from random import random
import keyboard
import os

VERBOSE = False
TERMINAL_GAME = True

SCREEN_WIDTH = 64
SCREEN_HEIGHT = 32

BEGIN_ROM_ADDRESS = 0x200

AVAILABLE_KEYS = list(range(0x30, 0x3A)) + list(range(0x41, 0x47))
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

KEYS = [
    '1', '2', '3', '4',
    'Q', 'W', 'E', 'R',
    'A', 'S', 'D', 'F',
    'Z', 'X', 'C', 'V']

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

def update_keys():


def check_key(key):
    return keyboard.is_pressed(KEYBOARD_MAP[key])


def dec_to_bin(x):
    return int(bin(int(x))[2:])


class Chip8:

    def __init__(self):
        self.MEMORY = [0] * 4096
        for i in range(4096):
            self.MEMORY[i] = 0

        self.MEMORY[0x00:0x50] = NUMBER_SPRITES

        self.V_REG = [0] * 16
        self.I_REG = 0

        self.TIMER = 0
        self.SOUND = 0

        self.PC = 0
        self.SP = 0xEFF

        self.DISPLAY = []
        self.ACTIVE_KEYS = []

        for x_screen in range(SCREEN_WIDTH):
            new_column = []
            for y_screen in range(SCREEN_HEIGHT):
                new_column.append(0)
            self.DISPLAY.append(new_column)

    def display_clear(self):
        for x in range(SCREEN_WIDTH):
            for y in range(SCREEN_HEIGHT):
                self.DISPLAY[x][y] = 0

    def show_display(self):
        display_buffer = ""
        display_buffer += "."
        for x in range(SCREEN_WIDTH):
            display_buffer += '_'
        display_buffer += '\n'
        for y in range(SCREEN_HEIGHT):
            display_buffer += '|'
            for x in range(SCREEN_WIDTH):
                if self.DISPLAY[x][y] == 1:
                    display_buffer += '▓'
                else:
                    display_buffer += ' '

            display_buffer += '\n'

        clearConsole = lambda: os.system('cls' if os.name in ('nt', 'dos') else 'clear')
        clearConsole()
        print(display_buffer)

    def get_display(self):
        return self.DISPLAY

    # Return from subroutine
    # 00EE
    # PC = address at top of stack
    # SP -= 2
    def RET(self):
        if VERBOSE:
            print("0033")
        self.PC = self.MEMORY[self.SP] << 8
        self.PC |= self.MEMORY[self.SP - 1]
        self.SP -= 2

    # Jump 1nnn
    # PC = address nnn
    def JMP(self, addr):
        if VERBOSE:
            print("1nnn")
        self.PC = addr

    # Call 2nnn
    # Calls subroutine at nnn
    def CALL(self, addr):
        if VERBOSE:
            print("2nnn")
        self.SP += 2
        self.MEMORY[self.SP] = self.PC >> 8
        self.MEMORY[self.SP - 1] = self.PC & 0xFF
        self.PC = addr

    # SE 3xkk
    def SEB(self, x, byte):
        if VERBOSE:
            print("4xkk")
        if self.V_REG[x] == byte:
            self.PC += 2

    # SNE 4xkk
    def SNEB(self, x, byte):
        if VERBOSE:
            print("4xkkk")
        if self.V_REG[x] != byte:
            self.PC += 2

    # SE 5xy0
    def SER(self, x, y):
        if VERBOSE:
            print("5xy0")
        if self.V_REG[x] == self.V_REG[y]:
            self.PC += 2

    # LD 6xkk
    def LDB(self, x, byte):
        if VERBOSE:
            print("6xkk")
        self.V_REG[x] = byte

    # ADD 7xkk
    def ADDB(self, x, byte):
        if VERBOSE:
            print("7xkk")
        self.V_REG[x] = self.V_REG[x] + byte
        self.V_REG[x] &= 0xFF

    # LD 8xy0
    def LDRR(self, x, y):
        if VERBOSE:
            print("8xy0")
        self.V_REG[x] = self.V_REG[y]

    # OR 8xy1
    def ORR(self, x, y):
        if VERBOSE:
            print("8xy1")
        self.V_REG[x] = self.V_REG[x] | self.V_REG[y]

    # AND 8xy2
    def ANDR(self, x, y):
        if VERBOSE:
            print("8xy2")
        self.V_REG[x] &= self.V_REG[y]

    # XOR 8xy3
    def XORR(self, x, y):
        if VERBOSE:
            print("8xy3")
        self.V_REG[x] ^= self.V_REG[y]

    # ADD 8xy4
    def ADDR(self, x, y):
        if VERBOSE:
            print("8xy4")
        sum = self.V_REG[x] + self.V_REG[y]
        if sum >> 8 == 1:
            self.V_REG[0xF] = 1
            sum &= 0xFF
        else:
            self.V_REG[0xF] = 0
        self.V_REG[x] = sum

    # SUB 8xy5 #Underflow how it works we do not
    def SUBR(self, x, y):
        if VERBOSE:
            print("8xy5")
        dif = self.V_REG[x] - self.V_REG[y]
        if dif < 0:
            self.V_REG[0xF] = 0
            dif += 256
        else:
            self.V_REG[0xF] = 1
        self.V_REG[x] = dif

    # SHR 8xy6
    def SHR(self, x):
        if VERBOSE:
            print("8xy6")
        self.V_REG[0xF] = self.V_REG[x] & 0x01
        self.V_REG[x] >>= 1

    # SUBN 8xy7
    def SUBNR(self, x, y):
        if VERBOSE:
            print("8xy7")
        dif = self.V_REG[y] - self.V_REG[x]
        if dif < 0:
            self.V_REG[0xF] = 0
            dif += 256
        else:
            self.V_REG[0xF] = 1
        self.V_REG[x] = dif

    # SHL 8xyE
    def SHLR(self, x):
        if VERBOSE:
            print("8xyE")
        self.V_REG[0xF] = (self.V_REG[x] >> 7) & 0x01
        self.V_REG[x] = self.V_REG[x] << 1 & 0xFF

    # SNE 9xy0
    def SNER(self, x, y):
        if VERBOSE:
            print("9xy0")
        if self.V_REG[x] != self.V_REG[y]:
            self.PC += 2

    # LD Annn
    def LDRI(self, addr):
        if VERBOSE:
            print("Annn")
        self.I_REG = addr

    # JP Bnnn
    def JMPI(self, addr):
        if VERBOSE:
            print("Bnnn")
        self.PC = addr + self.V_REG[0x00]

    # RND Cxkk
    def RNDB(self, x, byte):
        if VERBOSE:
            print("Cnnn")
        self.V_REG[x] = int(random() * 256) & byte

    def DRW(self, x, y, n):
        if VERBOSE:
            print("Dxyn")
        erased = 0
        for i in range(n):
            sprite_line = self.MEMORY[self.I_REG + i]
            for j in range(8):
                original_pixel = self.DISPLAY[(self.V_REG[x] + j) % SCREEN_WIDTH][(self.V_REG[y] + i) % SCREEN_HEIGHT]
                sprite_pixel = sprite_line >> (7 - j) & 0x1
                new_pixel = original_pixel ^ sprite_pixel
                if original_pixel & sprite_pixel == 0x1:
                    erased = 0x1
                self.DISPLAY[(self.V_REG[x] + j) % SCREEN_WIDTH][(self.V_REG[y] + i) % SCREEN_HEIGHT] = new_pixel
        self.V_REG[0xF] = erased
        if TERMINAL_GAME:
            self.show_display()

    # SKP Ex9E
    def SKP(self, x):
        if VERBOSE:
            print("Wz9E")
        if check_key(self.V_REG[x]):
            self.PC += 2

    # SKNP ExA1
    def SKNP(self, x):
        if VERBOSE:
            print("ExA1")
        if not check_key(self.V_REG[x]):
            self.PC += 2

    # LD Fx07
    def LDRT(self, x):
        if VERBOSE:
            print("Fx07")
        self.V_REG[x] = self.TIMER

    # LD Fx0A
    def LDWFK(self, x):
        if VERBOSE:
            print("Fx0A")
        while True:
            for key in AVAILABLE_KEYS:
                if check_key(key):
                    self.V_REG[x] = key
                    return

    # LD Fx15
    def LDTR(self, x):
        if VERBOSE:
            print("Fx15")
        self.TIMER = self.V_REG[x]

    # LD Fx18
    def LDSR(self, x):
        if VERBOSE:
            print("Fx18")

        self.SOUND = self.V_REG[x]

    # ADD Fx1E
    def ADDIR(self, x):
        if VERBOSE:
            print("Fx1E")

        self.I_REG = self.I_REG + self.V_REG[x]

    # LD Fx29
    def LDSPRI(self, x):
        if VERBOSE:
            print("Fx29")
        self.I_REG = int(self.V_REG[x]) * 5

    # LD Fx33
    def BCD(self, x):
        if VERBOSE:
            print("Fx33")

        self.MEMORY[self.I_REG] = (self.V_REG[x] // 100) % 10
        self.MEMORY[self.I_REG + 1] = (self.V_REG[x] // 10) % 10
        self.MEMORY[self.I_REG + 2] = self.V_REG[x] % 10

    # Fx55
    def LDMR(self, x):
        if VERBOSE:
            print("Fx55")
        for i in range(x + 1):
            self.MEMORY[self.I_REG + i] = self.V_REG[i]

    # Fx65
    def LDRM(self, x):
        if VERBOSE:
            print("Fx65")
        for i in range(x + 1):  # Maybe increment I
            self.V_REG[i] = self.MEMORY[self.I_REG + i]

    def print_mem(self, start, end):
        for address in range(start, end):
            print("ADDRESS {}: {} {}".format(hex(address), hex(self.MEMORY[address]), dec_to_bin(self.MEMORY[address])))

    def read_pc(self):
        b0 = self.MEMORY[self.PC] >> 4 & 0xF
        b1 = self.MEMORY[self.PC] & 0xF
        b2 = self.MEMORY[self.PC + 1] >> 4 & 0xF
        b3 = self.MEMORY[self.PC + 1] & 0xF
        self.PC += 2
        self.interpret_command(b0, b1, b2, b3)

    def load_rom(self, filename):
        with open(filename, "rb") as rom:
            byte = rom.read(1)
            address = BEGIN_ROM_ADDRESS
            while byte:
                self.MEMORY[address] = int.from_bytes(byte, 'little')
                address += 1
                byte = rom.read(1)
        self.PC = 0x200
        self.SP = 0xEFF

    def interpret_command(self, b0, b1, b2, b3):
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
            self.display_clear()
        elif b0 == 0x0 and b1 == 0x0 and b2 == 0xE and b3 == 0xE:
            self.RET()
        elif b0 == 0x1:
            self.JMP(addr)
        elif b0 == 0x2:
            self.CALL(addr)
        elif b0 == 0x3:
            self.SEB(x, byte)
        elif b0 == 0x4:
            self.SNEB(x, byte)
        elif b0 == 0x5 and b3 == 0x0:
            self.SER(x, y)
        elif b0 == 0x6:
            self.LDB(x, byte)
        elif b0 == 0x7:
            self.ADDB(x, byte)
        elif b0 == 0x8 and b3 == 0x0:
            self.LDRR(x, y)
        elif b0 == 0x8 and b3 == 0x1:
            self.ORR(x, y)
        elif b0 == 0x8 and b3 == 0x2:
            self.ANDR(x, y)
        elif b0 == 0x8 and b3 == 0x3:
            self.XORR(x, y)
        elif b0 == 0x8 and b3 == 0x4:
            self.ADDR(x, y)
        elif b0 == 0x8 and b3 == 0x5:
            self.SUBR(x, y)
        elif b0 == 0x8 and b3 == 0x6:
            self.SHR(x)
        elif b0 == 0x8 and b3 == 0x7:
            self.SUBNR(x, y)
        elif b0 == 0x8 and b3 == 0xE:
            self.SHLR(x)
        elif b0 == 0x9 and b3 == 0x0:
            self.SNER(x, y)
        elif b0 == 0xA:
            self.LDRI(addr)
        elif b0 == 0xB:
            self.JMPI(addr)
        elif b0 == 0xC:
            self.RNDB(x, byte)
        elif b0 == 0xD:
            self.DRW(x, y, b3)
        elif b0 == 0xE and b2 == 0x9 and b3 == 0xE:
            self.SKP(x)
        elif b0 == 0xE and b2 == 0xA and b3 == 0x1:
            self.SKNP(x)
        elif b0 == 0xF and b2 == 0x0 and b3 == 0x7:
            self.LDRT(x)
        elif b0 == 0xF and b2 == 0x0 and b3 == 0xA:
            self.LDWFK(x)
        elif b0 == 0xF and b2 == 0x1 and b3 == 0x5:
            self.LDTR(x)
        elif b0 == 0xF and b2 == 0x1 and b3 == 0x8:
            self.LDSR(x)
        elif b0 == 0xF and b2 == 0x1 and b3 == 0xE:
            self.ADDIR(x)
        elif b0 == 0xF and b2 == 0x2 and b3 == 0x9:
            self.LDSPRI(x)
        elif b0 == 0xF and b2 == 0x3 and b3 == 0x3:
            self.BCD(x)
        elif b0 == 0xF and b2 == 0x5 and b3 == 0x5:
            self.LDMR(x)
        elif b0 == 0xF and b2 == 0x6 and b3 == 0x5:
            self.LDRM(x)
        else:
            print("UNKNOWN")
            print("{} {} {} {} ".format(hex(b0), hex(b1), hex(b2), hex(b3)))
            input("")

    def tick(self):
        if self.TIMER > 0:
            self.TIMER -= 1
        if self.SOUND > 0:
            self.SOUND -= 1
        self.read_pc()


if TERMINAL_GAME:
    emu = Chip8()
    emu.load_rom("pong.ch8")
    while True:
        emu.tick()

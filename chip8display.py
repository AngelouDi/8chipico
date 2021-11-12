import chippico8
import pygame

SCREEN_WIDTH = 64
SCREEN_HEIGHT = 32
SCREEN_MULTIPLIER = 12
print('tests')

def show_display(DISPLAY):
    for y in range(SCREEN_HEIGHT):
        for x in range(SCREEN_WIDTH):
            if DISPLAY[x][y] == 1:
                pygame.draw.rect(screen, WHITE, [x*SCREEN_MULTIPLIER, y*SCREEN_MULTIPLIER, 1*SCREEN_MULTIPLIER, 1*SCREEN_MULTIPLIER])


pygame.init()
size = [SCREEN_WIDTH*SCREEN_MULTIPLIER, SCREEN_HEIGHT*SCREEN_MULTIPLIER]
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
screen = pygame.display.set_mode(size)

done = False
clock = pygame.time.Clock()

emu = chippico8.Chip8()
emu.load_rom("pong.ch8")
while not done:
    clock.tick(480)
    emu.update_keys()
    emu.tick()
    for event in pygame.event.get(): # User did something
        if event.type == pygame.QUIT: # If user clicked close
            done=True # Flag that we are done so we exit this loop
    screen.fill(BLACK)
    DISPLAY = emu.get_display()
    show_display(DISPLAY)
    pygame.display.flip()

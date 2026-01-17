import pygame
import sys

pygame.init()

# Set up the window dimensions
WIDTH, HEIGHT = 800, 600
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Pygame Window Test")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    SCREEN.fill(BLACK) # Fill the screen with black
    # You can draw other things here
    
    pygame.display.flip() # Update the full display Surface to the screen

pygame.quit()
sys.exit()

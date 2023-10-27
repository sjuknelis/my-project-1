import pygame, sys

from state import State, Action
from constants import WIDTH, HEIGHT, CAR_SIZE, CHECKPOINT_SIZE

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (128, 0, 0)
GREEN = (0, 255, 0)

pygame.init()

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Car Game")

drawing = False
last_drawing_pos = None
checkpoint_placed = False

def render_state(state: State) -> Action:
    global drawing, last_drawing_pos, checkpoint_placed

    # Drawing track using mouse
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            drawing = True
            last_drawing_pos = event.pos
        elif event.type == pygame.MOUSEBUTTONUP:
            drawing = False
        elif event.type == pygame.MOUSEMOTION and drawing:
            state.tracks.append((last_drawing_pos, event.pos))
            last_drawing_pos = event.pos

    keys = pygame.key.get_pressed()

    if keys[pygame.K_r]:
        state.reset()
    
    if keys[pygame.K_e] and not checkpoint_placed:
        checkpoint_placed = True
        state.checkpoints.append(pygame.mouse.get_pos())
    elif not keys[pygame.K_e]:
        checkpoint_placed = False

    screen.fill(BLACK)

    for checkpoint in state.checkpoints:
        rect = pygame.Rect((checkpoint[0] - CHECKPOINT_SIZE, checkpoint[1] - CHECKPOINT_SIZE, CHECKPOINT_SIZE * 2, CHECKPOINT_SIZE * 2))
        pygame.draw.rect(screen, RED, rect)

    pygame.draw.polygon(screen, WHITE, state.car.get_points())

    for track in state.tracks:
        pygame.draw.line(screen, WHITE, track[0], track[1], 3)

    for ray in state.rays:
        pygame.draw.line(screen, GREEN, ray[0], ray[1])
    
    pygame.display.flip()

    acc = 0
    steer = 0
    if keys[pygame.K_w]:
        acc = 1
    elif keys[pygame.K_s]:
        acc = -1
    if keys[pygame.K_d]:
        steer = 1
    elif keys[pygame.K_a]:
        steer = -1
    return Action(acc, steer)
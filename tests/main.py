# Example file showing a circle moving on screen

import sys

sys.path.append("../../skelform_pygame")

import pygame
import zipfile
import json
import skelform_pygame
import time

pygame.init()
screen = pygame.display.set_mode((1280, 720))
pygame.display.set_caption("SkelForm Basic Animation")
clock = pygame.time.Clock()
running = True
dt = 0

player_pos = pygame.Vector2(screen.get_width() / 2, screen.get_height() / 2)

(skellington, skellington_img) = skelform_pygame.load_skelform("untitled.skf")

moving = False

while running:
    # poll for events
    # pygame.QUIT event means the user clicked X to close your window
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # fill the screen with a color to wipe away anything from last frame
    screen.fill("black")

    keys = pygame.key.get_pressed()
    if keys[pygame.K_w]:
        player_pos.y -= 300 * dt
        moving = True
    if keys[pygame.K_s]:
        player_pos.y += 300 * dt
        moving = True
    if keys[pygame.K_a]:
        player_pos.x -= 300 * dt
        moving = True
    if keys[pygame.K_d]:
        player_pos.x += 300 * dt
        moving = True

    speed = 50

    if keys[pygame.K_UP]:
        skellington.armature.bones[1].pos.y += speed
    if keys[pygame.K_DOWN]:
        skellington.armature.bones[1].pos.y -= speed
    if keys[pygame.K_LEFT]:
        skellington.armature.bones[1].pos.x -= speed
    if keys[pygame.K_RIGHT]:
        skellington.armature.bones[1].pos.x += speed

    anim_idx = 0

    if moving:
        anim_idx = 1

    frame = skelform_pygame.time_frame(
        time.time(), skellington.armature.animations[0], False, True
    )
    props = skelform_pygame.animate(
        screen,
        skellington.armature,
        skellington_img,
        anim_idx,
        frame,
        skelform_pygame.AnimOptions(player_pos, 0.25),
    )
    skelform_pygame.draw(props, skellington.armature.styles, skellington_img, screen)

    # flip() the display to put your work on screen
    pygame.display.flip()

    # limits FPS to 60
    # dt is delta time in seconds since last frame, used for framerate-
    # independent physics.
    dt = clock.tick(60) / 1000
    moving = False

pygame.quit()

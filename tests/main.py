# Example file showing a circle moving on screen

import sys

import os

os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "1"

sys.path.append("../../skelform_pygame")

import pygame
import zipfile
import json
import skelform_pygame as skf_pg
import time
import copy

pygame.init()
screen = pygame.display.set_mode((1280, 720))
pygame.display.set_caption("SkelForm Basic Animation")
font = pygame.font.Font(None, 50)
clock = pygame.time.Clock()
running = True
dt = 0
dir = 1
anim_time = 0
blend = 20
last_anim_idx = 0
vel_y = 0
started_falling = False
ground = screen.get_height() / 2 + 75

player_pos = pygame.Vector2(screen.get_width() / 2, ground - 50)

(skellina, skellina_img) = skf_pg.load("skellina.skf")


# helper for finding bone by name
def bone(name, bones):
    for bone in bones:
        if bone.name == name:
            return bone


# renders text with a drop-shadow
def text(str, pos):
    drop_x = pos[0]
    drop_y = pos[1]
    drop_x += 2.5
    drop_y += 2.5
    text = font.render(str, True, (0, 0, 0))
    screen.blit(text, (drop_x, drop_y))
    text = font.render(str, True, (255, 255, 255))
    screen.blit(text, pos)


while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    screen.fill("grey")
    speed = 400
    moving = False
    keys = pygame.key.get_pressed()

    # moving with A and D keys
    if keys[pygame.K_a]:
        player_pos.x -= speed * dt
        dir = -1
        moving = True
    if keys[pygame.K_d]:
        player_pos.x += speed * dt
        dir = 1
        moving = True

    # press space to jump
    grounded = player_pos.y > ground
    if keys[pygame.K_SPACE] and grounded:
        player_pos.y = ground - 1
        vel_y = -10
        grounded = False
        started_falling = False
        anim_time = 0

    # gravity
    player_pos.y += vel_y
    vel_y += 0.3
    if grounded:
        vel_y = 0

    # animation states
    anim_idx = 0
    looping = True
    reversing = False
    blend_frames = 20
    if moving:
        anim_idx = 1
    if not grounded:
        anim_idx = 3
        looping = False

    # falling animation
    if vel_y > 0:
        if not started_falling:
            anim_time = 0
        started_falling = True
        reversing = True
        blend_frames = 0

    # reset animation timer whenever a new animation starts
    if last_anim_idx != anim_idx:
        anim_time = 0
        last_anim_idx = anim_idx

    anim_frame = skf_pg.time_frame(
        anim_time, skellina.animations[anim_idx], reversing, looping
    )
    skellina.bones = skf_pg.animate(
        skellina,
        [skellina.animations[anim_idx]],
        [anim_frame],
        [blend_frames],
    )

    # make immutable edits to armature for construction
    skellina_c = copy.deepcopy(skellina)

    # point shoulder and head to mouse
    skel_scale = 0.15
    shoulder_target = bone("Left Shoulder Pad Target", skellina_c.bones)
    looker = bone("Looker", skellina_c.bones)
    raw_mouse = pygame.mouse.get_pos()
    mouse = skf_pg.skf_py.Vec2(
        -player_pos.x / skel_scale * dir + raw_mouse[0] / skel_scale * dir,
        player_pos.y / skel_scale - raw_mouse[1] / skel_scale,
    )
    shoulder_target.pos = mouse
    looker.pos = mouse

    # flip shoulder IK constraint if looking the other way
    left_shoulder = bone("Left Shoulder Pad", skellina_c.bones)
    looking_back_left = dir == -1 and raw_mouse[0] > player_pos.x
    looking_back_right = dir != -1 and raw_mouse[0] < player_pos.x
    if looking_back_left or looking_back_right:
        bone("Skull", skellina_c.bones).scale.y = -1
        left_shoulder.ik_constraint = 1
    else:
        left_shoulder.ik_constraint = 2

    # construct and draw skellina
    props = skf_pg.construct(
        skellina_c,
        screen,
        skf_pg.ConstructOptions(
            player_pos,
            scale=pygame.Vector2(skel_scale * dir, skel_scale),
        ),
    )
    skf_pg.draw(props, skellina_c.styles, skellina_img, screen)
    pygame.draw.circle(screen, (255, 0, 0), (raw_mouse), 5)

    # Text
    offset = 40
    initial = 25
    text("A - Move left", (25, initial))
    text("D - Move right", (25, initial + offset))
    text("Space - Jump", (25, initial + offset * 2))
    text("Skellina will look at and reach for cursor", (25, initial + offset * 3))

    pygame.display.flip()

    dt = clock.tick(144) / 1000
    anim_time += clock.get_time() / 1000

pygame.quit()

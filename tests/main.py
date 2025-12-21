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
clock = pygame.time.Clock()
running = True
dt = 0
dir = 1
anim_time = 0
blend = 20

player_pos = pygame.Vector2(screen.get_width() / 2, screen.get_height() / 2)

(skellington, skellington_img) = skf_pg.load("skellina.skf")


def bone(name, bones):
    for bone in bones:
        if bone.name == name:
            return bone


while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    screen.fill("grey")

    speed = 400

    moving = False

    keys = pygame.key.get_pressed()
    if keys[pygame.K_a]:
        player_pos.x -= speed * dt
        dir = -1
        moving = True
    if keys[pygame.K_d]:
        player_pos.x += speed * dt
        dir = 1
        moving = True

    keys_down = pygame.key.get_just_pressed()
    if keys_down[pygame.K_d]:
        anim_time = 0
        blend = 20
    if keys_down[pygame.K_a]:
        anim_time = 0
        blend = 20

    keys_up = pygame.key.get_just_released()
    if keys_up[pygame.K_d]:
        anim_time = 0
        blend = 20
    if keys_up[pygame.K_a]:
        anim_time = 0
        blend = 20

    anim_idx = 0
    if moving:
        anim_idx = 1

    anim_frame = skf_pg.time_frame(
        anim_time, skellington.animations[anim_idx], False, True
    )
    skellington.bones = skf_pg.animate(
        skellington,
        [skellington.animations[anim_idx]],
        [anim_frame],
        [20],
    )

    # make immutable edits to armature for construction
    skellington_c = copy.deepcopy(skellington)

    # point shoulder and head to mouse
    skel_scale = 0.15
    shoulder_target = bone("Left Shoulder Pad Target", skellington_c.bones)
    looker = bone("Looker", skellington_c.bones)
    raw_mouse = pygame.mouse.get_pos()
    mouse = skf_pg.skf_py.Vec2(
        -player_pos.x / skel_scale * dir + raw_mouse[0] / skel_scale * dir,
        player_pos.y / skel_scale - raw_mouse[1] / skel_scale,
    )
    shoulder_target.pos = mouse
    looker.pos = mouse

    # flip shoulder IK constraint if looking the other way
    left_shoulder = bone("Left Shoulder Pad", skellington_c.bones)
    looking_back_left = dir == -1 and raw_mouse[0] > player_pos.x
    looking_back_right = dir != -1 and raw_mouse[0] < player_pos.x
    if looking_back_left or looking_back_right:
        bone("Skull", skellington_c.bones).scale.y = -1
        left_shoulder.ik_constraint = 1
    else:
        left_shoulder.ik_constraint = 2

    # construct and draw skellina
    props = skf_pg.construct(
        skellington_c,
        screen,
        skf_pg.AnimOptions(
            player_pos,
            scale=pygame.Vector2(skel_scale * dir, skel_scale),
            blend_frames=[blend],
        ),
    )
    skf_pg.draw(props, skellington_c.styles, skellington_img, screen)
    pygame.draw.circle(screen, (255, 0, 0), (raw_mouse), 5)

    pygame.display.flip()

    dt = clock.tick(144) / 1000
    anim_time += clock.get_time() / 1000

pygame.quit()

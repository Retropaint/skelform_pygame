import pygame
import skelform_python
import math
import copy
import zipfile
import json


def load_skelform(path):
    with zipfile.ZipFile(path, "r") as zip_file:
        skelform_root = json.load(zip_file.open("armature.json"))
        texture_img = pygame.image.load(zip_file.open("textures.png"))

    return (skelform_root, texture_img)


class AnimOptions:
    def __init__(
        self,
        # Offset armature's position by this much.
        pos_offset: pygame.Vector2 = pygame.Vector2(0, 0),
        # Scale armature by a factor of this.
        scale_factor=0.25,
        # Should the armature immediately be rendered?
        # Set to False if you would like to process the armature some more before rendering.
        render=True,
    ):
        self.pos_offset = pos_offset
        self.scale_factor = scale_factor
        self.render = render


# Animate a SkelForm armature.
def animate(
    screen,
    armature,
    texture_img,
    anim_idx,
    frame=-1,
    elapsed_time=-1,
    anim_options=AnimOptions(),
):
    if elapsed_time != -1:
        frame = get_frame_by_time(armature, anim_idx, elapsed_time, False)

    props = skelform_python.animate(armature, anim_idx, frame)

    ao = anim_options

    for prop in props:
        if prop["tex_idx"] == -1:
            continue

        tex = armature["textures"][prop["tex_idx"]]
        tex_surf = clip(
            texture_img,
            tex["offset"]["x"],
            tex["offset"]["y"],
            tex["size"]["x"],
            tex["size"]["y"],
        )

        scale_x = ao.scale_factor * prop["scale"]["x"]
        scale_y = ao.scale_factor * prop["scale"]["y"]
        tex_surf = pygame.transform.scale_by(
            tex_surf,
            (scale_x, scale_y),
        )

        # pygame treats positive y as down
        prop["pos"]["y"] = -prop["pos"]["y"]

        # adjust positions for scale factor
        # actual scale is already accounted for in core logic
        prop["pos"]["x"] *= ao.scale_factor
        prop["pos"]["y"] *= ao.scale_factor

        # push textures back left and up so that it's centered
        prop["pos"]["x"] -= tex_surf.get_size()[0] / 2
        prop["pos"]["y"] -= tex_surf.get_size()[1] / 2

        deg = prop["rot"] * 180 / 3.14
        (tex_surf, rect) = rot_center(tex_surf, tex_surf.get_rect(), deg)

        if not ao.render:
            continue

        screen.blit(
            tex_surf,
            rect.move(
                prop["pos"]["x"] + ao.pos_offset.x,
                prop["pos"]["y"] + ao.pos_offset.y,
            ),
        )

    return props


def get_frame_by_time(armature, anim_idx, elapsed, reverse):
    return skelform_python.get_frame_by_time(armature, anim_idx, elapsed, reverse)


# https://stackoverflow.com/a/71370036
def clip(surface, x, y, x_size, y_size):  # Get a part of the image
    handle_surface = surface.copy()  # Sprite that will get process later
    clipRect = pygame.Rect(x, y, x_size, y_size)  # Part of the image
    handle_surface.set_clip(clipRect)  # Clip or you can call cropped
    image = surface.subsurface(handle_surface.get_clip())  # Get subsurface
    return image.copy()  # Return


# https://www.pygame.org/wiki/RotateCenter
def rot_center(image, rect, angle):
    rot_image = pygame.transform.rotate(image, angle)
    rot_rect = rot_image.get_rect(center=rect.center)
    return rot_image, rot_rect

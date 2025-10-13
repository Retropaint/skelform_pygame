import sys

import math
import copy
import zipfile
import json

# 3rd parties
sys.path.append("../../skelform_python")
import skelform_python as skf_py
import dacite
import pygame


def load_skelform(path):
    with zipfile.ZipFile(path, "r") as zip_file:
        skelform_root_json = json.load(zip_file.open("armature.json"))
        texture_img = pygame.image.load(zip_file.open("textures.png"))

    skelform_root = dacite.from_dict(data_class=skf_py.SkfRoot, data=skelform_root_json)

    return (skelform_root, texture_img)


class AnimOptions:
    def __init__(
        self,
        # Offset armature's position by this much.
        pos_offset: pygame.Vector2 = pygame.Vector2(0, 0),
        # Scale armature by a factor of this.
        scale_factor=0.25,
    ):
        self.pos_offset = pos_offset
        self.scale_factor = scale_factor


# Animate a SkelForm armature.
def animate(
    armature,
    texture_img,
    animations: list[skf_py.Animation],
    frames: list[int],
    screen,
    anim_options=AnimOptions(),
):
    for a in range(len(animations)):
        armature.bones = skf_py.animate(armature, animations[a], frames[a])

    props = copy.deepcopy(armature.bones)
    inh_props = copy.deepcopy(props)

    inh_props = skf_py.inheritance(inh_props, {})
    for i in range(10):
        ik_rots = skf_py.inverse_kinematics(inh_props, armature.ik_families, False)
    props = skf_py.inheritance(props, ik_rots)

    ao = anim_options

    for prop in props:
        # pygame treats positive y as down
        prop.pos.y = -prop.pos.y

        # adjust positions for scale factor
        # actual scale is already accounted for in core logic
        prop.pos.x *= ao.scale_factor
        prop.pos.y *= ao.scale_factor
        prop.scale.x *= ao.scale_factor
        prop.scale.y *= ao.scale_factor
        prop.pos.x += ao.pos_offset.x
        prop.pos.y += ao.pos_offset.y

    return props


def draw(props, styles, tex_img, screen):
    props.sort(key=lambda prop: prop.zindex)
    surfaces = []

    for prop in props:
        if prop.style_ids is None:
            continue

        tex = styles[0].textures[prop.tex_idx]
        tex_surf = clip(
            tex_img,
            tex.offset.x,
            tex.offset.y,
            tex.size.x,
            tex.size.y,
        )

        tex_surf = pygame.transform.scale_by(
            tex_surf,
            (math.fabs(prop.scale.x), math.fabs(prop.scale.y)),
        )

        # push textures back left and up so that it's centered
        prop_tex_pos = prop.pos
        prop_tex_pos.x -= tex_surf.get_size()[0] / 2
        prop_tex_pos.y -= tex_surf.get_size()[1] / 2

        deg = prop.rot * 180 / 3.14
        (tex_surf, rect) = rot_center(tex_surf, tex_surf.get_rect(), deg)

        surfaces.append(
            (
                tex_surf,
                rect.move(
                    prop_tex_pos.x,
                    prop_tex_pos.y,
                ),
            )
        )

    screen.blits(surfaces)


def get_frame_by_time(armature, anim_idx, elapsed, reverse):
    return skf_py.get_frame_by_time(armature, anim_idx, elapsed, reverse)


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


def time_frame(time, animation: skf_py.Animation, reverse, loop):
    return skf_py.time_frame(time, animation, reverse, loop)


def format_frame(frame, animation: skf_py.Animation, reverse, loop):
    return skf_py.format_frame(frame, animation, reverse, loop)

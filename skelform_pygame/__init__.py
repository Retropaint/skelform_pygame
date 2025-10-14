import sys

import math
import copy
import zipfile
import json
from dataclasses import dataclass
from typing import Optional

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


@dataclass
class AnimOptions:
    position: pygame.math.Vector2
    scale: pygame.Vector2
    blend_frames: list[int]

    def __init__(
        self,
        position=pygame.Vector2(0, 0),
        scale=pygame.Vector2(0.25, 0.25),
        blend_frames=[0, 0, 0, 0, 0, 0],
    ):
        self.position = position
        self.scale = scale
        self.blend_frames = blend_frames


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
        armature.bones = skf_py.animate(
            armature, animations[a], frames[a], anim_options.blend_frames[a]
        )

    inh_props = copy.deepcopy(armature.bones)

    inh_props = skf_py.inheritance(inh_props, {})
    for i in range(10):
        ik_rots = skf_py.inverse_kinematics(inh_props, armature.ik_families, False)

    final_bones = copy.deepcopy(armature.bones)
    final_bones = skf_py.inheritance(final_bones, ik_rots)

    for bone in final_bones:
        bone.pos.y = -bone.pos.y

        bone.pos = skf_py.vec_mul(bone.pos, anim_options.scale)
        bone.scale = skf_py.vec_mul(bone.scale, anim_options.scale)
        bone.pos = skf_py.vec_add(bone.pos, anim_options.position)

        either = anim_options.scale.x < 0 or anim_options.scale.y < 0
        both = anim_options.scale.x < 0 and anim_options.scale.y < 0
        if either and not both:
            bone.rot = -bone.rot

    return final_bones


def draw(props, styles, tex_img, screen):
    props.sort(key=lambda prop: prop.zindex)
    surfaces = []

    for prop in props:
        if prop.style_ids is None:
            continue

        tex = styles[0].textures[prop.tex_idx]

        tex_surf = tex_img.subsurface(
            (tex.offset.x, tex.offset.y, tex.size.x, tex.size.y)
        )

        tex_surf = pygame.transform.scale_by(
            tex_surf,
            (math.fabs(prop.scale.x), math.fabs(prop.scale.y)),
        )

        if prop.scale.x < 0 or prop.scale.y < 0:
            tex_surf = pygame.transform.flip(
                tex_surf, prop.scale.x < 0, prop.scale.y < 0
            )

        # push textures back left and up so that it's centered
        prop_tex_pos = prop.pos
        prop_tex_pos.x -= tex_surf.get_size()[0] / 2
        prop_tex_pos.y -= tex_surf.get_size()[1] / 2

        deg = math.degrees(prop.rot)
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


# https://www.pygame.org/wiki/RotateCenter
def rot_center(image, rect, angle):
    rot_image = pygame.transform.rotate(image, angle)
    rot_rect = rot_image.get_rect(center=rect.center)
    return rot_image, rot_rect


def time_frame(time, animation: skf_py.Animation, reverse, loop):
    return skf_py.time_frame(time, animation, reverse, loop)


def format_frame(frame, animation: skf_py.Animation, reverse, loop):
    return skf_py.format_frame(frame, animation, reverse, loop)

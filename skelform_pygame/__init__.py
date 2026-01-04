import sys

import math
import copy
import zipfile
import json
from dataclasses import dataclass
from typing import Optional

# 3rd parties
# sys.path.append("/Users/o/projects/skelform/runtimes/skelform_python")
import skelform_python as skf_py
import dacite
import pygame


def load(path):
    with zipfile.ZipFile(path, "r") as zip_file:
        armature_json = json.load(zip_file.open("armature.json"))

    armature = dacite.from_dict(data_class=skf_py.Armature, data=armature_json)
    textures = []

    with zipfile.ZipFile(path, "r") as zip_file:
        for atlas in armature.atlases:
            textures.append(pygame.image.load(zip_file.open(atlas.filename)))

    return (armature, textures)


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
    animations: list[skf_py.Animation],
    frames: list[int],
    blend_frames: list[int],
):
    return skf_py.animate(armature, animations, frames, blend_frames)


def construct(armature, screen, anim_options):
    final_bones = skf_py.construct(armature)

    for bone in final_bones:
        bone.pos.y = -bone.pos.y

        bone.pos *= anim_options.scale
        bone.scale *= anim_options.scale
        bone.pos += anim_options.position

        bone.rot = skf_py.check_bone_flip(bone.rot, anim_options.scale)

    return final_bones


def draw(props, styles, tex_imgs, screen):
    props.sort(key=lambda prop: prop.zindex)
    surfaces = []

    final_textures = skf_py.setup_bone_textures(props, styles)

    for prop in props:
        if prop.id not in final_textures:
            continue

        tex = final_textures[prop.id]

        tex_surf = tex_imgs[tex.atlas_idx].subsurface(
            (tex.offset.x, tex.offset.y, tex.size.x, tex.size.y)
        )

        pygame.Surface.convert(tex_surf)

        tex_surf = pygame.transform.smoothscale_by(
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

        moved_rect = rect.move(
            prop_tex_pos.x,
            prop_tex_pos.y,
        )

        surfaces.append((tex_surf, moved_rect))

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

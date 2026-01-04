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
from typing import List, Tuple


# Loads an `.skf` file.
def load(path: str) -> Tuple[skf_py.Armature, List[pygame.image]]:
    with zipfile.ZipFile(path, "r") as zip_file:
        armature_json = json.load(zip_file.open("armature.json"))

    armature = dacite.from_dict(data_class=skf_py.Armature, data=armature_json)
    textures = []

    with zipfile.ZipFile(path, "r") as zip_file:
        for atlas in armature.atlases:
            textures.append(pygame.image.load(zip_file.open(atlas.filename)))

    return (armature, textures)


@dataclass
class ConstructOptions:
    position: pygame.math.Vector2
    scale: pygame.Vector2

    def __init__(
        self,
        position=pygame.Vector2(0, 0),
        scale=pygame.Vector2(0.25, 0.25),
    ):
        self.position = position
        self.scale = scale


# Transforms an armature's bones based on the provided animation(s) and their frame(s).
#
# `smoothFrames` is used to smoothly interpolate transforms. Mainly used for smooth animation transitions. Higher frames are smoother.
#
# Note: smoothFrames should ideally be set to 0 (or empty) when reversing animations.
def animate(
    armature: skf_py.Armature,
    animations: list[skf_py.Animation],
    frames: list[int],
    smooth_frames: list[int],
) -> List[skf_py.Bone]:
    return skf_py.animate(armature, animations, frames, smooth_frames)


# Returns the constructed array of bones from this armature.
#
# While constructing, several options (positional offset, scale) may be set.
def construct(
    armature: skf_py.Armature, screen: pygame.Surface, anim_options: ConstructOptions
) -> List[skf_py.Bone]:
    final_bones = skf_py.construct(armature)

    for bone in final_bones:
        bone.pos.y = -bone.pos.y

        bone.pos *= anim_options.scale
        bone.scale *= anim_options.scale
        bone.pos += anim_options.position

        bone.rot = skf_py.check_bone_flip(bone.rot, anim_options.scale)

    return final_bones


# Draws the bones to the provided screen, using the provided styles and textures.
#
# Recommended: include the whole texture array from the file even if not all will be used,
# as the provided styles will determine the final appearance.
def draw(
    bones: List[skf_py.Bone],
    styles: List[skf_py.Style],
    tex_imgs: List[pygame.image],
    screen: pygame.Surface,
):
    bones.sort(key=lambda prop: prop.zindex)
    surfaces = []

    final_textures = skf_py.setup_bone_textures(bones, styles)

    for bone in bones:
        if bone.id not in final_textures:
            continue

        tex = final_textures[bone.id]

        tex_surf = tex_imgs[tex.atlas_idx].subsurface(
            (tex.offset.x, tex.offset.y, tex.size.x, tex.size.y)
        )

        pygame.Surface.convert(tex_surf)

        tex_surf = pygame.transform.smoothscale_by(
            tex_surf,
            (math.fabs(bone.scale.x), math.fabs(bone.scale.y)),
        )

        if bone.scale.x < 0 or bone.scale.y < 0:
            tex_surf = pygame.transform.flip(
                tex_surf, bone.scale.x < 0, bone.scale.y < 0
            )

        # push textures back left and up so that it's centered
        prop_tex_pos = bone.pos
        prop_tex_pos.x -= tex_surf.get_size()[0] / 2
        prop_tex_pos.y -= tex_surf.get_size()[1] / 2

        deg = math.degrees(bone.rot)
        (tex_surf, rect) = rot_center(tex_surf, tex_surf.get_rect(), deg)

        moved_rect = rect.move(
            prop_tex_pos.x,
            prop_tex_pos.y,
        )

        surfaces.append((tex_surf, moved_rect))

    screen.blits(surfaces)


# https://www.pygame.org/wiki/RotateCenter
def rot_center(image: pygame.image, rect: pygame.Rect, angle: float):
    rot_image = pygame.transform.rotate(image, angle)
    rot_rect = rot_image.get_rect(center=rect.center)
    return rot_image, rot_rect


# Returns the animation frame based on the provided time.
def time_frame(time: int, animation: skf_py.Animation, reverse: bool, loop: bool):
    return skf_py.time_frame(time, animation, reverse, loop)


# Returns the properly bound animation frame based on the provided animation.
def format_frame(frame: int, animation: skf_py.Animation, reverse: bool, loop: bool):
    return skf_py.format_frame(frame, animation, reverse, loop)

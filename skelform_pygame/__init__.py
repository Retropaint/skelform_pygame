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
        velocity=pygame.Vector2(0, 0),
    ):
        self.position = position
        self.scale = scale
        self.velocity = velocity


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
def construct(armature: skf_py.Armature, const_options: ConstructOptions):
    armature.constructed_bones = skf_py.construct(armature)

    for b in range(len(armature.constructed_bones)):
        const_bone = armature.constructed_bones[b]

        const_bone.pos.y = -const_bone.pos.y

        const_bone.pos *= const_options.scale
        const_bone.scale *= const_options.scale
        const_bone.pos += const_options.position

        if const_bone.physics_id != -1:
            phys = armature.physics[const_bone.physics_id]
            if phys:
                phys.global_pos -= const_options.velocity

        if skf_py.is_facing_left(const_options.scale):
            const_bone.rot = -const_bone.rot

    return (armature.bones, armature.constructed_bones)


# Draws the bones to the provided screen, using the provided styles and textures.
#
# Recommended: include the whole texture array from the file even if not all will be used,
# as the provided styles will determine the final appearance.
def draw(
    armature: skf_py.Armature,
    styles: List[skf_py.Style],
    tex_imgs: List[pygame.image],
    screen: pygame.Surface,
):
    armature.constructed_bones.sort(
        key=lambda prop: prop.visuals_id != -1
        and armature.visuals[prop.visuals_id].zindex
    )
    surfaces = []

    for bone in armature.constructed_bones:
        if bone.visuals_id == -1:
            continue
        visuals = armature.visuals[bone.visuals_id]

        tex = skf_py.get_bone_texture(visuals.tex, styles)
        if not tex:
            continue

        scale = skf_py.Vec2(
            bone.scale.x * visuals.pivot_scale.x, bone.scale.y * visuals.pivot_scale.y
        )

        # setup texture surface
        tex_surf = tex_imgs[tex.atlas_idx].subsurface(
            (tex.offset.x, tex.offset.y, tex.size.x, tex.size.y)
        )
        tex_surf = pygame.transform.scale_by(
            tex_surf,
            (math.fabs(scale.x), math.fabs(scale.y)),
        )

        if scale.x < 0 or scale.y < 0:
            tex_surf = pygame.transform.flip(tex_surf, scale.x < 0, scale.y < 0)

        # will be used to flip pivot rotations if necessary
        dir = -1 if skf_py.is_facing_left(bone.scale) else 1

        # setup pivot
        pivot_pos = (
            skf_py.rotate_vec2(visuals.pivot_pos * tex.size, bone.rot * dir) * bone.scale
        )
        pivot_pos.y = -pivot_pos.y

        # rotate texture from its center
        deg = math.degrees(bone.rot + visuals.pivot_rot * dir)
        (tex_surf, rect) = rot_center(tex_surf, tex_surf.get_rect(), deg)

        # push textures back left and up so that it's centered
        push_center = skf_py.Vec2(
            tex.size.x / 2 * math.fabs(bone.scale.x),
            tex.size.y / 2 * math.fabs(bone.scale.y),
        )

        final_rect = rect.move(
            bone.pos.x + (pivot_pos.x - push_center.x),
            bone.pos.y + (pivot_pos.y - push_center.y),
        )

        surfaces.append((tex_surf, final_rect))

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

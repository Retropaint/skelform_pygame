Library for running [SkelForm](https://skelform.org) animations in
[Pygame](https://pygame.org).

```
import skelform_pygame as skf_pg
```

## Basic Setup

- `skf_pg.load()` - loads `.skf` file and returns armature & textures, to be
  used later
- `skf_pg.animate()` - transforms the armature's bones based on the animation(s)
- `skf_pg.construct()` - provides the bones from this armature that are ready
  for use
- `skf_pg.draw()` - draws the bones on-screen, with the provided style(s)

### 1. Load:

```
(armature, textures) = skf_pg.load("skellina.skf")
```

This should only be called once (eg; before main game loop), and `armature` and
`textures` should be kept for later use.

### 2\. Animate:

```
# use `skf_pg.time_frame()` to get the animation frame based on time (1000 = 1 second)
time = 2000
frame = skf_pg.time_frame(time, armature.animations[0], False, True)

print(frame) # will be at the 2 second mark of the animation

armature.bones = skf_pg.animate(armature, [armature.animations[0]], [0], [0])
```

_Note: not needed if armature is statilc_

### 3\. Construct:

```
center = pygame.Vector2(screen.get_width()/2, screen.get_height()/2)

final_bones = skf_pg.construct(
    armature,
    screen,
    skf_pg.AnimOptions(
      pos=center
    )
)
```

Modifications to the armature (eg; aiming at cursor) may be done before or after
construction.

### 4\. Draw:

```
skf_pg.draw(final_bones, armature.styles, textures, screen)
```

## Limitations

- Mesh deformation not supported

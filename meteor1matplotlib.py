import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation

#son matplotlib makes me do this just to change keybinds
if 's' in plt.rcParams['keymap.save']:
    plt.rcParams['keymap.save'].remove('s')


#menu text in console, maybe ill change it later
#i might remove drifting idk it seems like worse than the other one

print("Select Star Types:")
print("1: Drifting")
print("2: Following")
mode_choice = input("Enter 1 or 2: ").strip()

#TO-DO
# for some reason the top of the box gets stained when you move idk
#slow down meteor movement, make it damage the ship
#make it more clear when a meteor is damaged and stuff
#rn this isn't bad tho
#WE LOVE DRIFTING MECHANICS
#Point score S tier whatever maybe boosts and power ups if you do good
#oh yeah also catch up mechanics/rubberbanding if they do bad
#make different modes of shooting like laser or something
#screenshake when a large asteroid explodes or when your ship takes damage.
#freeze frames spam Pausing the game for a fraction of a second (e.g., 50 milliseconds) right when a bullet strikes an asteroid to emphasize the impact.
#particle effect swhen you shoot or destroy asteroid or  other stuff like raising score etc
#maybe i can add LORE? that took so long last time tho
#sound effects and music
#remember to have a bunch of different laser shots sfx so the sound doesn't become repetitive, and explosion sfx
#make stuff flash  white for one frame before it breaks apart, or add a glowing bloom effect to neon vector lines
# actually make the game lol by spawning bullets, moving asteroids at random angles, and programming the logic to split large asteroids into medium and small pieces upon impact
#detect hits between bullets, asteroids, and the player ship, plus adding lives, respawning with brief invulnerability, and game-over states
#add  vector-style particle explosions, sound effects, a scoring system, and maybe? other types of enemies

#hold on these star effects are sick i might have to make an exploration or something game
#where instead of teleporting from one side to the other when you cross
#it uses the 1/3/1 rule of screen control that would be nice













width,height = 100,100
rotatespeed = 10
accel = 0.3
drag = 0.92
laserspeed = 4.0
maxprojectiles = 5
meteorspeed = 1.0
recoil_strength = 0.15
shoot_cooldown = 8
shoot_timer = 0

#okay so here i probably have to change some stuff
#like the meteorspeed is not individualized for ehach meteor right now
#and theres other stuff i gotta change
#levels, special abilities, and powerups?

ship = [width / 2, height / 2, 0.0, 0.0, 90.0]
projectiles = []
keys_pressed = set()
thruster_level = 0.0

meteors = []
meteor_spawn_timer = 0
meteor_spawn_rate = 65
score = 0

ship_shape = np.array([[0, 2], [-1.5, -1.5], [0, -0.5], [1.5, -1.5], [0, 2]])
thruster_shape = np.array([[0, -0.5], [-0.7, -1.5], [0, -3.0], [0.7, -1.5], [0, -0.5]])
# ^ okay this looks kinda trash maybe ill fix later
# i mean maybe not the shape more like the way that it appears and disappears

num_stars = 80
stars_x = np.random.uniform(0, width, num_stars)
stars_y = np.random.uniform(1, height-1, num_stars)

star_depth = np.random.power(0.6, num_stars)
if mode_choice == "2":
    star_speeds = 0.3 + star_depth * 1.2
else:
    star_speeds = 0.08 + star_depth * 0.35

star_sizes = 1.0 + star_depth * 6.0
star_base_alphas = 0.25 + star_depth * 0.7

star_colors = np.random.choice(
    ['#FFFFFF', '#DCE8FF', '#FFF3D6', '#E3D4FF'],
    size=num_stars,
    p=[0.55, 0.2, 0.15, 0.1]
)

twinkle_offsets = np.random.uniform(0, 2 * np.pi, num_stars)
fig, ax = plt.subplots(figsize=(6, 6), facecolor='#050510')
ax.set_facecolor('#050510')
ax.set_xlim(0, width)
ax.set_ylim(0, height)
ax.set_aspect('equal', adjustable='box')

#deltarune lookin backdrop
#maybe with some effects itll look good tho
ax.grid(True, color='#1A1A3A', linestyle='-', linewidth=1)
ax.set_xticks(np.arange(0, width, 10))
ax.set_yticks(np.arange(0, height, 10))
ax.set_xticklabels([])
ax.set_yticklabels([])

for spine in ax.spines.values():
    spine.set_visible(True)
    spine.set_color('#444466')
    spine.set_linewidth(2)

stars_glow = ax.scatter(stars_x, stars_y, c=star_colors, s=star_sizes * 4.5, alpha=star_base_alphas * 0.2, edgecolors='none', clip_on=True)
stars_plot = ax.scatter(stars_x, stars_y, c=star_colors, s=star_sizes, alpha=star_base_alphas, edgecolors='none', clip_on=True)
lasers_plot, = ax.plot([], [], 'o', color='#FF3366', markersize=4, clip_on=True)
thruster_plot, = ax.plot([], [], color='magenta', lw=1.5, alpha=0.8, clip_on=True)
ship_plot, = ax.plot([], [], color='cyan', lw=2, clip_on=True)

meteor_plots = []
for i in range(100):
    line, = ax.plot([], [], color='#FFAA55', lw=1.8, clip_on=True)
    meteor_plots.append(line)

score_text = ax.text(
    3, 95, "POINTS: 0",
    color='#FFFFFF',
    fontsize=11,
    fontweight='bold',
    verticalalignment='top'
)

def spawn_meteor(x=None, y=None, size=3):
    if x is None:
        side = np.random.randint(0, 4)

        if side == 0:
            x, y = np.random.uniform(0, width), height
        elif side == 1:
            x, y = np.random.uniform(0, width), 0
        elif side == 2:
            x, y = 0, np.random.uniform(0, height)
        else:
            x, y = width, np.random.uniform(0, height)

    angle = np.arctan2(height / 2 - y, width / 2 - x)
    angle += np.random.uniform(-1.0, 1.0)

    speed = meteorspeed * np.random.uniform(0.5, 1.5)

    points = np.random.randint(8, 13)
    angles = np.linspace(0, 2 * np.pi, points, endpoint=False)
    radii = size * np.random.uniform(0.7, 1.3, points)

    health = {3: 3, 2: 2, 1: 1}[size]

    meteors.append({
        'x': x,
        'y': y,
        'vx': np.cos(angle) * speed,
        'vy': np.sin(angle) * speed,
        'size': size,
        'health': health,
        'max_health': health,
        'angles': angles,
        'radii': radii,
        'flash': 0
    })

def on_key_press(event):
    keys_pressed.add(event.key)

def on_key_release(event):
    keys_pressed.discard(event.key)

fig.canvas.mpl_connect('key_press_event', on_key_press)
fig.canvas.mpl_connect('key_release_event', on_key_release)

def update_game(frame):
    global ship, stars_x, stars_y, projectiles, thruster_level, shoot_timer
    global meteors, meteor_spawn_timer, score

    if shoot_timer > 0:
        shoot_timer -= 1

    if ' ' in keys_pressed and shoot_timer == 0 and len(projectiles) < maxprojectiles:
        angle_rad = np.radians(ship[4])
        vx = np.cos(angle_rad) * laserspeed
        vy = np.sin(angle_rad) * laserspeed
        start_x = ship[0] + np.cos(angle_rad) * 2
        start_y = ship[1] + np.sin(angle_rad) * 2
        projectiles.append([start_x, start_y, vx, vy])

        ship[2] -= np.cos(angle_rad) * recoil_strength
        ship[3] -= np.sin(angle_rad) * recoil_strength

        shoot_timer = shoot_cooldown

    if 'left' in keys_pressed:
        ship[4] += rotatespeed
    if 'right' in keys_pressed:
        ship[4] -= rotatespeed
    if 'up' in keys_pressed:
        angle_rad = np.radians(ship[4])
        ship[2] += np.cos(angle_rad) * accel
        ship[3] += np.sin(angle_rad) * accel
    if 'down' in keys_pressed:
        angle_rad = np.radians(ship[4])
        ship[2] -= np.cos(angle_rad) * (accel * 0.5)
        ship[3] -= np.sin(angle_rad) * (accel * 0.5)

    ship[2] *= drag
    ship[3] *= drag
    ship[0] = (ship[0] + ship[2]) % width
    ship[1] = (ship[1] + ship[3]) % height

    active_projectiles = []
    for p in projectiles:
        p[0] += p[2]
        p[1] += p[3]
        if 0 <= p[0] <= width and 0 <= p[1] <= height:
            active_projectiles.append(p)
    projectiles = active_projectiles

    meteor_spawn_timer += 1
    if meteor_spawn_timer >= meteor_spawn_rate:
        spawn_meteor(size=3)
        meteor_spawn_timer = 0

    for meteor in meteors:
        meteor['x'] = (meteor['x'] + meteor['vx']) % width
        meteor['y'] = (meteor['y'] + meteor['vy']) % height

    remaining_projectiles = []
    destroyed = []

    for p in projectiles:
        hit = False

        for meteor in meteors:
            if meteor in destroyed:
                continue

            dx = p[0] - meteor['x']
            dy = p[1] - meteor['y']

            dx = (dx + width / 2) % width - width / 2
            dy = (dy + height / 2) % height - height / 2

            if np.sqrt(dx**2 + dy**2) < meteor['size']:
                hit = True

                meteor['health'] -= 1
                meteor['flash'] = 3

                if meteor['health'] <= 0:
                    destroyed.append(meteor)

                    if meteor['size'] == 3:
                        score += 100

                        for i in range(2):
                            spawn_meteor(
                                meteor['x'],
                                meteor['y'],
                                size=2
                            )

                    elif meteor['size'] == 2:
                        score += 50

                        for i in range(2):
                            spawn_meteor(
                                meteor['x'],
                                meteor['y'],
                                size=1
                            )

                    else:
                        score += 25

                break

        if not hit:
            remaining_projectiles.append(p)

    projectiles = remaining_projectiles

    for meteor in destroyed:
        if meteor in meteors:
            meteors.remove(meteor)

    for meteor in meteors:
        if meteor['flash'] > 0:
            meteor['flash'] -= 1

    for i, plot in enumerate(meteor_plots):
        if i < len(meteors):
            meteor = meteors[i]
            angles = meteor['angles']
            radii = meteor['radii']

            mx = meteor['x'] + np.cos(angles) * radii
            my = meteor['y'] + np.sin(angles) * radii

            mx = np.append(mx, mx[0])
            my = np.append(my, my[0])

            plot.set_data(mx, my)

            if meteor['flash'] > 0:
                plot.set_color('#FFFFFF')
                plot.set_linewidth(3)
            else:
                plot.set_color('#FFAA55')
                plot.set_linewidth(1.8)

            plot.set_visible(True)
        else:
            plot.set_data([], [])
            plot.set_visible(False)

    if projectiles:
        lasers_plot.set_data([p[0] for p in projectiles], [p[1] for p in projectiles])
    else:
        lasers_plot.set_data([], [])

    #i just realized these names are unfortunately abstract
    #ship[0] is the x coordinate
    #ship 1 is y coord
    #ship 2 is horizontal velocity
    #ship 3 is velocity vertically
    #ship 4 is angle of the ship facing since its a triangle

    if mode_choice == "2":
        stars_x -= ship[2] * star_speeds
        stars_y -= ship[3] * star_speeds
        stars_x %= width
        stars_y %= height
    else:
        stars_y -= star_speeds
        stars_y %= height

    offsets = np.c_[stars_x, stars_y]
    stars_glow.set_offsets(offsets)
    stars_plot.set_offsets(offsets)

    twinkle = np.clip(star_base_alphas + 0.15 * np.sin(frame * 0.15 + twinkle_offsets), 0.1, 1.0)
    stars_plot.set_alpha(twinkle)
    stars_glow.set_alpha(twinkle * 0.2)
    rad = np.radians(ship[4] - 90)
    c, s = np.cos(rad), np.sin(rad)
    rot_matrix = np.array([[c, -s], [s, c]])
    if 'up' in keys_pressed:
        thruster_level = min(1.0, thruster_level + 0.25)
    else:
        thruster_level = max(0.0, thruster_level - 0.15)

    if thruster_level > 0:
        flicker_scale = np.random.uniform(0.7, 1.3) * thruster_level
        current_thruster = thruster_shape.copy()
        current_thruster[:, 1] *= flicker_scale
        rot_thruster = current_thruster @ rot_matrix.T
        thruster_plot.set_data(rot_thruster[:, 0] + ship[0], rot_thruster[:, 1] + ship[1])
        thruster_plot.set_alpha(0.85 * thruster_level)
        thruster_plot.set_visible(True)
    else:
        thruster_plot.set_visible(False)

    transformed_shape = ship_shape @ rot_matrix.T
    ship_plot.set_data(transformed_shape[:, 0] + ship[0], transformed_shape[:, 1] + ship[1])
    score_text.set_text(f"POINTS: {score}")

    return [stars_glow, stars_plot, lasers_plot, thruster_plot, ship_plot, score_text] + meteor_plots

def init_game():
    stars_glow.set_offsets(np.empty((0, 2)))
    stars_plot.set_offsets(np.empty((0, 2)))
    lasers_plot.set_data([], [])
    thruster_plot.set_data([], [])
    ship_plot.set_data([], [])
    thruster_plot.set_data([], [])

    for plot in meteor_plots:
        plot.set_data([], [])

    return [stars_glow, stars_plot, lasers_plot, thruster_plot, ship_plot, score_text] + meteor_plots

ani = animation.FuncAnimation(fig, update_game, init_func=init_game, interval=33, blit=True, cache_frame_data=False)
print("Game opened in new window.")
print("Move with arrow keys, space to shoot.")
plt.show()

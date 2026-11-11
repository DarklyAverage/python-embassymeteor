import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation


#menu text in console, maybe ill change it later
#i might remove drifting idk it seems like worse than the other one

print("Select Star Types:")
print("1: Drifting")
print("2: Following")
mode_choice = input("Enter 1 or 2: ").strip()

#TO-DO
#uhh we gotta make the actual game where meteors spawn in and you can attack
#rn this isn't bad tho
#maybe make a background or at least more effects since this looks boring
# make it scale when you fullscreen and stuff
#look for bugs and such
#fade in fade out for the engine thrusted
#WE LOVE DRIFTING MECHANICS
#Point score S tier whatever maybe boosts and power ups if you do good
#oh yeah also catch up mechanics/rubberbanding if they do bad
# make stars different colors maybe and add some more effects

#hold on these star effects are sick i might have to make an exploration or something game
#where instead of teleporting from one side to the other when you cross
#it uses the 1/3/1 rule of screen control that would be nice

width,height = 100,100
rotatespeed = 10
accel = 0.25
drag = 0.92
laserspeed = 4.0
maxprojectiles = 5
meteorspeed = 1.0

#okay so here i probably have to change some stuff
#like the meteorspeed is not individualized for each meteor
#and theres other stuff i gotta change
#levels, special abilities, and powerups?

ship = [width / 2, height / 2, 0.0, 0.0, 90.0]
keys_pressed = set()

ship_shape = np.array([[0, 2], [-1.5, -1.5], [0, -0.5], [1.5, -1.5], [0, 2]])
thruster_shape = np.array([[0, -0.5], [-0.7, -1.5], [0, -3.0], [0.7, -1.5], [0, -0.5]])
# ^ okay this looks kinda trash maybe ill fix later
# i mean maybe not the shape more like
#the way that it appears and disappears

num_stars = 40
stars_x = np.random.uniform(0, width, num_stars)

if mode_choice == "2":
    stars_y = np.random.uniform(1, height-1, num_stars)
    star_speeds = np.random.uniform(0.5, 1.5, num_stars)
else:
    stars_y = np.random.uniform(1, height-1, num_stars)
    star_speeds = np.random.uniform(0.1, 0.4, num_stars)

fig, ax = plt.subplots(figsize=(6, 6), facecolor='black')
ax.set_facecolor('black')
ax.set_xlim(0, width)
ax.set_ylim(0, height)

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

stars_plot = ax.scatter(stars_x, stars_y, c='white', s=np.random.uniform(1, 4, num_stars), alpha=0.6, clip_on=True)
thruster_plot, = ax.plot([], [], color='magenta', lw=1.5, alpha=0.8, clip_on=True)
ship_plot, = ax.plot([], [], color='cyan', lw=2, clip_on=True)

def on_key_press(event):
    keys_pressed.add(event.key)

def on_key_release(event):
    keys_pressed.discard(event.key)

fig.canvas.mpl_connect('key_press_event', on_key_press)
fig.canvas.mpl_connect('key_release_event', on_key_release)

def update_game(frame):
    global ship, stars_x, stars_y
    
    if 'left' in keys_pressed:
        ship[4] += rotatespeed
    if 'right' in keys_pressed:
        ship[4] -= rotatespeed
    if 'up' in keys_pressed:
        angle_rad = np.radians(ship[4])
        ship[2] += np.cos(angle_rad) * accel
        ship[3] += np.sin(angle_rad) * accel

    ship[2] *= drag
    ship[3] *= drag
    ship[0] = (ship[0] + ship[2]) % width
    ship[1] = (ship[1] + ship[3]) % height

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
        stars_plot.set_offsets(np.c_[stars_x, stars_y])
    else:
        stars_y -= star_speeds
        stars_y %= height
        stars_plot.set_offsets(np.c_[stars_x, stars_y])

    rad = np.radians(ship[4] - 90)
    c, s = np.cos(rad), np.sin(rad)
    rot_matrix = np.array([[c, -s], [s, c]])

    if 'up' in keys_pressed:
        flicker_scale = np.random.uniform(0.7, 1.3)
        current_thruster = thruster_shape.copy()
        current_thruster[:, 1] *= flicker_scale
        rot_thruster = current_thruster @ rot_matrix.T
        thruster_plot.set_data(rot_thruster[:, 0] + ship[0], rot_thruster[:, 1] + ship[1])
        thruster_plot.set_visible(True)
    else:
        thruster_plot.set_visible(False)

    transformed_shape = ship_shape @ rot_matrix.T
    ship_plot.set_data(transformed_shape[:, 0] + ship[0], transformed_shape[:, 1] + ship[1])
    return [stars_plot, thruster_plot, ship_plot]

def init_game():
    stars_plot.set_offsets(np.empty((0, 2)))
    thruster_plot.set_data([], [])
    ship_plot.set_data([], [])
    return [stars_plot, thruster_plot, ship_plot]

ani = animation.FuncAnimation(fig, update_game, init_func=init_game, interval=33, blit=True, cache_frame_data=False)

print("Press Arrow Keys to Fly")

# i gotta change this message at some point

plt.show()


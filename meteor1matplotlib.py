import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation

#TO-DO
#uhh we gotta make the actual game where meteors spawn in and you can attack
#rn this isn't bad tho
#maybe make a background since this looks boring

width,height = 100,100
rotatespeed = 10
accel = 0.25
drag = 0.98
laserspeed = 4.0
maxprojectiles = 5
meteorspeed = 1.0

ship = [width / 2, height / 2, 0.0, 0.0, 90.0]
keys_pressed = set()

ship_shape = np.array([[0, 2], [-1.5, -1.5], [0, -0.5], [1.5, -1.5], [0, 2]])

fig, ax = plt.subplots(figsize=(6, 6), facecolor='black')
ax.set_facecolor('black')
ax.set_xlim(0, width)
ax.set_ylim(0, height)

ship_plot, = ax.plot([], [], color='cyan', lw=2)

def on_key_press(event):
    keys_pressed.add(event.key)

def on_key_release(event):
    keys_pressed.discard(event.key)

fig.canvas.mpl_connect('key_press_event', on_key_press)
fig.canvas.mpl_connect('key_release_event', on_key_release)

def update_game(frame):
    global ship
    
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

    rad = np.radians(ship[4] - 90)
    c, s = np.cos(rad), np.sin(rad)
    rot_matrix = np.array([[c, -s], [s, c]])
    transformed_shape = ship_shape @ rot_matrix.T
    ship_plot.set_data(transformed_shape[:, 0] + ship[0], transformed_shape[:, 1] + ship[1])
    return [ship_plot]

ani = animation.FuncAnimation(fig, update_game, interval=33, blit=True, cache_frame_data=False)

print("Press Arrow Keys to Fly")
# i gotta change this message
plt.show()

# -*- coding: utf-8 -*-
"""
Created on Fri Jun  2 12:05:15 2017

@author: p000495138
"""

import matplotlib.pyplot as plt
import numpy as np
import time

x = np.arange(0, 2*np.pi, 0.1)
y = np.sin(x)

fig, axes = plt.subplots(nrows=6)

fig.show()

# We need to draw the canvas before we start animating...
fig.canvas.draw()

styles = ['r-', 'g-', 'y-', 'm-', 'k-', 'c-']
def plot(ax, style):
    return ax.plot(x, y, style, animated=True)[0]
lines = [plot(ax, style) for ax, style in zip(axes, styles)]

# Let's capture the background of the figure
backgrounds = [fig.canvas.copy_from_bbox(ax.bbox) for ax in axes]

tstart = time.time()
for i in range(1, 2000):
    items = enumerate(zip(lines, axes, backgrounds), start=1)
    for j, (line, ax, background) in items:
        fig.canvas.restore_region(background)
        line.set_ydata(np.sin(j*x + i/10.0))
        ax.draw_artist(line)
        fig.canvas.blit(ax.bbox)
        time.sleep(0.001)

print('FPS:' , 2000/(time.time()-tstart))

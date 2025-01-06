import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider, TextBox

# Data
x = np.array([0.5, 1.5, 2.5])
y = np.array([0.5, 1.5, 2.5])

fig, ax = plt.subplots()
plt.subplots_adjust(bottom=0.35)  # Adjust space for widgets

sc = ax.scatter(x, y, s=100)  # Initial point size is 100

dragging_point = None

# Drag-and-drop event handlers
def on_press(event):
    global dragging_point
    if event.inaxes != ax:
        return
    distances = np.hypot(x - event.xdata, y - event.ydata)
    dragging_point = np.argmin(distances) if np.min(distances) < 0.1 else None

def on_motion(event):
    global dragging_point
    if dragging_point is None or event.inaxes != ax:
        return
    x[dragging_point], y[dragging_point] = event.xdata, event.ydata
    sc.set_offsets(np.c_[x, y])
    fig.canvas.draw_idle()

def on_release(event):
    global dragging_point
    dragging_point = None

# Connect drag-and-drop events
fig.canvas.mpl_connect('button_press_event', on_press)
fig.canvas.mpl_connect('motion_notify_event', on_motion)
fig.canvas.mpl_connect('button_release_event', on_release)

# Slider for point size
ax_slider = plt.axes([0.25, 0.15, 0.65, 0.03])  # Position: [left, bottom, width, height]
slider = Slider(ax_slider, 'Point Size', 10, 200, valinit=100)

def update_size(val):
    sc.set_sizes([slider.val] * len(x))
    fig.canvas.draw_idle()

slider.on_changed(update_size)

# TextBox for numerical input
ax_textbox = plt.axes([0.25, 0.05, 0.3, 0.05])  # Position: [left, bottom, width, height]
textbox = TextBox(ax_textbox, 'Set X:')

def submit_text(value):
    try:
        num = float(value)
        if dragging_point is not None:
            x[dragging_point] = num
            sc.set_offsets(np.c_[x, y])
            fig.canvas.draw_idle()
    except ValueError:
        print("Invalid input. Please enter a number.")

textbox.on_submit(submit_text)

plt.show()

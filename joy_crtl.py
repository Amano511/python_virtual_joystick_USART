import tkinter as tk
import serial
import threading
import time

# 串口初始化
ser = serial.Serial('COM10', 9600, timeout=0.1)

# 摇杆初始值
rocker_lx = 126
rocker_ly = 126
rocker_rx = 126
rocker_ry = 126

# 窗口设置
root = tk.Tk()
root.title("虚拟双摇杆控制器")
root.geometry("500x300")

canvas = tk.Canvas(root, width=500, height=300, bg="white")
canvas.pack()

# 左摇杆绘制参数
left_center = (125, 150)
right_center = (375, 150)
radius = 50
handle_radius = 10

# 画出底圈
canvas.create_oval(left_center[0]-radius, left_center[1]-radius, left_center[0]+radius, left_center[1]+radius, outline="gray")
canvas.create_oval(right_center[0]-radius, right_center[1]-radius, right_center[0]+radius, right_center[1]+radius, outline="gray")

# 摇杆小球
left_handle = canvas.create_oval(left_center[0]-handle_radius, left_center[1]-handle_radius, left_center[0]+handle_radius, left_center[1]+handle_radius, fill="blue")
right_handle = canvas.create_oval(right_center[0]-handle_radius, right_center[1]-handle_radius, right_center[0]+handle_radius, right_center[1]+handle_radius, fill="green")

# 用于标记按住的摇杆（None, 'left', 'right'）
dragging = None

def update_rocker_value(center, x, y):
    dx = x - center[0]
    dy = center[1] - y  # Y方向反过来
    dx = max(-radius, min(radius, dx))
    dy = max(-radius, min(radius, dy))
    lx = int(126 + (dx / radius) * 129)
    ly = int(126 + (dy / radius) * 129)
    lx = max(0, min(255, lx))
    ly = max(0, min(255, ly))
    return lx, ly

def move_handle(handle, center, x, y):
    dx = x - center[0]
    dy = y - center[1]
    dx = max(-radius, min(radius, dx))
    dy = max(-radius, min(radius, dy))
    canvas.coords(handle, center[0]+dx-handle_radius, center[1]+dy-handle_radius, center[0]+dx+handle_radius, center[1]+dy+handle_radius)

def on_mouse_down(event):
    global dragging
    if abs(event.x - left_center[0]) < radius and abs(event.y - left_center[1]) < radius:
        dragging = 'left'
    elif abs(event.x - right_center[0]) < radius and abs(event.y - right_center[1]) < radius:
        dragging = 'right'

def on_mouse_move(event):
    global rocker_lx, rocker_ly, rocker_rx, rocker_ry
    if dragging == 'left':
        move_handle(left_handle, left_center, event.x, event.y)
        rocker_lx, rocker_ly = update_rocker_value(left_center, event.x, event.y)
    elif dragging == 'right':
        move_handle(right_handle, right_center, event.x, event.y)
        rocker_rx, rocker_ry = update_rocker_value(right_center, event.x, event.y)

def on_mouse_up(event):
    global dragging, rocker_lx, rocker_ly, rocker_rx, rocker_ry
    if dragging == 'left':
        canvas.coords(left_handle, left_center[0]-handle_radius, left_center[1]-handle_radius, left_center[0]+handle_radius, left_center[1]+handle_radius)
        rocker_lx, rocker_ly = 126, 126
    elif dragging == 'right':
        canvas.coords(right_handle, right_center[0]-handle_radius, right_center[1]-handle_radius, right_center[0]+handle_radius, right_center[1]+handle_radius)
        rocker_rx, rocker_ry = 126, 126
    dragging = None

def send_loop():
    while True:
        packet = bytes([0xCE, 0x00, 0x00, rocker_lx, rocker_ly, rocker_rx, rocker_ry, 0xEC])
        ser.write(packet)
        time.sleep(0.05)

canvas.bind("<Button-1>", on_mouse_down)
canvas.bind("<B1-Motion>", on_mouse_move)
canvas.bind("<ButtonRelease-1>", on_mouse_up)

# 开启线程发送数据
threading.Thread(target=send_loop, daemon=True).start()

root.mainloop()
ser.close()

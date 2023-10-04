# ------------ Package Import ------------

import OpenGL.GL as GL
import glfw
import numpy as np
import random
from copy import deepcopy
from time import sleep

# ------------ Library Import ------------

from libs.transform import *
from itertools import cycle

# ------------ Shape Import --------------

from mesh import *
from linear import *
from sphere import *


class Viewer:
    def __init__(self, width=1600, height=800):
        self.fill_modes = cycle([GL.GL_LINE, GL.GL_POINT, GL.GL_FILL])

        # version hints: create GL windows with >= OpenGL 3.3 and core profile
        glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 3)
        glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 3)
        glfw.window_hint(glfw.OPENGL_FORWARD_COMPAT, GL.GL_TRUE)
        glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)
        glfw.window_hint(glfw.RESIZABLE, True)
        glfw.window_hint(glfw.DEPTH_BITS, 16)
        glfw.window_hint(glfw.DOUBLEBUFFER, True)
        self.win = glfw.create_window(width, height, 'Viewer', None, None)

        # make win's OpenGL context current; no OpenGL calls can happen before
        glfw.make_context_current(self.win)

        # initialize trackball
        self.trackball = Trackball()
        self.mouse = (0, 0)

        # register event handlers
        glfw.set_key_callback(self.win, self.on_key)
        glfw.set_cursor_pos_callback(self.win, self.on_mouse_move)
        glfw.set_scroll_callback(self.win, self.on_scroll)

        # useful message to check OpenGL renderer characteristics
        print('OpenGL', GL.glGetString(GL.GL_VERSION).decode() + ', GLSL',
              GL.glGetString(GL.GL_SHADING_LANGUAGE_VERSION).decode() +
              ', Renderer', GL.glGetString(GL.GL_RENDERER).decode())

        # initialize GL by setting viewport and default render characteristics
        GL.glClearColor(0.5, 0.5, 0.5, 0.1)
        # GL.glEnable(GL.GL_CULL_FACE)   # enable backface culling (Exercise 1)
        # GL.glFrontFace(GL.GL_CCW) # GL_CCW: default

        GL.glEnable(GL.GL_DEPTH_TEST)  # enable depth test (Exercise 1)
        GL.glDepthFunc(GL.GL_LESS)   # GL_LESS: default

        # initially empty list of object to draw
        self.drawables = []
        self.gradient = []
        self.points_line = []
        self.radius = 0

    def run(self):
        """ Main render loop for this OpenGL windows """
        num_frame = 0
        while not glfw.window_should_close(self.win):
            # clear draw buffer
            num_frame = num_frame % int(len(self.points_line)*4/5)
            GL.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT)

            win_size = glfw.get_window_size(self.win)
            view = self.trackball.view_matrix()
            projection = self.trackball.projection_matrix(win_size)

            normal_vec = normalized(vec(-self.gradient[num_frame][0], -self.gradient[num_frame][1], 1))
            trans_matrix = translate(vec((self.points_line[num_frame][0], self.points_line[num_frame][1], self.points_line[num_frame][2])) + self.radius * normal_vec)
            
            if num_frame==0:
                rot_matrix = identity()
            else:
                velo_vec = vec((self.points_line[num_frame][0] - self.points_line[num_frame-1][0], self.points_line[num_frame][1] - self.points_line[num_frame-1][1], self.points_line[num_frame][2] - self.points_line[num_frame-1][2]))
                d = np.linalg.norm(velo_vec)
                rot_axis = normalized(np.cross(normal_vec, velo_vec + self.radius * normal_vec))
                alpha = 360*d/(self.radius*2*np.pi)
                rot_matrix = rotate(rot_axis, alpha) @ rot_matrix
                
            model = trans_matrix @ rot_matrix
            
            # draw our scene objects
            for drawable in self.drawables:
                drawable.draw(projection, view, model)
            
            # flush render commands, and swap draw buffers
            glfw.swap_buffers(self.win)

            # Poll for and process events
            glfw.poll_events()
            
            num_frame += 1
            sleep(0.01)

    def add(self, *drawables):
        """ add objects to draw in this windows """
        self.drawables.extend(drawables)

    def on_key(self, _win, key, _scancode, action, _mods):
        """ 'Q' or 'Escape' quits """
        if action == glfw.PRESS or action == glfw.REPEAT:
            if key == glfw.KEY_ESCAPE or key == glfw.KEY_Q:
                glfw.set_window_should_close(self.win, True)

            if key == glfw.KEY_W:
                GL.glPolygonMode(GL.GL_FRONT_AND_BACK, next(self.fill_modes))

            for drawable in self.drawables:
                if hasattr(drawable, 'key_handler'):
                    drawable.key_handler(key)

    def on_mouse_move(self, win, xpos, ypos):
        """ Rotate on left-click & drag, pan on right-click & drag """
        old = self.mouse
        self.mouse = (xpos, glfw.get_window_size(win)[1] - ypos)
        if glfw.get_mouse_button(win, glfw.MOUSE_BUTTON_LEFT):
            self.trackball.drag(old, self.mouse, glfw.get_window_size(win))
        if glfw.get_mouse_button(win, glfw.MOUSE_BUTTON_RIGHT):
            self.trackball.pan(old, self.mouse)

    def on_scroll(self, win, _deltax, deltay):
        """ Scroll controls the camera distance to trackball center """
        self.trackball.zoom(deltay, glfw.get_window_size(win)[1])



def newpoints(size, numEdge):
    derivative = size/numEdge
    points = []
    
    for i in range(numEdge+1):
        for j in range(numEdge+1):
            points += [[-size/2+derivative*j, size/2-derivative*i, 0]]
    
    return points



def func(points):
    newpoints = []
    meanZ = 0
    
    x, y = symbols("x y")
    expression = sin(x) + cos(y)
    
    for point in points:
        z = expression.subs([(x, point[0]), (y, point[1])])
        meanZ += z
        point[2] = z
        newpoints.append(point)
    meanZ = meanZ / len(newpoints)

    return newpoints, meanZ



def compute_grad(point):
    grad_x = np.cos(point[0])
    grad_y = -np.sin(point[1])
    
    return grad_x, grad_y



def GD(rate):
    points = []
    gradient = []
    x = random.uniform(-1.8, 1.8)
    y = random.uniform(-0.2, 0.2)
    init, dontcare = func([[x, y, 0]])
    points += deepcopy(init)
    last_grad_x=0
    last_grad_y=0
    for i in range(11*round(abs(x)/rate+11*abs(y)/rate)):
        grad_x, grad_y = compute_grad(init[0])
        grad_x = last_grad_x*(1-rate)+grad_x*rate
        grad_y = last_grad_y*(1-rate)+grad_y*rate
        last_grad_x = grad_x
        last_grad_y = grad_y
        gradient += deepcopy([[grad_x, grad_y]])
        init[0][0] = init[0][0]-grad_x
        init[0][1] = init[0][1]-grad_y
        init, dontcare = func(init)
        points += deepcopy(init)
    gradient += [[0, 0]]
    return points, gradient
    


def main(argv):
    viewer = Viewer()
    
    viewer.radius = 0.4
    points = newpoints(15, 70)
    points, meanZ = func(points)
    Plane = Mesh(points, meanZ, 'resources/shaders/phong.vert', 'resources/shaders/phong.frag').setup()
    
    viewer.points_line, viewer.gradient = GD(0.05)
    Line = Linear(viewer.points_line, 'resources/shaders/phong.vert', 'resources/shaders/phong.frag').setup()
    
    Ball = Sphere(viewer.radius, 'resources/shaders/phong_texture.vert', 'resources/shaders/phong_texture.frag').setup()
    
    viewer.add(Plane)
    viewer.add(Line)
    viewer.add(Ball)
    viewer.run() 



if __name__ == '__main__':
    glfw.init()
    main(sys.argv[1:])
    glfw.terminate()

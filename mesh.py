from libs.buffer import *
from libs import transform as T
from libs.shader import *
from utils import *
import ctypes
import glfw
import math
import numpy as np
from sympy import *

def newmesh(points, meanZ):
    vertices, indices, color = points, [], []
    numEdge = sqrt(len(points)) - 1
    
    for vertex in vertices:
        if vertex[2]>meanZ:
            color += [[vertex[2]-meanZ, 0, 0]]
        else:
            color += [[0, meanZ-vertex[2], 0]]
    for j in range(numEdge):
        for i in range(numEdge):
            point = (numEdge+1)*j+i
            indices += [point, point, point+numEdge+1, point+1, point+numEdge+2]
            if i==numEdge-1:
                for k in range(numEdge):
                    indices += [(numEdge+1)*j+(numEdge-k-1), (numEdge+1)*j+(numEdge-k-1)]
    
    vertices = np.array(vertices, dtype=np.float32)
    color = np.array(color, dtype=np.float32)
    indices = np.array(indices, dtype=np.uint32)        
    
    return vertices, indices, color

class Mesh(object):
    def __init__(self, points, meanZ, vert_shader, frag_shader):
        self.vertices, self.indices, self.colors = newmesh(points, meanZ)
        self.normals = generate_normals(self.vertices, self.indices)    

        self.vao = VAO()
        self.shader = Shader(vert_shader, frag_shader)
        self.uma = UManager(self.shader)
        
    def setup(self):
        self.vao.add_vbo(0, self.vertices, ncomponents=3, stride=0, offset=None)
        self.vao.add_vbo(1, self.normals, ncomponents=3, stride=0, offset=None)
        self.vao.add_vbo(2, self.colors, ncomponents=3, stride=0, offset=None)
        
        self.vao.add_ebo(self.indices)

        normalMat = np.identity(4, 'f')
        projection = T.ortho(-0.5, 2.5, -0.5, 1.5, -1, 1)
        modelview = np.identity(4, 'f')

        # Light
        I_light = np.array([
            [0.5, 0.5, 0.5],  # diffuse
            [1.0, 1.0, 1.0],  # specular
            [0.5, 0.5, 0.5]  # ambient
        ], dtype=np.float32).T
        light_pos = np.array([0, 0, -1000], dtype=np.float32)

        # Materials
        K_materials = np.array([
            [0.54,      0.89,       0.63],  # diffuse
            [0.316228,	0.316228,	0.316228],  # specular
            [0.135,	    0.2225,	    0.1575]  # ambient
        ], dtype=np.float32).T
        
        shininess = 200.0
        mode = 2

        GL.glUseProgram(self.shader.render_idx)
        self.uma.upload_uniform_matrix4fv(normalMat, 'normalMat', True)
        self.uma.upload_uniform_matrix4fv(projection, 'projection', True)
        self.uma.upload_uniform_matrix4fv(modelview, 'modelview', True)

        self.uma.upload_uniform_matrix3fv(I_light, 'I_light', False)
        self.uma.upload_uniform_vector3fv(light_pos, 'light_pos')

        self.uma.upload_uniform_matrix3fv(K_materials, 'K_materials', False)
        self.uma.upload_uniform_scalar1f(shininess, 'shininess')
        self.uma.upload_uniform_scalar1i(mode, 'mode')
        
        return self

    def draw(self, projection, view, model):
        GL.glUseProgram(self.shader.render_idx)
        modelview = view

        self.uma.upload_uniform_matrix4fv(projection, 'projection', True)
        self.uma.upload_uniform_matrix4fv(modelview, 'modelview', True)
        self.uma.upload_uniform_matrix4fv(view, 'normalMat', True)

        self.vao.activate()
        GL.glDrawElements(GL.GL_TRIANGLE_STRIP,
                          self.indices.shape[0], GL.GL_UNSIGNED_INT, None)

    def key_handler(self, key):

        if key == glfw.KEY_1:
            self.selected_texture = 1
        if key == glfw.KEY_2:
            self.selected_texture = 2
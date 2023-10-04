from libs.buffer import *
from libs import transform as T
from libs.shader import *
from utils import *
import ctypes
import glfw
import math
import numpy as np

def rotation_matrix(axis, angle):
    """
    Calculate rotation matrix for rotation around an arbitrary axis.
    :param axis: 3D vector representing the axis of rotation
    :param angle: Angle of rotation in radians
    :return: 3x3 rotation matrix
    """
    # Normalize the axis vector
    axis = np.asarray(axis)
    axis = axis / np.linalg.norm(axis)
    print(axis)

    # Calculate the skew-symmetric matrix of the axis vector
    ux, uy, uz = axis[0][0], axis[0][1], axis[0][2]
    skew_symmetric = np.array([[0, -uz, uy],
                               [uz, 0, -ux],
                               [-uy, ux, 0]])

    # Calculate the rotation matrix using the Rodrigues formula
    cos_theta = np.cos(angle)
    sin_theta = np.sin(angle)
    rotation_matrix = (cos_theta * np.eye(3) +
                       (1 - cos_theta) * np.outer(axis, axis) +
                       sin_theta * skew_symmetric)

    return rotation_matrix



def newsphere1(radius, sides):
    vertices, indices, color, texcoords = [], [], [], []
    for i in range(sides+1):
        for j in range(sides+1):
            theta = np.pi * i / sides
            phi = 2 * np.pi * j / sides
            x = radius * np.sin(theta) * np.cos(phi)
            y = radius * np.sin(theta) * np.sin(phi)
            z = radius * np.cos(theta)
            
            vertices += [[x, y, z]]
            color += [[0, 0, 1]]
            texcoords += [[j / sides, i / sides]]
            
    
    for j in range(sides):
        for i in range(sides):
            point = (sides+1)*j+i
            indices += [point, point+sides+1, point+1, point+sides+2]
            
    vertices = np.array(vertices, dtype=np.float32)
    color = np.array(color, dtype=np.float32)
    indices = np.array(indices, dtype=np.uint32) 
    texcoords = np.array(texcoords, dtype=np.float32)       
    return vertices, indices, color, texcoords


class Sphere(object):
    def __init__(self, radius, vert_shader, frag_shader):   
        self.radius = radius
        self.vertices, self.indices, self.colors, self.texcoords = newsphere1(self.radius, 30)     

        self.normals = generate_normals(self.vertices, self.indices)

        self.vao = VAO()

        self.shader = Shader(vert_shader, frag_shader)
        self.uma = UManager(self.shader)

    def setup(self):
        self.vao.add_vbo(0, self.vertices, ncomponents=3, stride=0, offset=None)
        self.vao.add_vbo(1, self.normals, ncomponents=3, stride=0, offset=None)
        # self.vao.add_vbo(2, self.colors, ncomponents=3, stride=0, offset=None)
        self.vao.add_vbo(3, self.texcoords, ncomponents=2, stride=0, offset=None)
        
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
        
        self.uma.setup_texture('tex1', 'D:/Workplace/Source Code/Python/CG/Assignment/resources/textures/earth.jpg')
        
        return self

    def draw(self, projection, view, model):
        GL.glUseProgram(self.shader.render_idx)
        modelview = view @ model
        
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
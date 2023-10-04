import numpy as np

def generate_normals(vertices, indices):
    normals = np.zeros((len(vertices), 3), dtype=np.float32)
    for i in range(2, len(indices)):
        v1 = vertices[indices[i-2]]
        v2 = vertices[indices[i-1]]
        v3 = vertices[indices[i]]
        normal = np.cross(v2-v1, v3-v1)
        length = np.linalg.norm(normal)
        if length > 0:
            normal /= length
            normals[indices[i-2]] += normal
            normals[indices[i-1]] += normal
            normals[indices[i]] += normal
    # normals /= np.linalg.norm(normals, axis=1).reshape(-1, 1)
    normals_len = np.linalg.norm(normals, axis=1)
    # add small epsilon to avoid division by zero
    normals_len[normals_len == 0] = 1e-7
    normals /= normals_len.reshape(-1, 1)
    return normals

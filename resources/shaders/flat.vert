#version 330 core

// input attribute variable, given per vertex
layout(location = 0) in vec3 position;

void main() {
    gl_Position = vec4(position, 1);
}

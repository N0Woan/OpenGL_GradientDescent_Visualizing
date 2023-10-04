#version 330 core

// input attribute variable, given per vertex
layout(location = 0) in vec3 position;
layout(location = 1) in vec3 color;
layout(location = 2) in vec3 normal;
uniform mat4 projection, modelview, normalMat;
out vec3 normalInterp;
out vec3 vertPos;
out vec3 colorInterp;



void main(){
  colorInterp = color;
  vec4 vertPos4 = modelview * vec4(position, 1.0);
  vertPos = vec3(vertPos4) / vertPos4.w;
  normalInterp = vec3(normalMat * vec4(normal, 0.0));
  gl_Position = projection * vertPos4;
}

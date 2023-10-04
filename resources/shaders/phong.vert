#version 330 core

// input attribute variable, given per vertex
layout(location = 0) in vec3 position;
layout(location = 1) in vec3 normal;
layout(location = 2) in vec3 color;
uniform mat4 projection, modelview;
out vec3 normal_interp;
out vec3 vertPos;
out vec3 colorInterp;



void main(){
  colorInterp = color;
  vec4 vertPos4 = modelview * vec4(position, 1.0);
  vertPos = vec3(vertPos4) / vertPos4.w;

  mat4 normal_matrix = transpose(inverse(modelview));
  normal_interp = vec3(normal_matrix * vec4(normal, 0.0));

  gl_Position = projection * vertPos4;
}

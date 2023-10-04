#version 330 core

precision mediump float;
in vec3 normalInterp;  // Surface normal
in vec3 vertPos;       // Vertex position
in vec3 colorInterp;

uniform mat3 K_materials_1;
uniform mat3 K_materials_2;
uniform mat3 I_light;

uniform int mode;   // Rendering mode
uniform float shininess; // Shininess
uniform vec3 light_pos; // Light position
out vec4 fragColor;
uniform int face;

void main() {
  vec3 N = normalize(normalInterp);
  vec3 L = normalize(light_pos - vertPos);
  vec3 R = reflect(-L, N);      // Reflected light vector
  vec3 V = normalize(-vertPos); // Vector to viewer

  float specAngle = max(dot(R, V), 0.0);
  float specular = pow(specAngle, shininess);
  vec3 g = vec3(max(dot(L, N), 0.0), specular, 1.0);
  vec3 rgb;
  if(face == 1){
    rgb = matrixCompMult(K_materials_1, I_light) * g + 0.0*colorInterp;
  }
  else{
    rgb = matrixCompMult(K_materials_2, I_light) * g + 0.0*colorInterp;
  }

  fragColor = vec4(rgb, 1.0);
}

#version 330
in vec3 positionIn;

uniform mat4 worldToClipTfm;

void main()
{
    gl_Position = worldToClipTfm * vec4(positionIn, 1.0);
}
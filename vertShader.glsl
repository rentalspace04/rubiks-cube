#version 330
in vec3 positionIn;
in vec2 textureCoord;

uniform mat4 worldToClipTfm;

out vec2 v2f_textureCoord;

void main()
{
    v2f_textureCoord = textureCoord;
    gl_Position = worldToClipTfm * vec4(positionIn, 1.0);
}
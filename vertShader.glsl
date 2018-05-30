#version 330
in vec3 positionIn;
in vec2 textureCoord;

uniform mat4 worldToClipTfm;
uniform mat4 modelToView;
uniform mat3 modelToViewNormal;
uniform vec3 squareNormal;

out vec2 v2f_textureCoord;
out vec3 v2f_normal;
out vec3 v2f_viewSpacePosition;

void main()
{
    v2f_normal = normalize(modelToViewNormal * squareNormal);
    v2f_textureCoord = textureCoord;
    gl_Position = worldToClipTfm * vec4(positionIn, 1.0);
    v2f_viewSpacePosition = (modelToView * vec4(positionIn, 1.0)).xyz;
}
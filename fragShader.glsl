#version 330

vec4 getSquareColor(int index) {
    if (index == 1) {
        // White
        return vec4(1.0, 1.0, 1.0, 1.0);
    } else if (index == 2) {
        // Yellow
        return vec4(1.0, 1.0, 0.0, 1.0);
    } else if (index == 3) {
        // Red
        return vec4(1.0, 0.0, 0.0, 1.0);
    } else if (index == 4) {
        // Orange
        return vec4(1.0, 0.5, 0.0, 1.0);
    } else if (index == 5) {
        // Green
        return vec4(0.0, 1.0, 0.2, 1.0);
    } else if (index == 6) {
        // Blue
        return vec4(0.0, 0.0, 1.0, 1.0);
    } else if (index == 7) {
        // Black
        return vec4(0.0, 0.0, 0.0, 1.0);
    }
}

in vec2 v2f_textureCoord;
in vec3 v2f_normal;
in vec3 v2f_viewSpacePosition;

uniform int squareColorIndex;
uniform sampler2D plasticTexture;
uniform vec3 viewSpaceLightPosition;
uniform vec3 lightColourAndIntensity;
uniform vec3 ambientLightColourAndIntensity;

out vec4 fragmentColor;
void main()
{
    vec3 viewSpaceDirToLight = normalize(viewSpaceLightPosition - v2f_viewSpacePosition);
    vec3 viewSpaceNormal = normalize(v2f_normal);
    float incomingIntensity = max(0.0, dot(viewSpaceNormal, viewSpaceDirToLight));
    vec4 textureColor = texture(plasticTexture, v2f_textureCoord);
    fragmentColor = vec4(vec3(incomingIntensity), 1.0);
    //fragmentColor = vec4(v2f_normal, 1.0);//textureColor * getSquareColor(squareColorIndex);
}
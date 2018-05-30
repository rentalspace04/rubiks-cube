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

uniform int squareColorIndex;
uniform sampler2D plasticTexture;

out vec4 fragmentColor;
void main()
{
    vec4 textureColor = texture(plasticTexture, v2f_textureCoord);
    fragmentColor = textureColor * getSquareColor(squareColorIndex);
}
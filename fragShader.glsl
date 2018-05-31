#version 330

float getSpecularExponent(int index) {
    if (index == 7) {
        return 30.0;
    }
    return 10.0;
}

vec3 fresnelSchick(vec3 r0, float cosAngle) {
    return r0 + (vec3(1.0) - r0) * pow(1.0 - cosAngle, 5.0);
}

vec3 getSquareColor(int index) {
    if (index == 1) {
        // White
        return vec3(1.0, 1.0, 1.0);
    } else if (index == 2) {
        // Yellow
        return vec3(1.0, 1.0, 0.0);
    } else if (index == 3) {
        // Red
        return vec3(1.0, 0.0, 0.0);
    } else if (index == 4) {
        // Orange
        return vec3(1.0, 0.5, 0.0);
    } else if (index == 5) {
        // Green
        return vec3(0.0, 1.0, 0.2);
    } else if (index == 6) {
        // Blue
        return vec3(0.0, 0.0, 1.0);
    } else if (index == 7) {
        // Black
        return vec3(0.2, 0.2, 0.2);
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
uniform vec3 materialSpecular;

out vec4 fragmentColor;
void main()
{
    // Get the positions, directions and normals of everything
    vec3 viewSpaceDirToLight = normalize(viewSpaceLightPosition - v2f_viewSpacePosition);
    vec3 viewSpaceNormal = normalize(v2f_normal);
    vec3 viewSpaceDirToEye = normalize(-v2f_viewSpacePosition);
    vec3 halfVector = normalize(viewSpaceDirToEye + viewSpaceDirToLight);
    // Get the incoming light
    float incomingIntensity = max(0.0, dot(viewSpaceNormal, viewSpaceDirToLight));
    vec3 incomingLight = incomingIntensity * lightColourAndIntensity;
    // Work out the colours
    vec3 materialDiffuse = (
        texture(plasticTexture, v2f_textureCoord).xyz * 
        getSquareColor(squareColorIndex)
    );
    float specularNormalizationFactor = (
        (getSpecularExponent(squareColorIndex) + 2.0) / 2.0
    );
    float specularIntensity = (
        specularNormalizationFactor * 
        pow(
            max(0.0, dot(halfVector, viewSpaceNormal)),
            getSpecularExponent(squareColorIndex)
        )
    );
    vec3 fresnelSpecular = fresnelSchick(
        materialSpecular, max(0.0, dot(viewSpaceDirToLight, halfVector))
    );
    vec3 outgoingLight = ((incomingLight + ambientLightColourAndIntensity) * materialDiffuse +
        incomingLight * specularIntensity * fresnelSpecular);

    fragmentColor = vec4(outgoingLight, 1.0);
    //fragmentColor = vec4(v2f_normal, 1.0);//textureColor * getSquareColor(squareColorIndex);
}
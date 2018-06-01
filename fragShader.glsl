#version 330

#define FLOAT_PRECISION 0.0001

// Inputs
in vec2 v2f_textureCoord;
in vec3 v2f_normal;
in vec3 v2f_viewSpacePosition;

// Model to view transform
uniform mat4 modelToView;
uniform vec3 camPos;

// Colour and texture
uniform int squareColorIndex;
uniform sampler2D plasticTexture;

// Light positions and colors
uniform vec3 viewSpaceLightPosition1;
uniform vec3 lightColourAndIntensity1;
uniform vec3 viewSpaceLightPosition2;
uniform vec3 lightColourAndIntensity2;
uniform vec3 viewSpaceLightPosition3;
uniform vec3 lightColourAndIntensity3;
uniform vec3 viewSpaceLightPosition4;
uniform vec3 lightColourAndIntensity4;

// Ambient and Specular Colors
uniform vec3 ambientLightColourAndIntensity;
uniform vec3 materialSpecular;

// Fog constants
uniform vec3 fogColor;
uniform float fogDensityConst;
uniform float fogHeightConst;
uniform float fogMax;

out vec4 fragmentColor;

vec3 addFog(in vec3 colorIn, in float distanceToCamera, in vec3 camPos, in vec3 camToPoint) {
    float fogAmount = (
        fogHeightConst * exp(-camPos.y * fogDensityConst)
        * (1.0 - exp(-distanceToCamera * camToPoint.y * fogDensityConst)) / camToPoint.y
    );
    fogAmount = min(fogAmount, fogMax);
    return mix(colorIn, fogColor, fogAmount);
}

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

bool vec_is_zero(vec3 vector) {
    return vector.x < FLOAT_PRECISION && vector.y < FLOAT_PRECISION && vector.z < FLOAT_PRECISION;
}

vec3 make_shading(vec3 lightPosition, vec3 lightColor) {
    // Get the positions, directions and normals of everything
    vec3 viewSpaceDirToLight = normalize(lightPosition - v2f_viewSpacePosition);
    vec3 viewSpaceNormal = normalize(v2f_normal);
    vec3 viewSpaceDirToEye = normalize(-v2f_viewSpacePosition);
    vec3 halfVector = normalize(viewSpaceDirToEye + viewSpaceDirToLight);
    // Get the incoming light
    float incomingIntensity = max(0.0, dot(viewSpaceNormal, viewSpaceDirToLight));
    vec3 incomingLight = incomingIntensity * lightColor;
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
    vec3 outgoingLight = (incomingLight * materialDiffuse + incomingLight * specularIntensity * fresnelSpecular);
    return outgoingLight;
}

void main()
{
    vec3 light1 = make_shading(viewSpaceLightPosition1, lightColourAndIntensity1);
    vec3 light2 = make_shading(viewSpaceLightPosition2, lightColourAndIntensity2);
    vec3 light3 = make_shading(viewSpaceLightPosition3, lightColourAndIntensity3);
    vec3 light4 = make_shading(viewSpaceLightPosition4, lightColourAndIntensity4);
    vec3 materialDiffuse = (
        texture(plasticTexture, v2f_textureCoord).xyz * 
        getSquareColor(squareColorIndex)
    );
    vec3 ambient = materialDiffuse * ambientLightColourAndIntensity;

    float distanceToCamera = length(v2f_viewSpacePosition);

    vec3 viewCamPos = (modelToView * vec4(camPos, 1.0)).xyz;

    vec3 outgoingLight = light1 + light2 + light3 + light4 + ambient;
    outgoingLight = addFog(outgoingLight, distanceToCamera, viewCamPos, v2f_viewSpacePosition);
    fragmentColor = vec4(outgoingLight, 1.0);
    //fragmentColor = vec4(v2f_normal, 1.0);//textureColor * getSquareColor(squareColorIndex);
}
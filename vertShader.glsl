#version 330
in vec3 ndcPositionAttr;

void main()
{
    gl_Position = vec4(ndcPositionAttr, 1.0);
}
#version 330 core

uniform sampler2D tex;
uniform float time;

in vec2 fragTexCoord;
out vec4 f_color;

void main() {

    float vignette_strength = 0.5;

    // Get the original color from the texture
    vec4 color = texture(tex, fragTexCoord);

    // Normalize coordinates (0,0) -> (-1,-1) and (1,1) at the corners
    vec2 uv = fragTexCoord * 2.0 - 1.0;

    // Compute vignette factor based on distance from center
    float dist = length(uv);  // Distance from center (0 at center, ~1.4 at corners)
    float vignette = smoothstep(1.0, 0.0, dist * vignette_strength);

    f_color = vec4(color.rgb * vignette, color.a);
}
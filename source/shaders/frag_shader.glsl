#version 330 core

#define NUM_LIGHTS 50  // Max number of lights

uniform sampler2D gameTex;
uniform sampler2D uiTex;
uniform float time;

// Light Sources:
uniform vec2 lightPositions[NUM_LIGHTS];
uniform vec3 lightColors[NUM_LIGHTS];
uniform float lightIntensities[NUM_LIGHTS];

in vec2 fragTexCoord;
out vec4 f_color;

void main() {

    vec4 baseColor = texture(gameTex, fragTexCoord);
    vec3 finalLight = vec3(0.0);  // Start with darkness

    for (int i = 0; i < NUM_LIGHTS; i++) {
        vec2 lightDir = lightPositions[i] - fragTexCoord;
        float distance = length(lightDir);

        // Attenuation (inverse square law or smoothstep for softer falloff)
        float attenuation = lightIntensities[i] / (1.0 + distance * distance);

        // Light contribution
        finalLight += lightColors[i] * attenuation;
    }

    // Apply lighting to the base texture color
    f_color = vec4(baseColor.rgb * finalLight, baseColor.a);

    float vignette_strength = 0.5;
    float intensity = lightIntensities[0];
    vec2 pos = lightPositions[0];

    // Get the original color from the texture
    vec4 color = texture(gameTex, fragTexCoord);
    vec4 uiColor = texture(uiTex, fragTexCoord);

    // Normalize coordinates (0,0) -> (-1,-1) and (1,1) at the corners
    vec2 uv = fragTexCoord * 2.0 - 1.0;


    // Compute vignette factor based on distance from center
    float dist = length(uv);  // Distance from center (0 at center, ~1.4 at corners)
    float vignette = smoothstep(1.0, 0.0, dist * vignette_strength);

    vec4 gameColor = vec4(color.rgb * vignette, color.a);






    // Use UI or Game color, return
    if (length(uiColor) > 0.1) {
        f_color = uiColor;
    } else {
        f_color = gameColor;
    }
}
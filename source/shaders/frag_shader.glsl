#version 330 core

#define NUM_LIGHTS 50  // Max number of lights
#define VIGNETTE_STRENGTH 0.7

#define SCREEN_WIDTH 320.0
#define SCREEN_HEIGHT 180.0

uniform sampler2D gameTex;
uniform sampler2D uiTex;
uniform float time;

uniform vec2 cameraPos;

// Light Sources:
uniform vec2 lightPositions[NUM_LIGHTS];
uniform vec3 lightColors[NUM_LIGHTS];
uniform float lightIntensities[NUM_LIGHTS];

in vec2 fragTexCoord;
out vec4 f_color;

vec2 getWorldPos() {
    vec2 screenPos = vec2(fragTexCoord.x * SCREEN_WIDTH, fragTexCoord.y * SCREEN_HEIGHT);
    vec2 worldPos = cameraPos + screenPos;
    return worldPos;
}

vec2 getFragPos(vec2 _worldPos) {
    return vec2((_worldPos.x - cameraPos.x) / SCREEN_WIDTH,
                (_worldPos.y - cameraPos.y) / SCREEN_HEIGHT);
}

float getLight() {
    vec3 finalLight = vec3(0.3);

    for (int i = 0; i < NUM_LIGHTS; i++) {
        vec2 lightDir = lightPositions[i] - getWorldPos();
        float distance = length(lightDir);

        // Smoothstep falloff (less harsh than inverse square)
        float attenuation = lightIntensities[i] * smoothstep(40.0, 0.1, distance) * 0.1;

        finalLight += lightColors[i] * attenuation;
    }

    return finalLight;
}

vec4 applyVignette(vec4 baseColor) {
    // Normalize coordinates (0,0) -> (-1,-1) and (1,1) at the corners
    vec2 uv = fragTexCoord * 2.0 - 1.0;

    // Compute vignette factor based on distance from center
    float dist = length(uv);  // Distance from center (0 at center, ~1.4 at corners)
    float vignette = smoothstep(1.0, 0.0, dist * VIGNETTE_STRENGTH);

    baseColor = vec4(baseColor.rgb * vignette, baseColor.a);

    return baseColor;
}


void main() {

    vec4 baseColor = texture(gameTex, fragTexCoord);
    vec4 uiColor = texture(uiTex, fragTexCoord);

    // Apply lighting to the base texture color
    vec4 gameColor = vec4(baseColor.rgb * getLight(), baseColor.a);

    // Apply vignette
    gameColor = applyVignette(gameColor);


    // Use UI or Game color, return
    if (length(uiColor) > 0.1) {
        f_color = uiColor;
    } else {
        f_color = gameColor;
    }
}
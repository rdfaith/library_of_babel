#version 330 core

#define NUM_LIGHTS 50  // Max number of lights
#define VIGNETTE_STRENGTH 0.7

#define SCREEN_WIDTH 320.0
#define SCREEN_HEIGHT 180.0

uniform sampler2D gameTex;
//uniform sampler2D gameNormal;
uniform sampler2D uiTex;
uniform sampler2D bg0Tex; // Parallax background (moon sky)
uniform sampler2D bg1Tex; // Parallax background (wall windows)
uniform sampler2D bg2Tex; // Parallax background (columns)
uniform sampler2D bg3Tex; // Parallax background (shelves)

uniform float time;
uniform float moonLightIntensity;
uniform ivec2 moonPosition;

uniform bool lightDebugMode;

uniform vec2 cameraPos;

// Light Sources:
uniform vec2 lightPositions[NUM_LIGHTS];
uniform vec3 lightColors[NUM_LIGHTS];
uniform float lightIntensities[NUM_LIGHTS];
uniform float lightRadii[NUM_LIGHTS];

in vec2 fragTexCoord;
out vec4 f_color;

vec2 getWorldPos(vec2 uvCoord) {
    vec2 screenPos = vec2(uvCoord.x * SCREEN_WIDTH, uvCoord.y * SCREEN_HEIGHT);
    vec2 worldPos = cameraPos + screenPos;
    return worldPos;
}

vec2 getFragPos(vec2 _worldPos) {
    return vec2((_worldPos.x - cameraPos.x) / SCREEN_WIDTH,
                (_worldPos.y - cameraPos.y) / SCREEN_HEIGHT);
}

vec3 getLight(vec2 worldPos) {
    vec3 finalLight = vec3(0.05, 0.28, 0.32) * moonLightIntensity; // Base ambient moonlight

    for (int i = 0; i < NUM_LIGHTS; i++) {
        vec2 lightDir = lightPositions[i] - worldPos;
        float distance = length(lightDir);
        vec3 lightVec = normalize(vec3(lightDir, 1.0)); // Convert to 3D vector

        // Compute normal influence (Lambertian reflection)
//        float NdotL = max(dot(normal, lightVec), 0.0);

        // Smoothstep falloff (soft edge falloff)
        float attenuation = lightIntensities[i] * smoothstep(lightRadii[i], 0.1, distance) * 0.1;

        finalLight += lightColors[i] * attenuation; // * NdotL; // Apply normal influence
    }

    return finalLight;
}

vec4 applyVignette(vec4 baseColor, vec2 uv) {

    // Compute vignette factor based on distance from center
    float dist = length(uv);  // Distance from center (0 at center, ~1.4 at corners)
    float vignette = smoothstep(1.0, 0.0, dist * VIGNETTE_STRENGTH);

    baseColor = vec4(baseColor.rgb * vignette, baseColor.a);

    return baseColor;
}

vec4 addLayerColor(vec4 lowerLayerCol, vec4 higherLayerCol) {
    return higherLayerCol * higherLayerCol.a + lowerLayerCol * (1.0 - higherLayerCol.a);
}

vec4 getParallaxLayersAt(vec2 texCoord) {

    vec4 bg1 = texture(bg1Tex, texCoord);
    vec4 bg2 = texture(bg2Tex, texCoord);
    vec4 bg3 = texture(bg3Tex, texCoord);
    vec4 gameColor = texture(gameTex, texCoord);

    // Add parallax bgs on top of each other
    vec4 parallaxBG = addLayerColor(bg1, bg2);
    parallaxBG = addLayerColor(parallaxBG, bg3);
    parallaxBG = addLayerColor(parallaxBG, gameColor);

    return parallaxBG;
}

ivec2 uvToPixel(vec2 uv) {
    return ivec2(uv.x * 320.0, uv.y * 180.0);
}

vec2 pixelToUV(ivec2 pixel) {
    return vec2(pixel.x / 320.0, pixel.y / 180.0);
}

vec3 quantizeColor(vec3 color, int levels) {
    float factor = float(levels - 1);
    return floor(color * factor + 0.5) / factor;
}

float quantizeLighting(float intensity, int levels) {
    float step = 1.0 / float(levels);
    return floor(intensity / step + 0.5) * step;
}

void main() {

    // Normalize coordinates (0,0) -> (-1,-1) and (1,1) at the corners
    vec2 uv = fragTexCoord * 2.0 - 1.0;

    // Get World Position
    vec2 fragCoords = pixelToUV(uvToPixel(fragTexCoord)); // clamped to nearest pixel for pixel perfect
    vec2 worldPos = getWorldPos(fragCoords);

    vec4 bg0 = texture(bg0Tex, fragTexCoord);
    vec4 bg1 = texture(bg1Tex, fragTexCoord);
    vec4 bg2 = texture(bg2Tex, fragTexCoord);
    vec4 bg3 = texture(bg3Tex, fragTexCoord);

    vec4 gameColor = texture(gameTex, fragTexCoord);
    vec4 uiColor = texture(uiTex, fragTexCoord);

    vec4 color = vec4(0.0);


    vec4 onlyLight = vec4(0.5, 0.5, 0.5, 1.0);

    vec4 parallaxBG = getParallaxLayersAt(fragTexCoord);
    // Adjust background lighting (general ambient lighting)
    parallaxBG = vec4(parallaxBG.rgb * 0.3 * moonLightIntensity, parallaxBG.a);

    // Light rays from moonlight (raymarching)
    vec2 moonPosNormalised = pixelToUV(moonPosition);
    vec2 lightDirection = (fragCoords - moonPosNormalised); // direction for moonlight
    float lightStrength = 0.0;  // Start with no light

    // If the mask is transparent, start raymarching
    if (parallaxBG.a > 0.5) {
        vec2 offset = lightDirection * - 0.005;  // Small step size for the rays
        vec2 pos = fragCoords;

        for (int i = 0; i < 50; i++) {  // March outward in the light direction
            pos += offset;
            if (pos.x < 0.0 || pos.x > 1.0 || pos.y < 0.0 || pos.y > 1.0) break;  // Stop if out of bounds
            lightStrength += (1.0 - getParallaxLayersAt(pos).a) * 0.02;  // Accumulate light
        }
    }

    // Apply the volumetric light effect
    vec3 lightColor = vec3(0.5, 0.8, 0.95);  // Cold moonlight color
    float intensity = 0.3 * moonLightIntensity;
    vec4 finalParallax = vec4(parallaxBG.rgb + lightColor * lightStrength * intensity, parallaxBG.a);

    onlyLight = vec4(onlyLight.rgb + lightColor * lightStrength * intensity, onlyLight.a);

    // Adjust skybox lighting
    bg0 = vec4(bg0.rgb * moonLightIntensity, bg0.a);

    // Add parallax ontop of skybox
    color = addLayerColor(bg0, finalParallax);

    // Do foreground lighting
    //float lighting = quantizeLighting(getLight(worldPos), 8);
    vec3 lighting = getLight(worldPos);
    lighting = quantizeColor(lighting, 8); // quantize lighting levels to 8
    gameColor = vec4(gameColor.rgb * lighting, gameColor.a);

    onlyLight = vec4(onlyLight.rgb * lighting, onlyLight.a);

    // Add foreground ontop of background
    color = addLayerColor(color, gameColor);

    // Add UI on top and return
    f_color = addLayerColor(color, uiColor);

    if (lightDebugMode) f_color = onlyLight;
}
#version 330 core

uniform sampler2D gameTex;
uniform sampler2D uiTex;
uniform float time;

in vec2 fragTexCoord;
out vec4 f_color;

void main() {

    float vignette_strength = 0.5;

    // Get the original color from the texture
    vec4 color = texture(gameTex, fragTexCoord);
    vec4 uiColor = texture(uiTex, fragTexCoord);

    // Normalize coordinates (0,0) -> (-1,-1) and (1,1) at the corners
    vec2 uv = fragTexCoord * 2.0 - 1.0;

    // Compute vignette factor based on distance from center
    float dist = length(uv);  // Distance from center (0 at center, ~1.4 at corners)
    float vignette = smoothstep(1.0, 0.0, dist * vignette_strength);

    vec4 gameColor = vec4(color.rgb * vignette, color.a);

    float ui_alpha = (length(uiColor.rgb) > 0.01) ? 1.0 : 0.0;

    if (length(uiColor) > 0.1) {
        f_color = uiColor;
    } else {
        f_color = gameColor;
    }

    //uiColor = vec4(uiColor.rgb, (uiColor.a > 0.01) ? 0.0 : 1.0);

    // f_color = vec4(gameColor.rgb * gameColor.a + uiColor.rgb * uiColor.a, 1.0);
    // f_color = ((uiColor.a == 0.0) ? gameColor : uiColor);
    // f_color = vec4(mix(gameColor.rgb, uiColor.rgb, uiColor.a), 1.0);
}
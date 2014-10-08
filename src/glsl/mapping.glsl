/*
UV
p : [0, 1]^2

square
p : [-1, 1]^2

disk
p : [-1, 1]^2
|p| < 1

sphere
p : [-1, 1]^3
|p| = 1
*/

float PI = radians(180.0);
float PI_4 = PI / 4.0;

vec2 uvToSquare(vec2 uv) {
  return 2.0 * uv - 1.0;
}

vec2 squareToUV(vec2 onSquare) {
  return 0.5 * onSquare + 0.5;
}

vec2 scrollSquare(vec2 onSquare, vec2 scroll) {
  return mod(onSquare + scroll, 1.0);
}

vec2 squareToDiskPolar(vec2 onSquare) {
  vec2 p = onSquare;
  vec2 r = (p.x > -p.y) ? (
    // region 1 or 2
    (p.x > p.y) ? (
      // region 1, |p.x| > |p.y|
      vec2(p.x, 0.0 + p.y / p.x)
    ) : (
      // region 2, |p.x| < |p.y|
      vec2(p.y, 2.0 - p.x / p.y)
    )
  ) : (
    // region 3 or 4
    (p.x < p.y) ? (
      // region 3, |p.x| >= |p.y|
      vec2(-p.x, 4.0 + p.y / p.x)
    ) : (
      // region 4, |p.x| <= |p.y|
      vec2(-p.y, 6.0 - p.x / p.y)
    )
  );
  return vec2(r.x, PI_4 * mod(r.y, 8.0));
}

vec3 diskPolarToHemisphere(vec2 onDiskPolar) {
  float z = 1.0 - onDiskPolar.x * onDiskPolar.x;
  float r = sqrt(1.0 - z * z);
  float a = onDiskPolar.y;
  return vec3(r * vec2(cos(a), sin(a)), z);
}

vec3 squareToSphere(vec2 onSquare) {
  vec2 a = abs(onSquare);
  float d = a.x + a.y;
  vec3 onDiamond = (d < 1.0) ? (
    vec3(onSquare, 1.0)
  ) : (
    vec3(sign(onSquare) - onSquare, -1.0)
  );
  vec2 onSmallSquare = vec2(onDiamond.x + onDiamond.y, onDiamond.x - onDiamond.y);
  vec2 onDiskPolar = squareToDiskPolar(onSmallSquare);
  vec3 onHemisphere = diskPolarToHemisphere(onDiskPolar);
  return vec3(onHemisphere.xy, onDiamond.z * onHemisphere.z);
}

vec2 ontoPlane(vec3 dir) {
  return dir.xy / dir.z;
}

float grid(float d, float s, vec2 uv) {
  vec2 p = uvToSquare(mod(d * uv, 1.0));
  return 1.0 - pow(p.x, s) - pow(p.y, s);
}

vec4 testCubeMap(vec3 onSphere) {
  vec3 p = abs(onSphere);
  vec3 dir = vec3(0.0);
  vec3 col = vec3(0.0);
  if (p.x >= p.y && p.x >= p.z) {
    dir = vec3(p.y, p.z, p.x);
    col = onSphere.x > 0.0 ? vec3(1.0, 0.0, 0.0) : vec3(0.0, 1.0, 1.0);
  } else if (p.y >= p.x && p.y >= p.z) {
    dir = vec3(p.x, p.z, p.y);
    col = onSphere.y > 0.0 ? vec3(0.0, 1.0, 0.0) : vec3(1.0, 0.0, 1.0);
  } else if (p.z >= p.x && p.z >= p.y) {
    dir = vec3(p.x, p.y, p.z);
    col = onSphere.z > 0.0 ? vec3(0.0, 0.0, 1.0) : vec3(1.0, 1.0, 0.0);
  }
  vec2 uv = ontoPlane(dir);
  return vec4(col * grid(8.0, 6.0, uv), 0.0);
}

void main(void) {
  vec2 uv = gl_FragCoord.xy / iResolution.xy;
  vec2 onSquare = uvToSquare(uv);
  //vec2 onDiskPolar = squareToDiskPolar(onSquare);
  //vec2 onDisk = onDiskPolar.x * vec2(cos(onDiskPolar.y), sin(onDiskPolar.y));
  vec3 onSphere = squareToSphere(onSquare).xzy;
  // rotate view about the Y axis
  float t = 0.25 * PI;//0.1 * iGlobalTime;
  vec2 r = vec2(cos(t), sin(t));
  onSphere = vec3(
    onSphere.x * r.x + onSphere.z * r.y,
    onSphere.y,
    onSphere.x * r.y - onSphere.z * r.x);
  gl_FragColor = testCubeMap(onSphere);
  //gl_FragColor = textureCube(iChannel0, onSphere);
  //gl_FragColor = vec4(0.5 * onSphere + 0.5, 0.0);
  //gl_FragColor = vec4((0.5 * onDiskPolar.y / PI) * grid(8.0, 6.0, onDisk));
}

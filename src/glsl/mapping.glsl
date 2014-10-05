/*
square
p : [0, 1]^2

centered square
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

vec2 squareToCenteredSquare(vec2 onSquare) {
  return 2.0 * onSquare - 1.0;
}

vec2 scrollSquare(vec2 onSquare, vec2 scroll) {
  return mod(onSquare + scroll, 1.0);
}

vec2 squareToDiskPolar(vec2 onSquare) {
  vec2 p = squareToCenteredSquare(onSquare);
  vec2 foo = (p.x > -p.y) ? (
    // region 1 or 2
    (p.x > p.y) ? (
      // region 1, |p.x| > |p.y|
      vec2(p.x, PI_4 * (0.0 + (p.y / p.x)))
    ) : (
      // region 2, |p.x| < |p.y|
      vec2(p.y, PI_4 * (2.0 - (p.x / p.y)))
    )
  ) : (
    // region 3 or 4
    (p.x < p.y) ? (
      // region 3, |p.x| >= |p.y|
      vec2(-p.x, PI_4 * (4.0 + (p.y / p.x)))
    ) : (
      // region 4, |p.x| <= |p.y|
      vec2(-p.y, PI_4 * (6.0 - (p.x / p.y)))
    )
  );
  vec2 q = foo.x * vec2(cos(foo.y), sin(foo.y));
  return vec2(length(q), atan(q.y, q.x) + PI);
}

vec3 diskPolarToHemisphere(vec2 onDiskPolar) {
  float z = 1.0 - onDiskPolar.x * onDiskPolar.x;
  float r = sqrt(1.0 - z * z);
  float a = onDiskPolar.y;
  return vec3(r * vec2(cos(a), sin(a)), z);
}

vec3 diskPolarToSphere(vec2 onDiskPolar) {
  float r = onDiskPolar.x;
  float a = onDiskPolar.y;
  vec3 foo = (a < PI) ?
    diskPolarToHemisphere(vec2(r, 2.0 * a)) :
    diskPolarToHemisphere(vec2(r, 2.0 * (2.0 * PI - a)));
  if (a > PI) {
    foo.z = -foo.z;
  }
  return foo;
}

vec3 squareToSphere(vec2 onSquare) {
  vec2 onScrolledSquare = scrollSquare(onSquare, vec2(0.0, 0.5));
  vec2 onDiskPolar = squareToDiskPolar(onScrolledSquare);
  return diskPolarToSphere(onDiskPolar);
}

vec2 ontoPlane(vec3 dir) {
  return dir.xy / dir.z;
}

float grid(float d, float s, vec2 uv) {
  vec2 p = squareToCenteredSquare(mod(d * uv, 1.0));
  return 1.0 - pow(p.x, s) - pow(p.y, s);
}

vec4 cubeMapFace(vec3 onSphere) {
  vec3 p = abs(onSphere);
  vec3 dir = vec3(0.0);
  vec3 col = vec3(0.0);
  if (p.x >= p.y && p.x >= p.z) {
    dir = vec3(p.y, p.z, p.x);
    col = onSphere.x > 0.0 ? vec3(1.0, 0.0, 0.0) : vec3(0.0, 1.0, 1.0);
  }
  if (p.y >= p.x && p.y >= p.z) {
    dir = vec3(p.x, p.z, p.y);
    col = onSphere.y > 0.0 ? vec3(0.0, 1.0, 0.0) : vec3(1.0, 0.0, 1.0);
  }
  if (p.z >= p.x && p.z >= p.y) {
    dir = vec3(p.x, p.y, p.z);
    col = onSphere.z > 0.0 ? vec3(0.0, 0.0, 1.0) : vec3(1.0, 1.0, 0.0);
  }
  vec2 uv = ontoPlane(dir);
  return vec4(col * grid(8.0, 6.0, uv), 0.0);
}

void main(void) {
  vec2 onSquare = gl_FragCoord.xy / iResolution.xy;
  vec3 onSphere = squareToSphere(onSquare);
  gl_FragColor = cubeMapFace(onSphere.xzy);
  //gl_FragColor = textureCube(iChannel0, onSphere.xzy);
  //gl_FragColor = vec4(0.5 * onSphere + 0.5, 0.0);
}
#include <math.h>
#include <Python.h>

/*
typedef void (*Sampler)(PyArrayInterface*, float[3], float[4]);

void frustum_xp(float t, float u, float out[3]) { out[0] = +1; out[1] = -u; out[2] = -t; }
void frustum_xm(float t, float u, float out[3]) { out[0] = -1; out[1] = -u; out[2] = +t; }
void frustum_yp(float t, float u, float out[3]) { out[0] = +t; out[1] = +1; out[2] = +u; }
void frustum_ym(float t, float u, float out[3]) { out[0] = +t; out[1] = -1; out[2] = -u; }
void frustum_zp(float t, float u, float out[3]) { out[0] = +t; out[1] = -u; out[2] = +1; }
void frustum_zm(float t, float u, float out[3]) { out[0] = -t; out[1] = -u; out[2] = -1; }

(void (*)(float, float, float[3])) frustum[6] = {
  frustum_xp,
  frustum_xm,
  frustum_yp,
  frustum_ym,
  frustum_zp,
  frustum_zm,
};
*/

int cube_map_check(PyObject *py_obj) {
  int ret;
  Py_buffer cube_map;
  ret = PyObject_GetBuffer(py_obj, &cube_map, PyBUF_STRIDED);
  if (ret != 0) { ret = 1; goto exit; }
  if (cube_map.ndim != 4) { ret = 2; goto exit; }
  if (cube_map.itemsize != 4) { ret = 3; goto exit; }
  int face_count = cube_map.shape[0];
  int height = cube_map.shape[1];
  int width = cube_map.shape[2];
  int depth = cube_map.shape[3];
  if (face_count != 6) { ret = 4; goto exit; }
  if (height != width) { ret = 5; goto exit; }
  if (depth != 4) { ret = 6; goto exit; }
exit:
  PyBuffer_Release(&cube_map);
  return ret;
}

/*
void cube_map_assign(PyArrayInterface *cube_map, Sampler sample, PyArrayInterface *sphere) {
  int size = cube_map->shape[1];
  int f_stride = cube_map->strides[0];
  int y_stride = cube_map->strides[1];
  int x_stride = cube_map->strides[2];
  int d_string = cube_map->strides[3];
  data = cube_map->data;
  for (int f = 0; f < 6; f++) {
    for (int y = 0; y < size; y++) {
      for (int x = 0; x < size; x++) {
        float v[3];
        frustum[f](2.0*x/size - 1.0, 2.0*y/size - 1.0, v);
        float s[4];
        int res = sample(sphere, v, s);
        if (res != 0) return 8;
        for (int d = 0; d < 4; d++) {
          *(float*)(data + f*f_stride + y*y_stride + x*x_stride + d*d_stride) = s[d];
        }
      }
    }
  }
  return 0;
}
*/

int equirect_check(PyObject *py_obj) {
  int ret;
  Py_buffer equirect;
  ret = PyObject_GetBuffer(py_obj, &equirect, PyBUF_STRIDED);
  if (ret != 0) { ret = 1; goto exit; }
  if (equirect.ndim != 3) { ret = 2; goto exit; }
  if (equirect.itemsize != 4) { ret = 3; goto exit; }
  int height = equirect.shape[0];
  int width = equirect.shape[1];
  int depth = equirect.shape[2];
  if (width != 2*height) return 4;
  if (depth != 4) return 5;
exit:
  PyBuffer_Release(&equirect);
  return ret;
}

/*
void equirect_sample(PyArrayInterface *sphere, float v[3], float s[4]) {
  int height = equirect->shape[0];
  int width = equirect->shape[1];
  int y_stride = equirect->strides[0];
  int x_stride = equirect->strides[1];
  int d_string = equirect->strides[2];
  float phi = atan2(v[1], v[0]);
  float r = sqrt(v[0]*v[0] + v[1]*v[1] + v[2]*v[2]);
  float theta = arccos(v[2] / r);
  float t = phi/(2*M_PI) + 0.5;
  float u = theta/M_PI;
  int x = t*(width - 1);
  int y = u*(height - 1);
  data = equirect->data;
  for (int d = 0; d < 4; d++) {
    s[d] = *(float*)(data + y*y_stride + x*x_stride + d*d_stride);
  }
}
*/

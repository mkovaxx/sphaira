#include <Python.h>
#include <numpy/arrayobject.h>
#include <math.h>


typedef void (*Sampler)(PyArrayObject* equirect, float* v, float* s);

static PyObject* cube_map_check(PyObject* self, PyObject* args);
static PyObject* equirect_check(PyObject* self, PyObject* args);

static PyObject* cube_map_assign(PyObject* self, PyObject* args);

static PyObject* equirect_get_sampler(PyObject* self, PyObject* args);

static PyMethodDef SphairaFunctions[] = {
  /* check */
  { "cube_map_check", cube_map_check, METH_VARARGS
  , "check if array has the shape of a cube map projection"
  }
, { "equirect_check", equirect_check, METH_VARARGS
  , "check if array has the shape for an equirectangular projection"
  }
  /* assign */
, { "cube_map_assign", cube_map_assign, METH_VARARGS
  , "assign the cube map from an image sphere"
  }
  /* sample */
, { "equirect_get_sampler", equirect_get_sampler, METH_VARARGS
  , "get the sampler for equirectangular projections"
  }
, {NULL, NULL, 0, NULL}
};

static PyObject* cube_map_check(PyObject* self, PyObject* args)
{
  int ret = 0;
  PyArrayObject* cube_map;
  if (!PyArg_ParseTuple(args, "O", &cube_map)) {
    ret = 1; goto exit;
  }
  if (PyArray_Check(cube_map) == 0) {
    ret = 2; goto exit;
  }
  if (PyArray_TYPE(cube_map) != NPY_FLOAT32) {
    ret = 3; goto exit;
  }
  if (PyArray_NDIM(cube_map) != 4) {
    ret = 4; goto exit;
  }
  if (PyArray_DIM(cube_map, 3) != 4) {
    ret = 5; goto exit;
  }
  if (PyArray_DIM(cube_map, 0) != 6) {
    ret = 6; goto exit;
  }
  if (PyArray_DIM(cube_map, 1) != PyArray_DIM(cube_map, 2)) {
    ret = 7; goto exit;
  }
exit:
  return PyInt_FromLong(ret);
}

static PyObject* equirect_check(PyObject* self, PyObject* args)
{
  int ret = 0;
  PyArrayObject* equirect;
  if (!PyArg_ParseTuple(args, "O", &equirect)) {
    ret = 1; goto exit;
  }
  if (PyArray_Check(equirect) == 0) {
    ret = 2; goto exit;
  }
  if (PyArray_TYPE(equirect) != NPY_FLOAT32) {
    ret = 3; goto exit;
  }
  if (PyArray_NDIM(equirect) != 3) {
    ret = 4; goto exit;
  }
  if (PyArray_DIM(equirect, 2) != 4) {
    ret = 5; goto exit;
  }
  if (2*PyArray_DIM(equirect, 0) != PyArray_DIM(equirect, 1)) {
    ret = 6; goto exit;
  }
exit:
  return PyInt_FromLong(ret);
}

static PyObject* cube_map_assign(PyObject* self, PyObject* args)
{
  PyArrayObject* cube_map;
  PyArrayObject* data_sphere;
  PyObject* sampler_cobj;
  if (!PyArg_ParseTuple(args, "OOO", &cube_map, &data_sphere, &sampler_cobj)) {
    return NULL;
  }
  Sampler sampler = PyCObject_AsVoidPtr(sampler_cobj);
  int size = PyArray_DIM(cube_map, 1);
  void* data = PyArray_DATA(cube_map);
  int sf = PyArray_STRIDE(cube_map, 0);
  int sy = PyArray_STRIDE(cube_map, 1);
  int sx = PyArray_STRIDE(cube_map, 2);
  int sd = PyArray_STRIDE(cube_map, 3);
  int f, y, x, d;
  float t;
  float u;
  float v[3];
  float s[4];
  for (f = 0; f < 6; f++) {
    for (y = 0; y < size; y++) {
      for (x = 0; x <  size; x++) {
        t = 2.0*x / size - 1.0;
        u = 2.0*y / size - 1.0;
        switch (f) {
          case 0: v[0] = +1; v[1] = -u; v[2] = -t; break;
          case 1: v[0] = -1; v[1] = -u; v[2] = +t; break;
          case 2: v[0] = +t; v[1] = +1; v[2] = +u; break;
          case 3: v[0] = +t; v[1] = -1; v[2] = -u; break;
          case 4: v[0] = +t; v[1] = -u; v[2] = +1; break;
          case 5: v[0] = -t; v[1] = -u; v[2] = -1; break;
        }
        sampler(data_sphere, v, s);
        for (d = 0; d < 4; d++) {
          *(float*)(data + f*sf + y*sy + x*sx + d*sd) = s[d];
        }
      }
    }
  }
  return Py_None;
}

static void equirect_sample(PyArrayObject* equirect, float* v, float* s) {
  int height = PyArray_DIM(equirect, 0);
  int width = PyArray_DIM(equirect, 1);
  int sy = PyArray_STRIDE(equirect, 0);
  int sx = PyArray_STRIDE(equirect, 1);
  int sd = PyArray_STRIDE(equirect, 2);
  float phi = atan2(v[1], v[0]);
  float r = sqrt(v[0]*v[0] + v[1]*v[1] + v[2]*v[2]);
  float theta = acos(v[2] / r);
  float t = phi/(2*M_PI) + 0.5;
  float u = theta/M_PI;
  int x = t*(width - 1);
  int y = u*(height - 1);
  int d;
  void* data = PyArray_DATA(equirect);
  for (d = 0; d < 4; d++) {
    s[d] = *(float*)(data + y*sy + x*sx + d*sd);
  }
}

static PyObject* equirect_get_sampler(PyObject* self, PyObject* args) {
  return PyCObject_FromVoidPtr(equirect_sample, NULL);
}

/* This initiates the module using the above definitions. */
#if PY_VERSION_HEX >= 0x03000000
static struct PyModuleDef moduledef = {
    PyModuleDef_HEAD_INIT,
    "sphaira",
    NULL,
    -1,
    SphairaFunctions,
    NULL,
    NULL,
    NULL,
    NULL
};

PyMODINIT_FUNC PyInit_external(void)
{
    PyObject *m;
    m = PyModule_Create(&moduledef);
    if (!m) {
        return NULL;
    }
    import_array();
    return m;
}
#else
PyMODINIT_FUNC initexternal(void)
{
    PyObject *m;

    m = Py_InitModule("external", SphairaFunctions);
    if (m == NULL) {
        return;
    }
    import_array();
}
#endif

#include <Python.h>
#include <numpy/arrayobject.h>
#include <math.h>


static PyObject* equirect_check(PyObject* self, PyObject* args);

static PyMethodDef SphairaFunctions[] =
{ { "equirect_check"
  , equirect_check
  , METH_VARARGS
  , "check if array has the shape of an equirectangular image"
  }
, {NULL, NULL, 0, NULL}
};

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

PyMODINIT_FUNC PyInit_sphaira(void)
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
PyMODINIT_FUNC initsphaira(void)
{
    PyObject *m;

    m = Py_InitModule("sphaira", SphairaFunctions);
    if (m == NULL) {
        return;
    }
    import_array();
}
#endif

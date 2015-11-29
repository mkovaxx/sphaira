from __future__ import division
from math import sqrt, sin, cos


class Vec3(object):

    def __init__(self, *xyz):
        (self.x, self.y, self.z) = xyz.__iter__()

    def __iter__(self):
        return (self.x, self.y, self.z).__iter__()

    def __repr__(self):
        return "Vec3(%s)" % (", ".join(str(e) for e in self))

    def fmap(self, f):
        return Vec3(f(self.x), f(self.y), f(self.z))

    def scale(self, s):
        return Vec3(s*self.x, s*self.y, s*self.z)

    def __add__(self, v):
        return Vec3(self.x + v.x, self.y + v.y, self.z + v.z)

    def __sub__(self, v):
        return Vec3(self.x - v.x, self.y - v.y, self.z - v.z)

    def __neg__(self):
        return Vec3(-self.x, -self.y, -self.z)

    def cross(self, v):
        return Vec3(self.y*v.z - self.z*v.y,
                    self.z*v.x - self.x*v.z,
                    self.x*v.y - self.y*v.x)

    def dot(self, v):
        return self.x*v.x + self.y*v.y + self.z*v.z

    def norm(self):
        return sqrt(self.dot(self))

    def unit(self):
        return self.scale(1.0 / self.norm())

    def rotation(self):
        n = self.norm()
        u = self.unit()
        return Quat(cos(n), u.scale(sin(n)))


class Quat(object):

    def __init__(self, *wv):
        (self.w, self.v) = wv.__iter__()

    def __iter__(self):
        return (self.w, self.v).__iter__()

    def __repr__(self):
        return "Quat(%s)" % (", ".join(str(e) for e in self))

    def fmap(self, f):
        return Quat(f(self.w), self.v.fmap(f))

    def scale(self, s):
        return Quat(s*self.w, self.v.scale(s))

    def __add__(self, q):
        return Quat(self.w + q.w, self.v + q.v)

    def __sub__(self, q):
        return Quat(self.w - q.w, self.v - q.v)

    def __neg__(self):
        return Quat(-self.w, -self.v)

    def conj(self):
        return Quat(self.w, -self.v)

    def dot(self, q):
        return self.w*q.w + self.v.dot(q.v)

    def unit(self):
        return self.scale(1 / self.norm())

    def norm(self):
        return sqrt(self.dot(self))

    def __mul__(self, q):
        return Quat(self.w*q.w - self.v.dot(q.v),
                    self.v.scale(q.w) + q.v.scale(self.w) + self.v.cross(q.v))

    def __truediv__(self, q):
        return self * q.conj().unit()

    def matrix(self):
        w = self.w
        (x, y, z) = self.v
	return M3x3(Vec3(w*w+x*x-y*y-z*z, 2 * (x*y + w*z), 2 * (x*z - w*y)),
		    Vec3(2 * (x*y - w*z), w*w-x*x+y*y-z*z, 2 * (y*z + w*x)),
		    Vec3(2 * (x*z + w*y), 2 * (y*z - w*x), w*w-x*x-y*y+z*z))


class M3x3(object):

    def __init__(self, *XYZ):
        (self.X, self.Y, self.Z) = XYZ.__iter__()

    def __iter__(self):
        return (self.X, self.Y, self.Z).__iter__()

    def __repr__(self):
        return "M3x3(%s)" % (", ".join(str(x) for x in self))

    def fmap(self, f):
        return M3x3(self.X.fmap(f), self.Y.fmap(f), self.Z.fmap(f))

    def scale(self, s):
        return M3x3(self.X.scale(s), self.Y.scale(s), self.Z.scale(s))

    def __neg__(self):
        return M3x3(-self.X, -self.Y, -self.Z)

    def __add__(self, m):
        return M3x3(self.X + m.X, self.Y + m.Y, self.Z + m.Z)

    def __sub__(self, m):
        return M3x3(self.X - m.X, self.Y - m.Y, self.Z - m.Z)

    def __call__(self, v):
        return self.X.scale(v.x) + self.Y.scale(v.y) + self.Z.scale(v.z)

    def __mul__(self, m):
        return M3x3(self(m.X), self(m.Y), self(m.Z))

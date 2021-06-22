from ctypes import c_void_p, c_char_p, POINTER, c_int, CFUNCTYPE, cdll, CDLL, py_object, pythonapi, c_bool, c_uint32, \
    c_short, c_ushort, Structure
from types import FunctionType
from typing import TYPE_CHECKING


class Out:
    def __init__(self, ty):
        self.ty = ty


class Errcheck:
    def __init__(self, ty, check=None):
        self.ty = ty
        self.check = check


xlib = CDLL("/usr/lib/x86_64-linux-gnu/libX11.so")
xext = CDLL("/usr/lib/x86_64-linux-gnu/libXext.so.6")

PyCapsule_GetPointer = pythonapi.PyCapsule_GetPointer
PyCapsule_GetPointer.restype = c_void_p
PyCapsule_GetPointer.argtypes = [py_object, c_char_p]


def x_func(lib, func):
    if TYPE_CHECKING:
        return func
    func: FunctionType
    args_types = []
    args_flags = []
    ret = c_int
    check = None
    for name, arg in func.__annotations__.items():
        arg = eval(arg) if isinstance(arg, str) else arg
        if name == "return":
            if isinstance(arg, Errcheck):
                ret = arg.ty
                check = arg.check
            else:
                ret = arg
            continue
        if isinstance(arg, Out):
            t = arg.ty
            f = 2
        else:
            t = arg
            f = 1
        args_types.append(t)
        args_flags.append((f, name))
    prototype = CFUNCTYPE(ret, *args_types)
    f = prototype((func.__name__, lib), tuple(args_flags))
    if check is not None:
        f.errcheck = check
    return f


xlib_func = lambda func: x_func(xlib, func)
xext_func = lambda func: x_func(xext, func)

ShapeBounding = 0

ShapeSet = 0
ShapeUnion = 1
ShapeIntersect = 2
ShapeSubtract = 3
ShapeInvert = 4

@xlib_func
def XSetStandardProperties(
        display: c_void_p,
        w: c_void_p,
        window_name: c_char_p,
        icon_name: c_char_p,
        icon_pixmap: c_void_p,
        argv: POINTER(c_char_p),
        argc: c_int,
        hints: c_void_p
) -> c_int: ...


def errcheck(result, func, args):
    print(result, func, args)
    return (result, args)


@xext_func
def XShapeQueryExtension(
        display: c_void_p,
        event_basep: Out(POINTER(c_int)),
        error_basep: Out(POINTER(c_int)),
) -> Errcheck(c_bool, lambda res, _, args: (res and (args[1].value, args[2].value))): ...


Region = c_uint32


@xext_func
def XCreateRegion() -> Region: ...


class XRectangle(Structure):
    _fields_ = [
        ("x", c_short),
        ("y", c_short),
        ("width", c_ushort),
        ("height", c_ushort),
    ]


@xext_func
def XUnionRectWithRegion(
        rectangle: POINTER(XRectangle),
        src_region: Region,
        dest_region_return: Region
) -> c_int: ...


@xext_func
def XShapeCombineRegion(
        display: c_void_p,
        dest: c_void_p,
        dest_kind: c_int,
        x_off: c_int,
        y_off: c_int,
        region: Region,
        op: c_int,
): ...



def CreateRegion(x, y, w, h):
    rect = XRectangle(x, y, w, h)
    reg = XCreateRegion()
    XUnionRectWithRegion(rect, reg, reg)
    return reg


def CreateFrameRegion(bound, size):
    reg = XCreateRegion()
    rect = XRectangle(0, 0, size[0], bound)
    XUnionRectWithRegion(rect, reg, reg)
    rect = XRectangle(0, size[1] - bound, size[0], bound)
    XUnionRectWithRegion(rect, reg, reg)
    rect = XRectangle(0, 0, bound, size[1])
    XUnionRectWithRegion(rect, reg, reg)
    rect = XRectangle(size[0] - bound, 0, bound, size[1])
    XUnionRectWithRegion(rect, reg, reg)
    return reg

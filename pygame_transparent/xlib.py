from _ctypes import _Pointer
from collections import namedtuple
from ctypes import c_void_p, c_char_p, POINTER, c_int, CFUNCTYPE, cdll, CDLL, py_object, pythonapi, c_bool, c_uint32, \
    c_short, c_ushort, Structure, c_uint
from inspect import signature, Parameter, Signature
from types import FunctionType
from typing import TYPE_CHECKING, no_type_check_decorator, NamedTuple, Type

__all__ = [
    "PyCapsule_GetPointer",

    "XRectangle", "Region",

    "XCreateRegion", "XShapeCombineRegion", "XUnionRectWithRegion", "XSetStandardProperties", "XShapeQueryExtension",
    "CreateRegion", "CreateFrameRegion", "XShapeQueryVersion",

    "ShapeBounding", "ShapeClip", "ShapeSet", "ShapeInvert", "ShapeSubtract", "ShapeIntersect", "ShapeNotifyMask",
    "ShapeNotify", "ShapeInput", "ShapeUnion", "ShapeNumberEvents"
]


class Out:
    def __init__(self, ty):
        self.ty = ty


class Errcheck:
    def __init__(self, ty, check=None):
        self.ty = ty
        self.check = check


import importlib

xlib = CDLL("/usr/lib/x86_64-linux-gnu/libX11.so")
xext = CDLL("/usr/lib/x86_64-linux-gnu/libXext.so.6")

PyCapsule_GetPointer = pythonapi.PyCapsule_GetPointer
PyCapsule_GetPointer.restype = c_void_p
PyCapsule_GetPointer.argtypes = [py_object, c_char_p]


def x_func(lib, func):
    args_types = []
    args_flags = []
    sig = signature(func)
    out_params = {}
    for i, (name, param) in enumerate(sig.parameters.items()):
        if param.kind in (Parameter.POSITIONAL_ONLY, Parameter.POSITIONAL_OR_KEYWORD):
            arg = param.annotation
            if arg is Parameter.empty:
                raise ValueError("All parameters need to have a type annotation")
            if isinstance(arg, str):
                arg = eval(arg)
            if isinstance(arg, Out):
                t = arg.ty
                f = 2
                out_params[i] = name
                assert issubclass(t, _Pointer), t
            else:
                t = arg
                f = 1
            args_types.append(t)
            if param.default is not Parameter.empty:
                args_flags.append((f, name, param.default))
            else:
                args_flags.append((f, name))
        elif param.kind == Parameter.VAR_POSITIONAL:
            raise ValueError("Variadic Parameters are not")
        else:
            raise ValueError("x_func can't have keyword only parameter")

    check = None
    if isinstance(sig.return_annotation, Errcheck):
        ret = sig.return_annotation.ty
        check = sig.return_annotation.check
        if check is None:
            nt = namedtuple(func.__name__ + "Result", out_params.values())

            def check(result, func, args):
                if result:
                    return nt(**{n: args[i].value for i, n in out_params.items()})
                return None

    elif sig.return_annotation is not Signature.empty:
        ret = sig.return_annotation
    else:
        ret = c_int
    prototype = CFUNCTYPE(ret, *args_types)
    f = prototype((func.__name__, lib), tuple(args_flags))
    if check is not None:
        f.errcheck = check
    return f


xlib_func = lambda func: x_func(xlib, func)
xext_func = lambda func: x_func(xext, func)

ShapeSet = 0
ShapeUnion = 1
ShapeIntersect = 2
ShapeSubtract = 3
ShapeInvert = 4

ShapeBounding = 0
ShapeClip = 1
ShapeInput = 2

ShapeNotifyMask = 1 << 0
ShapeNotify = 0
ShapeNumberEvents = ShapeNotify + 1


@xlib_func
def XSetStandardProperties(
        display: c_void_p,
        w: c_void_p,
        window_name: c_char_p = None,
        icon_name: c_char_p = None,
        icon_pixmap: c_void_p = None,
        argv: POINTER(c_char_p) = None,
        argc: c_int = 0,
        hints: c_void_p = None
) -> c_int: ...


def errcheck_namedtuple(ty: Type[NamedTuple]):
    def errcheck_namedtuple(result, func, args):
        if result:
            print(func, ty)
        return args

    return errcheck_namedtuple


@xext_func
def XShapeQueryExtension(
        display: c_void_p,
        event_basep: Out(POINTER(c_int)),
        error_basep: Out(POINTER(c_int)),
) -> Errcheck(c_bool): ...


@xext_func
def XShapeQueryVersion(
        display: c_void_p,
        major_version: Out(POINTER(c_int)),
        minor_version: Out(POINTER(c_int)),
) -> Errcheck(c_bool): ...


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


@xext_func
def XShapeCombineRectangles(
        display: c_void_p,
        dest: c_void_p,
        dest_kind: c_int,
        x_off: c_int,
        y_off: c_int,
        rectangles: POINTER(XRectangle),
        n_rects: c_int,
        op: c_int,
        ordering: c_int,
): ...


@xext_func
def XShapeCombineShape(
        display: c_void_p,
        dest: c_void_p,
        dest_kind: c_int,
        x_off: c_int,
        y_off: c_int,
        src: c_void_p,
        src_kind: c_int,
        op: c_int,
): ...


@xext_func
def XShapeOffsetShape(
        display: c_void_p,
        dest: c_void_p,
        dest_kind: c_int,
        x_off: c_int,
        y_off: c_int,
): ...


@xext_func
def XShapeQueryExtents(
        display: c_void_p,
        dest: c_void_p,
        bounding_shaped: Out(POINTER(c_bool)),
        x_bounding: Out(POINTER(c_int)),
        y_bounding: Out(POINTER(c_int)),
        w_bounding: Out(POINTER(c_uint)),
        h_bounding: Out(POINTER(c_uint)),
        clip_shaped: Out(POINTER(c_bool)),
        x_clip: Out(POINTER(c_int)),
        y_clip: Out(POINTER(c_int)),
        w_clip: Out(POINTER(c_uint)),
        h_clip: Out(POINTER(c_uint)),
) -> Errcheck(c_int, errcheck_namedtuple(None)): ...


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

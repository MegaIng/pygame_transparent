from ctypes import c_void_p, c_char_p, Structure
from typing import Union, Any, NamedTuple

_Ptr = Union[c_void_p, int]
_Str = Union[bytes, c_char_p, _Ptr]

Region = Union[int]


class XRectangle(Structure):
    x: int
    y: int
    width: int
    height: int


def PyCapsule_GetPointer(
        capsule: Any,
        name: _Str
) -> int: ...


def XSetStandardProperties(
        display: _Ptr,
        w: _Ptr,
        window_name: _Str = None,
        icon_name: _Str = None,
        icon_pixmap: _Ptr = None,
        argv: _Ptr = None,
        argc: int = 0,
        hints: _Ptr = None
) -> int: ...


def XShapeQueryExtension(
        display: _Ptr
) -> Union[bool, tuple[int, int]]: ...


def XShapeQueryVersion(
        display: _Ptr
) -> Union[bool, tuple[int, int]]: ...


def XShapeCombineRegion(
        display: _Ptr,
        dest: _Ptr,
        dest_kind: int,
        x_off: int,
        y_off: int,
        region: Region,
        op: int,
): ...


def XShapeCombineRectangles(
        display: _Ptr,
        dest: _Ptr,
        dest_kind: int,
        x_off: int,
        y_off: int,
        rectangles: Union[_Ptr, XRectangle],
        n_rects: int,
        ordering: int,
): ...


def XCreateRegion() -> Region: ...


def XUnionRectWithRegion(
        rectangle: Union[_Ptr, XRectangle],
        src_region: Region,
        dest_region_return: Region
) -> int: ...


class _XShapeQueryExtentsResult(NamedTuple):
    bounding_shaped: bool
    x_bounding: int
    y_bounding: int
    w_bounding: int
    h_bounding: int
    clip_shaped: bool
    x_clip: int
    y_clip: int
    w_clip: int
    h_clip: int


def XShapeQueryExtents(
        display: c_void_p,
        dest: c_void_p,
) -> _XShapeQueryExtentsResult: ...


def CreateRegion(x: int, y: int, w: int, h: int) -> Region: ...


def CreateFrameRegion(bound: int, size: tuple[int, int]) -> Region: ...


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

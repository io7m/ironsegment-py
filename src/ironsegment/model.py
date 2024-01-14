#
# Copyright © 2024 Mark Raynsford <code@io7m.com> https://www.io7m.com
#
# Permission to use, copy, modify, and/or distribute this software for any
# purpose with or without fee is hereby granted, provided that the above
# copyright notice and this permission notice appear in all copies.
#
# THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES
# WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF
# MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY
# SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
# WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN
# ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF OR
# IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.
#

from collections.abc import Mapping
from enum import Enum

MAX_ID_VALUE_INCLUSIVE = 4294967295


class ObjectID:
    _value: int

    def __init__(self, value: int):
        _error = f"IDs must be in the range [1, {MAX_ID_VALUE_INCLUSIVE}]"
        if not value >= 1:
            raise ValueError(_error)
        if not value <= MAX_ID_VALUE_INCLUSIVE:
            raise ValueError(_error)
        self._value = value

    @property
    def value(self) -> int:
        return self._value


class ImageID:
    _value: int

    def __init__(self, value: int):
        _error = f"IDs must be in the range [1, {MAX_ID_VALUE_INCLUSIVE}]"
        if not value >= 1:
            raise ValueError(_error)
        if not value <= MAX_ID_VALUE_INCLUSIVE:
            raise ValueError(_error)
        self._value = value

    @property
    def value(self) -> int:
        return self._value


class ImageSemantic(Enum):
    DENOISE_RGB16 = 0
    DENOISE_RGB8 = 1
    DENOISE_RGBA16 = 2
    DENOISE_RGBA8 = 3
    DEPTH_16 = 4
    DEPTH_32 = 5
    MONOCHROME_LINES_8 = 6
    OBJECT_ID_32 = 7


class Image:
    _identifier: ImageID
    _semantic: ImageSemantic

    def __init__(self, identifier: ImageID, semantic: ImageSemantic):
        self._identifier = identifier
        self._semantic = semantic

    @property
    def identifier(self) -> ImageID:
        return self._identifier

    @property
    def semantic(self) -> ImageSemantic:
        return self._semantic


class Object:
    _identifier: ObjectID
    _description: str

    def __init__(self, identifier: ObjectID, description: str):
        self._identifier = identifier
        self._description = description

    @property
    def identifier(self) -> ObjectID:
        return self._identifier

    @property
    def description(self) -> str:
        return self._description


class Images:
    _width: int
    _height: int
    _images: Mapping[int, Image]

    def __init__(self, width: int, height: int, images: Mapping[int, Image]):
        self._width = width
        self._height = height
        self._images = images

    @property
    def width(self) -> int:
        return self._width

    @property
    def height(self) -> int:
        return self._height

    @property
    def images(self) -> Mapping[int, Image]:
        return self._images


class Manifest:
    _images: Images
    _objects: Mapping[int, Object]
    _metadata: Mapping[str, str]

    def __init__(self, images: Images, objects: Mapping[int, Object], metadata: Mapping[str, str]):
        self._images = images
        self._objects = objects
        self._metadata = metadata

    @property
    def images(self) -> Images:
        return self._images

    @property
    def objects(self) -> Mapping[int, Object]:
        return self._objects

    @property
    def metadata(self) -> Mapping[str, str]:
        return self._metadata

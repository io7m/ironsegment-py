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

import math
import mmap
from abc import ABC, abstractmethod
from struct import pack, unpack
from typing import IO, Any, Literal

import numpy as np

from ironsegment.model import (
    ImageID,
    ImageSemantic,
    Manifest,
    pixel_size_for_semantic,
)
from ironsegment.xml import parse_manifest, serialize_manifest

FILE_MAGIC_NUMBER = 0x894972530D0A1A0A


class FileReadableSection1(ABC):
    def __init__(
        self, data_map: mmap.mmap, section_type: int, offset: int, size: int
    ):
        self._map = data_map
        self._type = section_type
        self._offset = offset
        self._offset_data = offset + 16
        self._size = size

    @abstractmethod
    def name(self) -> str:
        pass

    @property
    def mapped_data(self) -> mmap.mmap:
        return self._map

    @property
    def size(self) -> int:
        return self._size

    @property
    def file_offset(self) -> int:
        return self._offset

    @property
    def data_offset(self) -> int:
        return self._offset_data


SECTION_IDENTIFIER_MANIFEST = 0x4972_535F_4D4E_4946


class FileReadableSection1Manifest(FileReadableSection1):
    def name(self) -> str:
        return "MANIFEST"

    def __init__(self, data_map: mmap.mmap, offset: int, size: int):
        super().__init__(
            data_map=data_map,
            section_type=SECTION_IDENTIFIER_MANIFEST,
            offset=offset,
            size=size,
        )

    def manifest(self) -> Manifest:
        manifest_start = self.data_offset + 4
        data_size = unpack(
            ">L", self.mapped_data[self.data_offset : manifest_start]
        )[0]
        manifest_data = self.mapped_data[
            manifest_start : manifest_start + data_size
        ]
        return parse_manifest(manifest_data)


SECTION_IDENTIFIER_END = 0x4972_535F_454E_4421


class FileReadableSection1End(FileReadableSection1):
    def name(self) -> str:
        return "END"

    def __init__(self, data_map: mmap.mmap, offset: int, size: int):
        super().__init__(
            data_map=data_map,
            section_type=SECTION_IDENTIFIER_END,
            offset=offset,
            size=size,
        )


SECTION_IDENTIFIER_IMAGE = 0x4972_535F_494D_4744


class FileReadableSection1Image(FileReadableSection1):
    def name(self) -> str:
        return "IMAGE"

    def __init__(self, data_map: mmap.mmap, offset: int, size: int):
        super().__init__(
            data_map=data_map,
            section_type=SECTION_IDENTIFIER_IMAGE,
            offset=offset,
            size=size,
        )

    def image_id(self) -> ImageID:
        id_buffer = self.mapped_data[self.data_offset : self.data_offset + 4]
        return ImageID(unpack(">L", id_buffer)[0])


class ImageReadable1:
    def __init__(
        self,
        semantic: ImageSemantic,
        width: int,
        height: int,
        data: np.ndarray[Any, Any],
    ):
        self._width = width
        self._height = height
        self._semantic = semantic
        self._data = data

    @property
    def semantic(self) -> ImageSemantic:
        return self._semantic

    def get_object_id(self, x: int, y: int) -> np.uint32:
        if x >= self._width:
            _error = f"X component {x} >= {self._width}"
            raise ValueError(_error)
        if y >= self._height:
            _error = f"Y component {y} >= {self._height}"
            raise ValueError(_error)

        if self.semantic == ImageSemantic.OBJECT_ID_32:
            _index = (y * self._width) + x
            return np.uint32(self._data[_index])

        _error = f"Cannot fetch object IDs from image with {self.semantic}"
        raise ValueError(_error)

    def get_rgb_float(
        self, x: int, y: int
    ) -> np.ndarray[Literal[3], np.dtype[np.float64]]:
        if x >= self._width:
            _error = f"X component {x} >= {self._width}"
            raise ValueError(_error)
        if y >= self._height:
            _error = f"Y component {y} >= {self._height}"
            raise ValueError(_error)

        _index: int
        match self.semantic:
            case ImageSemantic.OBJECT_ID_32:
                _index = (y * self._width) + x
                _oid32: np.uint32 = self._data[_index]
                _out = np.full(3, _oid32, dtype=np.float64)
                return np.divide(_out, 4294967296.0)

            case ImageSemantic.DEPTH_16:
                _index = (y * self._width) + x
                _u16: np.uint16 = self._data[_index]
                _out = np.full(3, _u16, dtype=np.float64)
                return np.divide(_out, 65536.0)

            case ImageSemantic.DEPTH_32:
                _index = (y * self._width) + x
                _u32: np.uint32 = self._data[_index]
                _out = np.full(3, _u32, dtype=np.float64)
                return np.divide(_out, 4294967296.0)

            case ImageSemantic.DENOISE_RGB8:
                _index = (y * self._width * 3) + (x * 3)
                _rgbu8: np.ndarray[Literal[3], np.dtype[np.uint8]]
                _rgbu8 = self._data[_index : _index + 3]
                return np.divide(_rgbu8, 256.0)

            case ImageSemantic.DENOISE_RGBA8:
                _index = (y * self._width * 4) + (x * 4)
                _rgbau8: np.ndarray[Literal[3], np.dtype[np.uint8]]
                _rgbau8 = self._data[_index : _index + 3]
                return np.divide(_rgbau8, 256.0)

            case ImageSemantic.DENOISE_RGBA16:
                _index = (y * self._width * 4) + (x * 4)
                _rgbau16: np.ndarray[Literal[3], np.dtype[np.uint16]]
                _rgbau16 = self._data[_index : _index + 3]
                return np.divide(_rgbau16, 65536.0)

            case ImageSemantic.DENOISE_RGB16:
                _index = (y * self._width * 3) + (x * 3)
                _rgba16: np.ndarray[Literal[3], np.dtype[np.uint16]]
                _rgba16 = self._data[_index : _index + 3]
                return np.divide(_rgba16, 65536.0)

            case ImageSemantic.MONOCHROME_LINES_8:
                _index = (y * self._width) + x
                _u8: np.uint8 = self._data[_index]
                _out = np.full(3, _u8, dtype=np.float64)
                return np.divide(_out, 256.0)

    def get_rgba_float(
        self, x: int, y: int
    ) -> np.ndarray[Literal[3], np.dtype[np.float64]]:
        if x >= self._width:
            _error = f"X component {x} >= {self._width}"
            raise ValueError(_error)
        if y >= self._height:
            _error = f"Y component {y} >= {self._height}"
            raise ValueError(_error)

        _index: int
        match self.semantic:
            case ImageSemantic.OBJECT_ID_32:
                _index = (y * self._width) + x
                _oid32: np.uint32 = self._data[_index]
                _out = np.full(4, _oid32, dtype=np.float64)
                _out[3] = 4294967296
                return np.divide(_out, 4294967296.0)

            case ImageSemantic.DEPTH_16:
                _index = (y * self._width) + x
                _u16: np.uint16 = self._data[_index]
                _out = np.full(4, _u16, dtype=np.float64)
                _out[3] = 65536
                return np.divide(_out, 65536.0)

            case ImageSemantic.DEPTH_32:
                _index = (y * self._width) + x
                _u32: np.uint32 = self._data[_index]
                _out = np.full(4, _u32, dtype=np.float64)
                _out[3] = 4294967296
                return np.divide(_out, 4294967296.0)

            case ImageSemantic.DENOISE_RGB8:
                _index = (y * self._width * 3) + (x * 3)
                _out_rgb8: np.ndarray[Literal[4], np.dtype[np.uint8]]
                _out_rgb8 = np.full(4, 1.0, dtype=np.float64)
                _out_rgb8[0:3] = self._data[_index : _index + 3]
                _out_rgb8[3] = 256.0
                return np.divide(_out_rgb8, 256.0)

            case ImageSemantic.DENOISE_RGBA8:
                _index = (y * self._width * 4) + (x * 4)
                _out_rgba8: np.ndarray[Literal[4], np.dtype[np.uint8]]
                _out_rgba8 = self._data[_index : _index + 4]
                return np.divide(_out_rgba8, 256.0)

            case ImageSemantic.DENOISE_RGBA16:
                _index = (y * self._width * 4) + (x * 4)
                _out_rgba16: np.ndarray[Literal[4], np.dtype[np.uint16]]
                _out_rgba16 = self._data[_index : _index + 4]
                return np.divide(_out_rgba16, 65536.0)

            case ImageSemantic.DENOISE_RGB16:
                _index = (y * self._width * 3) + (x * 3)
                _out_rgb16: np.ndarray[Literal[4], np.dtype[np.uint16]]
                _out_rgb16 = np.full(4, 1.0, dtype=np.float64)
                _out_rgb16[0:3] = self._data[_index : _index + 3]
                _out_rgb16[3] = 65536.0
                return np.divide(_out_rgb16, 65536.0)

            case ImageSemantic.MONOCHROME_LINES_8:
                _index = (y * self._width) + x
                _u8: np.uint8 = self._data[_index]
                _out_l8 = np.full(4, _u8, dtype=np.float64)
                _out_l8[3] = 256.0
                return np.divide(_out_l8, 256.0)


class FileReadable1:
    @classmethod
    def open_file(cls, path: str) -> "FileReadable1":
        f = open(path, "rb")
        mm = mmap.mmap(fileno=f.fileno(), length=0, access=mmap.ACCESS_READ)
        cls.check_magic_number(mm)
        (version_major, version_minor) = cls.check_version(mm)
        manifest_section, sections = cls.enumerate_sections(mm)
        manifest = manifest_section.manifest()
        return FileReadable1(
            file=f,
            mm=mm,
            version_major=version_major,
            version_minor=version_minor,
            manifest=manifest,
            sections=sections,
        )

    @classmethod
    def check_version(cls, mm: mmap.mmap) -> tuple[int, int]:
        version_major = unpack(">L", mm[8:12])[0]
        version_minor = unpack(">L", mm[12:16])[0]
        version_major_expected = 1
        if version_major != 1:
            _error = f"File major version {version_major} \
            should be {version_major_expected}"
            raise ValueError(_error)
        return (version_major, version_minor)

    @classmethod
    def check_magic_number(cls, mm: mmap.mmap) -> None:
        magic_expected = FILE_MAGIC_NUMBER
        magic = unpack(">Q", mm[0:8])[0]
        if magic != magic_expected:
            _error = f"File magic number {magic} should be {magic_expected}"
            raise ValueError(_error)

    @classmethod
    def enumerate_sections(
        cls, mm: mmap.mmap
    ) -> tuple[FileReadableSection1Manifest, list[FileReadableSection1]]:
        offset = 16
        sections: list[FileReadableSection1] = []
        manifest_section: FileReadableSection1Manifest | None = None

        while True:
            section_type_buffer = mm[offset : offset + 8]
            section_size_buffer = mm[offset + 8 : offset + 16]
            section_type: int = unpack(">Q", section_type_buffer)[0]
            section_size: int = unpack(">Q", section_size_buffer)[0]
            if section_type == SECTION_IDENTIFIER_MANIFEST:
                manifest_section = FileReadableSection1Manifest(
                    mm, offset, section_size
                )
                sections.append(manifest_section)
            elif section_type == SECTION_IDENTIFIER_IMAGE:
                sections.append(
                    FileReadableSection1Image(mm, offset, section_size)
                )
            elif section_type == SECTION_IDENTIFIER_END:
                sections.append(
                    FileReadableSection1End(mm, offset, section_size)
                )
                break
            offset = offset + 16
            offset = offset + section_size

        if not manifest_section:
            _error = "File is missing a manifest section."
            raise ValueError(_error)

        return manifest_section, sections

    def __init__(
        self,
        file: IO[bytes],
        mm: mmap.mmap,
        version_major: int,
        version_minor: int,
        manifest: Manifest,
        sections: list[FileReadableSection1],
    ):
        self._file = file
        self._map = mm
        self._version_major = version_major
        self._version_minor = version_minor
        self._manifest = manifest
        self._sections = sections

    def __enter__(self) -> "FileReadable1":
        return self

    def __exit__(
        self, exc_type: object, exc_value: object, traceback: object
    ) -> None:
        self._map.close()
        self._file.close()

    @property
    def version_major(self) -> int:
        return self._version_major

    @property
    def version_minor(self) -> int:
        return self._version_minor

    @property
    def sections(self) -> list[FileReadableSection1]:
        return self._sections

    def image_section(self, image_id: ImageID) -> FileReadableSection1Image:
        for section in self._sections:
            if (
                isinstance(section, FileReadableSection1Image)
                and section.image_id().value == image_id.value
            ):
                return section

        _error = "No such image section"
        raise ValueError(_error)

    def image_data(self, image_id: ImageID) -> ImageReadable1:
        section = self.image_section(image_id)
        semantic = self._manifest.images.images[image_id.value].semantic
        a_start = section.data_offset + 4
        a_end = a_start + section.size

        match semantic:
            case ImageSemantic.OBJECT_ID_32:
                return ImageReadable1(
                    semantic=semantic,
                    width=self._manifest.images.width,
                    height=self._manifest.images.height,
                    data=np.frombuffer(
                        buffer=self._map[a_start:a_end], dtype=np.dtype(">u4")
                    ),
                )
            case ImageSemantic.DEPTH_16:
                return ImageReadable1(
                    semantic=semantic,
                    width=self._manifest.images.width,
                    height=self._manifest.images.height,
                    data=np.frombuffer(
                        buffer=self._map[a_start:a_end], dtype=np.dtype(">u2")
                    ),
                )
            case ImageSemantic.DEPTH_32:
                return ImageReadable1(
                    semantic=semantic,
                    width=self._manifest.images.width,
                    height=self._manifest.images.height,
                    data=np.frombuffer(
                        buffer=self._map[a_start:a_end], dtype=np.dtype(">u4")
                    ),
                )
            case ImageSemantic.DENOISE_RGB8:
                return ImageReadable1(
                    semantic=semantic,
                    width=self._manifest.images.width,
                    height=self._manifest.images.height,
                    data=np.frombuffer(
                        buffer=self._map[a_start:a_end], dtype=np.dtype("B")
                    ),
                )
            case ImageSemantic.DENOISE_RGBA8:
                return ImageReadable1(
                    semantic=semantic,
                    width=self._manifest.images.width,
                    height=self._manifest.images.height,
                    data=np.frombuffer(
                        buffer=self._map[a_start:a_end], dtype=np.dtype("B")
                    ),
                )
            case ImageSemantic.DENOISE_RGBA16:
                return ImageReadable1(
                    semantic=semantic,
                    width=self._manifest.images.width,
                    height=self._manifest.images.height,
                    data=np.frombuffer(
                        buffer=self._map[a_start:a_end], dtype=np.dtype(">u2")
                    ),
                )
            case ImageSemantic.DENOISE_RGB16:
                return ImageReadable1(
                    semantic=semantic,
                    width=self._manifest.images.width,
                    height=self._manifest.images.height,
                    data=np.frombuffer(
                        buffer=self._map[a_start:a_end], dtype=np.dtype(">u2")
                    ),
                )
            case ImageSemantic.MONOCHROME_LINES_8:
                return ImageReadable1(
                    semantic=semantic,
                    width=self._manifest.images.width,
                    height=self._manifest.images.height,
                    data=np.frombuffer(
                        buffer=self._map[a_start:a_end], dtype=np.dtype("B")
                    ),
                )


class ImageWritable1:
    def __init__(self, semantic: ImageSemantic, offset: int, size: int):
        self._semantic = semantic
        self._offset = offset
        self._size = size

    @property
    def data_offset(self) -> int:
        return self._offset

    @property
    def data_size(self) -> int:
        return self._size

    @property
    def semantic(self) -> ImageSemantic:
        return self._semantic


class FileWritable1:
    @staticmethod
    def _aligned_size(size: int) -> int:
        return int(math.ceil(size / 16.0) * 16)

    @classmethod
    def open_file(cls, path: str, manifest: Manifest) -> "FileWritable1":
        f = open(path, "w+b")
        f.truncate(0)
        f.write(pack(">Q", FILE_MAGIC_NUMBER))
        f.write(pack(">L", 1))
        f.write(pack(">L", 0))

        section_data = serialize_manifest(manifest)
        section_size = FileWritable1._aligned_size(len(section_data))

        f.write(pack(">Q", SECTION_IDENTIFIER_MANIFEST))
        f.write(pack(">Q", section_size))
        f.write(section_data)
        f.write(bytes(section_size - len(section_data)))
        f.flush()

        writable_images: list[ImageWritable1] = []
        for i in sorted(manifest.images.images):
            image = manifest.images.images[i]
            size = pixel_size_for_semantic(image.semantic)
            total_size = manifest.images.width * manifest.images.height * size
            aligned_size = FileWritable1._aligned_size(total_size)
            f.write(pack(">Q", SECTION_IDENTIFIER_IMAGE))
            f.write(pack(">Q", aligned_size))
            f.flush()
            offset = f.tell()
            for _ in range(aligned_size):
                f.write(bytes(1))
            writable_images.append(
                ImageWritable1(
                    semantic=image.semantic, offset=offset, size=total_size
                )
            )

        f.write(pack(">Q", SECTION_IDENTIFIER_END))
        f.write(pack(">Q", 0))

        mm = mmap.mmap(fileno=f.fileno(), length=0, access=mmap.ACCESS_WRITE)
        return FileWritable1(
            file=f, mm=mm, manifest=manifest, writable_images=writable_images
        )

    def __init__(
        self,
        file: IO[bytes],
        mm: mmap.mmap,
        manifest: Manifest,
        writable_images: list[ImageWritable1],
    ):
        self._file = file
        self._map = mm
        self._manifest = manifest
        self._writable_images = writable_images

    @property
    def writable_images(self) -> list[ImageWritable1]:
        return self._writable_images

    def __enter__(self) -> "FileWritable1":
        return self

    def __exit__(
        self, exc_type: object, exc_value: object, traceback: object
    ) -> None:
        self._map.close()
        self._file.close()

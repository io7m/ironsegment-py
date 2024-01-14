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

import mmap
from abc import ABC, abstractmethod
from struct import unpack
from typing import IO

from ironsegment.model import ImageID, Manifest
from ironsegment.xml import parse_manifest


class FileReadableSection1(ABC):
    def __init__(self, data_map: mmap.mmap, section_type: int, offset: int, size: int):
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
        super().__init__(data_map=data_map, section_type=SECTION_IDENTIFIER_MANIFEST, offset=offset, size=size)

    def manifest(self) -> Manifest:
        manifest_start = self.data_offset + 4
        data_size = unpack(">L", self.mapped_data[self.data_offset : manifest_start])[0]
        manifest_data = self.mapped_data[manifest_start : manifest_start + data_size]
        return parse_manifest(manifest_data)


SECTION_IDENTIFIER_END = 0x4972_535F_454E_4421


class FileReadableSection1End(FileReadableSection1):
    def name(self) -> str:
        return "END"

    def __init__(self, data_map: mmap.mmap, offset: int, size: int):
        super().__init__(data_map=data_map, section_type=SECTION_IDENTIFIER_END, offset=offset, size=size)


SECTION_IDENTIFIER_IMAGE = 0x4972_535F_494D_4744


class FileReadableSection1Image(FileReadableSection1):
    def name(self) -> str:
        return "IMAGE"

    def __init__(self, data_map: mmap.mmap, offset: int, size: int):
        super().__init__(data_map=data_map, section_type=SECTION_IDENTIFIER_IMAGE, offset=offset, size=size)

    def image_id(self) -> ImageID:
        id_buffer = self.mapped_data[self.data_offset : self.data_offset + 4]
        return ImageID(unpack(">L", id_buffer)[0])


class FileReadable:
    @classmethod
    def open_file(cls, path: str) -> "FileReadable":
        f = open(path, "rb")
        mm = mmap.mmap(fileno=f.fileno(), length=0, access=mmap.ACCESS_READ)
        cls.check_magic_number(mm)
        (version_major, version_minor) = cls.check_version(mm)
        sections = cls.enumerate_sections(mm)
        return FileReadable(f, mm, version_major, version_minor, sections)

    @classmethod
    def check_version(cls, mm: mmap.mmap) -> tuple[int, int]:
        version_major = unpack(">L", mm[8:12])[0]
        version_minor = unpack(">L", mm[12:16])[0]
        version_major_expected = 1
        if version_major != 1:
            _error = f"File major version {version_major} should be {version_major_expected}"
            raise ValueError(_error)
        return (version_major, version_minor)

    @classmethod
    def check_magic_number(cls, mm: mmap.mmap) -> None:
        magic_expected = 0x894972530D0A1A0A
        magic = unpack(">Q", mm[0:8])[0]
        if magic != magic_expected:
            _error = f"File magic number {magic} should be {magic_expected}"
            raise ValueError(_error)

    @classmethod
    def enumerate_sections(cls, mm: mmap.mmap) -> list[FileReadableSection1]:
        offset = 16
        sections: list[FileReadableSection1] = []
        while True:
            section_type_buffer = mm[offset : offset + 8]
            section_size_buffer = mm[offset + 8 : offset + 16]
            section_type: int = unpack(">Q", section_type_buffer)[0]
            section_size: int = unpack(">Q", section_size_buffer)[0]
            if section_type == SECTION_IDENTIFIER_MANIFEST:
                sections.append(FileReadableSection1Manifest(mm, offset, section_size))
            elif section_type == SECTION_IDENTIFIER_IMAGE:
                sections.append(FileReadableSection1Image(mm, offset, section_size))
            elif section_type == SECTION_IDENTIFIER_END:
                sections.append(FileReadableSection1End(mm, offset, section_size))
                break
            offset = offset + 16
            offset = offset + section_size

        return sections

    def __init__(
        self,
        file: IO[bytes],
        mm: mmap.mmap,
        version_major: int,
        version_minor: int,
        sections: list[FileReadableSection1],
    ):
        self._file = file
        self._map = mm
        self._version_major = version_major
        self._version_minor = version_minor
        self._sections = sections

    def __enter__(self) -> "FileReadable":
        return self

    def __exit__(self, exc_type: object, exc_value: object, traceback: object) -> None:
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

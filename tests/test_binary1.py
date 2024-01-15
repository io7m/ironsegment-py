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

import os

import pytest

from ironsegment.binary1 import (
    FileReadable1,
    FileReadableSection1End,
    FileReadableSection1Image,
    FileReadableSection1Manifest,
    FileWritable1,
)
from ironsegment.model import ImageID, Manifest


def resource_file(name: str) -> str:
    return str(os.path.dirname(os.path.abspath(__file__)) + "/" + name)


class TestBinary1:
    def test_open_read(self) -> None:
        with FileReadable1.open_file(resource_file("example-0.isb")) as f:
            assert f.version_major == 1
            assert f.version_minor == 0
            assert len(f.sections) == 5
            assert isinstance(f.sections[0], FileReadableSection1Manifest)
            manifest = f.sections[0].manifest()
            assert isinstance(manifest, Manifest)
            assert isinstance(f.sections[1], FileReadableSection1Image)
            assert f.sections[1].image_id().value == 1
            assert isinstance(f.sections[2], FileReadableSection1Image)
            assert isinstance(f.sections[3], FileReadableSection1Image)
            assert isinstance(f.sections[4], FileReadableSection1End)

    def test_open_write(self, tmpdir) -> None:
        with FileReadable1.open_file(resource_file("example-0.isb")) as f:
            outfile = tmpdir + "/example-0.isb"
            manifest = f.sections[0].manifest()
            with FileWritable1.open_file(outfile, manifest) as w:
                assert len(w.writable_images) == 3
                assert w.writable_images[0].data_offset == 1248
                assert w.writable_images[1].data_offset == 2800
                assert w.writable_images[2].data_offset == 3840

    def test_get_rgb_float_x(self) -> None:
        with FileReadable1.open_file(resource_file("full.isb")) as f:
            data = f.image_data(ImageID(1))
            with pytest.raises(ValueError, match="X component.*"):
                data.get_rgb_float(1024, 0)

    def test_get_rgb_float_y(self) -> None:
        with FileReadable1.open_file(resource_file("full.isb")) as f:
            data = f.image_data(ImageID(1))
            with pytest.raises(ValueError, match="Y component.*"):
                data.get_rgb_float(0, 1024)

    def test_get_rgba_float_x(self) -> None:
        with FileReadable1.open_file(resource_file("full.isb")) as f:
            data = f.image_data(ImageID(1))
            with pytest.raises(ValueError, match="X component.*"):
                data.get_rgba_float(1024, 0)

    def test_get_rgba_float_y(self) -> None:
        with FileReadable1.open_file(resource_file("full.isb")) as f:
            data = f.image_data(ImageID(1))
            with pytest.raises(ValueError, match="Y component.*"):
                data.get_rgba_float(0, 1024)

    def test_get_rgb_float_image1(self) -> None:
        with FileReadable1.open_file(resource_file("full.isb")) as f:
            data = f.image_data(ImageID(1))
            rgb = data.get_rgb_float(0, 0)
            assert rgb[0] == 0.00000000
            assert rgb[1] == 1.0 / 65536.0
            assert rgb[2] == 2.0 / 65536.0
            assert len(rgb) == 3

            rgb = data.get_rgb_float(1, 0)
            assert rgb[0] == 1.0 / 65536.0
            assert rgb[1] == 2.0 / 65536.0
            assert rgb[2] == 3.0 / 65536.0
            assert len(rgb) == 3

            rgb = data.get_rgb_float(2, 0)
            assert rgb[0] == 2.0 / 65536.0
            assert rgb[1] == 3.0 / 65536.0
            assert rgb[2] == 4.0 / 65536.0
            assert len(rgb) == 3

    def test_get_rgb_float_image2(self) -> None:
        with FileReadable1.open_file(resource_file("full.isb")) as f:
            data = f.image_data(ImageID(2))
            rgb = data.get_rgb_float(0, 0)
            assert rgb[0] == 0.00000000
            assert rgb[1] == 1.0 / 256.0
            assert rgb[2] == 2.0 / 256.0
            assert len(rgb) == 3

            rgb = data.get_rgb_float(1, 0)
            assert rgb[0] == 1.0 / 256.0
            assert rgb[1] == 2.0 / 256.0
            assert rgb[2] == 3.0 / 256.0
            assert len(rgb) == 3

            rgb = data.get_rgb_float(2, 0)
            assert rgb[0] == 2.0 / 256.0
            assert rgb[1] == 3.0 / 256.0
            assert rgb[2] == 4.0 / 256.0
            assert len(rgb) == 3

    def test_get_rgb_float_image3(self) -> None:
        with FileReadable1.open_file(resource_file("full.isb")) as f:
            data = f.image_data(ImageID(3))
            rgb = data.get_rgb_float(0, 0)
            assert rgb[0] == 0.00000000
            assert rgb[1] == 1.0 / 65536.0
            assert rgb[2] == 2.0 / 65536.0
            assert len(rgb) == 3

            rgb = data.get_rgb_float(1, 0)
            assert rgb[0] == 1.0 / 65536.0
            assert rgb[1] == 2.0 / 65536.0
            assert rgb[2] == 3.0 / 65536.0
            assert len(rgb) == 3

            rgb = data.get_rgb_float(2, 0)
            assert rgb[0] == 2.0 / 65536.0
            assert rgb[1] == 3.0 / 65536.0
            assert rgb[2] == 4.0 / 65536.0
            assert len(rgb) == 3

    def test_get_rgb_float_image4(self) -> None:
        with FileReadable1.open_file(resource_file("full.isb")) as f:
            data = f.image_data(ImageID(4))
            rgb = data.get_rgb_float(0, 0)
            assert rgb[0] == 0.00000000
            assert rgb[1] == 1.0 / 256.0
            assert rgb[2] == 2.0 / 256.0
            assert len(rgb) == 3

            rgb = data.get_rgb_float(1, 0)
            assert rgb[0] == 1.0 / 256.0
            assert rgb[1] == 2.0 / 256.0
            assert rgb[2] == 3.0 / 256.0
            assert len(rgb) == 3

            rgb = data.get_rgb_float(2, 0)
            assert rgb[0] == 2.0 / 256.0
            assert rgb[1] == 3.0 / 256.0
            assert rgb[2] == 4.0 / 256.0
            assert len(rgb) == 3

    def test_get_rgb_float_image5(self) -> None:
        with FileReadable1.open_file(resource_file("full.isb")) as f:
            data = f.image_data(ImageID(5))
            rgb = data.get_rgb_float(0, 0)
            assert rgb[0] == 0.00000000
            assert rgb[1] == 0.00000000
            assert rgb[2] == 0.00000000
            assert len(rgb) == 3

            rgb = data.get_rgb_float(1, 0)
            assert rgb[0] == 1.0 / 65536.0
            assert rgb[1] == 1.0 / 65536.0
            assert rgb[2] == 1.0 / 65536.0
            assert len(rgb) == 3

            rgb = data.get_rgb_float(2, 0)
            assert rgb[0] == 2.0 / 65536.0
            assert rgb[1] == 2.0 / 65536.0
            assert rgb[2] == 2.0 / 65536.0
            assert len(rgb) == 3

    def test_get_rgb_float_image6(self) -> None:
        with FileReadable1.open_file(resource_file("full.isb")) as f:
            data = f.image_data(ImageID(6))
            rgb = data.get_rgb_float(0, 0)
            assert rgb[0] == 0.00000000
            assert rgb[1] == 0.00000000
            assert rgb[2] == 0.00000000
            assert len(rgb) == 3

            rgb = data.get_rgb_float(1, 0)
            assert rgb[0] == 1.0 / 4294967296.0
            assert rgb[1] == 1.0 / 4294967296.0
            assert rgb[2] == 1.0 / 4294967296.0
            assert len(rgb) == 3

            rgb = data.get_rgb_float(2, 0)
            assert rgb[0] == 2.0 / 4294967296.0
            assert rgb[1] == 2.0 / 4294967296.0
            assert rgb[2] == 2.0 / 4294967296.0
            assert len(rgb) == 3

    def test_get_rgb_float_image7(self) -> None:
        with FileReadable1.open_file(resource_file("full.isb")) as f:
            data = f.image_data(ImageID(7))
            rgb = data.get_rgb_float(0, 0)
            assert rgb[0] == 0.00000000
            assert rgb[1] == 0.00000000
            assert rgb[2] == 0.00000000
            assert len(rgb) == 3

            rgb = data.get_rgb_float(1, 0)
            assert rgb[0] == 1.0 / 256.0
            assert rgb[1] == 1.0 / 256.0
            assert rgb[2] == 1.0 / 256.0
            assert len(rgb) == 3

            rgb = data.get_rgb_float(2, 0)
            assert rgb[0] == 2.0 / 256.0
            assert rgb[1] == 2.0 / 256.0
            assert rgb[2] == 2.0 / 256.0
            assert len(rgb) == 3

    def test_get_rgb_float_image8(self) -> None:
        with FileReadable1.open_file(resource_file("full.isb")) as f:
            data = f.image_data(ImageID(8))
            rgb = data.get_rgb_float(0, 0)
            assert rgb[0] == 0.00000000
            assert rgb[1] == 0.00000000
            assert rgb[2] == 0.00000000
            assert len(rgb) == 3

            rgb = data.get_rgb_float(1, 0)
            assert rgb[0] == 1.0 / 4294967296.0
            assert rgb[1] == 1.0 / 4294967296.0
            assert rgb[2] == 1.0 / 4294967296.0
            assert len(rgb) == 3

            rgb = data.get_rgb_float(2, 0)
            assert rgb[0] == 2.0 / 4294967296.0
            assert rgb[1] == 2.0 / 4294967296.0
            assert rgb[2] == 2.0 / 4294967296.0
            assert len(rgb) == 3

    def test_get_rgba_float_image1(self) -> None:
        with FileReadable1.open_file(resource_file("full.isb")) as f:
            data = f.image_data(ImageID(1))
            rgba = data.get_rgba_float(0, 0)
            assert rgba[0] == 0.00000000
            assert rgba[1] == 1.0 / 65536.0
            assert rgba[2] == 2.0 / 65536.0
            assert len(rgba) == 4

            rgba = data.get_rgba_float(1, 0)
            assert rgba[0] == 1.0 / 65536.0
            assert rgba[1] == 2.0 / 65536.0
            assert rgba[2] == 3.0 / 65536.0
            assert len(rgba) == 4

            rgba = data.get_rgba_float(2, 0)
            assert rgba[0] == 2.0 / 65536.0
            assert rgba[1] == 3.0 / 65536.0
            assert rgba[2] == 4.0 / 65536.0
            assert len(rgba) == 4

    def test_get_rgba_float_image2(self) -> None:
        with FileReadable1.open_file(resource_file("full.isb")) as f:
            data = f.image_data(ImageID(2))
            rgba = data.get_rgba_float(0, 0)
            assert rgba[0] == 0.00000000
            assert rgba[1] == 1.0 / 256.0
            assert rgba[2] == 2.0 / 256.0
            assert len(rgba) == 4

            rgba = data.get_rgba_float(1, 0)
            assert rgba[0] == 1.0 / 256.0
            assert rgba[1] == 2.0 / 256.0
            assert rgba[2] == 3.0 / 256.0
            assert len(rgba) == 4

            rgba = data.get_rgba_float(2, 0)
            assert rgba[0] == 2.0 / 256.0
            assert rgba[1] == 3.0 / 256.0
            assert rgba[2] == 4.0 / 256.0
            assert len(rgba) == 4

    def test_get_rgba_float_image3(self) -> None:
        with FileReadable1.open_file(resource_file("full.isb")) as f:
            data = f.image_data(ImageID(3))
            rgba = data.get_rgba_float(0, 0)
            assert rgba[0] == 0.00000000
            assert rgba[1] == 1.0 / 65536.0
            assert rgba[2] == 2.0 / 65536.0
            assert len(rgba) == 4

            rgba = data.get_rgba_float(1, 0)
            assert rgba[0] == 1.0 / 65536.0
            assert rgba[1] == 2.0 / 65536.0
            assert rgba[2] == 3.0 / 65536.0
            assert len(rgba) == 4

            rgba = data.get_rgba_float(2, 0)
            assert rgba[0] == 2.0 / 65536.0
            assert rgba[1] == 3.0 / 65536.0
            assert rgba[2] == 4.0 / 65536.0
            assert len(rgba) == 4

    def test_get_rgba_float_image4(self) -> None:
        with FileReadable1.open_file(resource_file("full.isb")) as f:
            data = f.image_data(ImageID(4))
            rgba = data.get_rgba_float(0, 0)
            assert rgba[0] == 0.00000000
            assert rgba[1] == 1.0 / 256.0
            assert rgba[2] == 2.0 / 256.0
            assert len(rgba) == 4

            rgba = data.get_rgba_float(1, 0)
            assert rgba[0] == 1.0 / 256.0
            assert rgba[1] == 2.0 / 256.0
            assert rgba[2] == 3.0 / 256.0
            assert len(rgba) == 4

            rgba = data.get_rgba_float(2, 0)
            assert rgba[0] == 2.0 / 256.0
            assert rgba[1] == 3.0 / 256.0
            assert rgba[2] == 4.0 / 256.0
            assert len(rgba) == 4

    def test_get_rgba_float_image5(self) -> None:
        with FileReadable1.open_file(resource_file("full.isb")) as f:
            data = f.image_data(ImageID(5))
            rgba = data.get_rgba_float(0, 0)
            assert rgba[0] == 0.00000000
            assert rgba[1] == 0.00000000
            assert rgba[2] == 0.00000000
            assert len(rgba) == 4

            rgba = data.get_rgba_float(1, 0)
            assert rgba[0] == 1.0 / 65536.0
            assert rgba[1] == 1.0 / 65536.0
            assert rgba[2] == 1.0 / 65536.0
            assert len(rgba) == 4

            rgba = data.get_rgba_float(2, 0)
            assert rgba[0] == 2.0 / 65536.0
            assert rgba[1] == 2.0 / 65536.0
            assert rgba[2] == 2.0 / 65536.0
            assert len(rgba) == 4

    def test_get_rgba_float_image6(self) -> None:
        with FileReadable1.open_file(resource_file("full.isb")) as f:
            data = f.image_data(ImageID(6))
            rgba = data.get_rgba_float(0, 0)
            assert rgba[0] == 0.00000000
            assert rgba[1] == 0.00000000
            assert rgba[2] == 0.00000000
            assert len(rgba) == 4

            rgba = data.get_rgba_float(1, 0)
            assert rgba[0] == 1.0 / 4294967296.0
            assert rgba[1] == 1.0 / 4294967296.0
            assert rgba[2] == 1.0 / 4294967296.0
            assert len(rgba) == 4

            rgba = data.get_rgba_float(2, 0)
            assert rgba[0] == 2.0 / 4294967296.0
            assert rgba[1] == 2.0 / 4294967296.0
            assert rgba[2] == 2.0 / 4294967296.0
            assert len(rgba) == 4

    def test_get_rgba_float_image7(self) -> None:
        with FileReadable1.open_file(resource_file("full.isb")) as f:
            data = f.image_data(ImageID(7))
            rgba = data.get_rgba_float(0, 0)
            assert rgba[0] == 0.00000000
            assert rgba[1] == 0.00000000
            assert rgba[2] == 0.00000000
            assert len(rgba) == 4

            rgba = data.get_rgba_float(1, 0)
            assert rgba[0] == 1.0 / 256.0
            assert rgba[1] == 1.0 / 256.0
            assert rgba[2] == 1.0 / 256.0
            assert len(rgba) == 4

            rgba = data.get_rgba_float(2, 0)
            assert rgba[0] == 2.0 / 256.0
            assert rgba[1] == 2.0 / 256.0
            assert rgba[2] == 2.0 / 256.0
            assert len(rgba) == 4

    def test_get_rgba_float_image8(self) -> None:
        with FileReadable1.open_file(resource_file("full.isb")) as f:
            data = f.image_data(ImageID(8))
            rgba = data.get_rgba_float(0, 0)
            assert rgba[0] == 0.00000000
            assert rgba[1] == 0.00000000
            assert rgba[2] == 0.00000000
            assert len(rgba) == 4

            rgba = data.get_rgba_float(1, 0)
            assert rgba[0] == 1.0 / 4294967296.0
            assert rgba[1] == 1.0 / 4294967296.0
            assert rgba[2] == 1.0 / 4294967296.0
            assert len(rgba) == 4

            rgba = data.get_rgba_float(2, 0)
            assert rgba[0] == 2.0 / 4294967296.0
            assert rgba[1] == 2.0 / 4294967296.0
            assert rgba[2] == 2.0 / 4294967296.0
            assert len(rgba) == 4

    def test_get_object_id(self) -> None:
        with FileReadable1.open_file(resource_file("full.isb")) as f:
            for i in range(1, 9):
                data = f.image_data(ImageID(i))
                if i == 8:
                    assert data.get_object_id(0, 0) == 0
                    assert data.get_object_id(1, 0) == 1
                    assert data.get_object_id(2, 0) == 2
                else:
                    with pytest.raises(ValueError, match="Cannot fetch ob.*"):
                        data.get_object_id(0, 0)

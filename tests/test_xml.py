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
from lxml.etree import XMLSyntaxError

from ironsegment.model import ImageSemantic
from ironsegment.xml import (
    parse_manifest,
    parse_manifest_text,
    schema_bytes,
    serialize_manifest,
)


def resource(name: str) -> bytes:
    path = os.path.dirname(os.path.abspath(__file__)) + "/" + name
    with open(path, "rb") as f:
        return f.read()


class TestSchema:
    def test_schema_bytes(self) -> None:
        assert schema_bytes()

    def test_parse_text_0(self) -> None:
        with pytest.raises(XMLSyntaxError):
            parse_manifest_text("<x>")

    def test_parse_text_error_0(self) -> None:
        with pytest.raises(XMLSyntaxError):
            parse_manifest_text(resource("manifest-error0.xml"))

    def test_parse_text_error_1(self) -> None:
        with pytest.raises(XMLSyntaxError):
            parse_manifest_text(resource("manifest-error1.xml"))

    def test_parse_text_error_2(self) -> None:
        with pytest.raises(XMLSyntaxError):
            parse_manifest_text(resource("manifest-error2.xml"))

    def test_parse_text_error_3(self) -> None:
        with pytest.raises(XMLSyntaxError):
            parse_manifest_text(resource("manifest-error3.xml"))

    def test_parse_ok_0(self) -> None:
        tree = parse_manifest_text(resource("manifest0.xml"))
        assert tree[0].tag == "{urn:com.io7m.ironsegment:manifest:1}Images"
        assert tree[1].tag == "{urn:com.io7m.ironsegment:manifest:1}Objects"
        assert tree[2].tag == "{urn:com.io7m.ironsegment:manifest:1}Metadata"

    def test_parse_ok_1(self) -> None:
        manifest0 = parse_manifest(resource("manifest0.xml"))
        assert "Copyright" in manifest0.metadata["com.io7m.license"]
        assert manifest0.images.width == 1024
        assert manifest0.images.height == 1024
        assert manifest0.images.images[1].semantic == ImageSemantic.DENOISE_RGB8
        assert manifest0.images.images[2].semantic == ImageSemantic.DEPTH_16
        assert manifest0.images.images[3].semantic == ImageSemantic.OBJECT_ID_32
        assert manifest0.objects[1].description == ""

        manifest1 = parse_manifest(serialize_manifest(manifest0))
        assert manifest0.metadata == manifest1.metadata

        assert len(manifest0.objects) == len(manifest1.objects)
        assert (
            manifest0.objects[1].identifier.value
            == manifest1.objects[1].identifier.value
        )
        assert (
            manifest0.objects[1].description == manifest1.objects[1].description
        )

        assert manifest0.images.width == manifest1.images.width
        assert manifest0.images.height == manifest1.images.height
        assert len(manifest0.images.images) == len(manifest1.images.images)
        assert (
            manifest0.images.images[1].identifier.value
            == manifest1.images.images[1].identifier.value
        )
        assert (
            manifest0.images.images[1].semantic
            == manifest1.images.images[1].semantic
        )
        assert (
            manifest0.images.images[2].identifier.value
            == manifest1.images.images[2].identifier.value
        )
        assert (
            manifest0.images.images[2].semantic
            == manifest1.images.images[2].semantic
        )
        assert (
            manifest0.images.images[3].identifier.value
            == manifest1.images.images[3].identifier.value
        )
        assert (
            manifest0.images.images[3].semantic
            == manifest1.images.images[3].semantic
        )

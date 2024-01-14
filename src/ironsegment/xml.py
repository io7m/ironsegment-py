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


from importlib import resources as import_resources

from lxml import etree
from lxml.etree import XMLSchema, _Element

from ironsegment.model import Image, ImageID, Images, ImageSemantic, Manifest, Object, ObjectID


def schema_bytes() -> bytes:
    path = import_resources.files("ironsegment") / "manifest-1.xsd"
    with path.open("rb") as f:
        return f.read()


def schema() -> XMLSchema:
    schema_root = etree.XML(schema_bytes())
    return etree.XMLSchema(schema_root)


def parse_manifest_text(text: bytes) -> _Element:
    parser = etree.XMLParser(schema=schema(), resolve_entities=False)
    return etree.fromstring(text, parser)


def parse_manifest(text: bytes) -> Manifest:
    tree = parse_manifest_text(text)
    images_tree = tree[0]
    images: dict[int, Image] = {}
    width = int(str(images_tree.get("Width")))
    height = int(str(images_tree.get("Height")))
    for e in images_tree:
        image_id = ImageID(int(str(e.get("ID"))))
        image_semantic = ImageSemantic(ImageSemantic[(str(e.get("Semantic")))])
        images[image_id.value] = Image(image_id, image_semantic)

    objects_tree = tree[1]
    objects: dict[int, Object] = {}
    for e in objects_tree:
        object_id = ObjectID(int(str(e.get("ID"))))
        description = e.text or ""
        objects[object_id.value] = Object(object_id, description)

    metadata_tree = tree[2]
    metadata: dict[str, str] = {}
    for e in metadata_tree:
        meta_name = str(e.get("Name"))
        meta_text = e.text or ""
        metadata[meta_name] = meta_text

    return Manifest(Images(width, height, images), objects, metadata)

The images the shop runs

images.txt has one line for each image the service uses: the image's name,
a space, and the file its index was saved to, under this folder.

Three of the files are real, saved from their registries on 2026-11-11 with
`docker buildx imagetools inspect --raw IMAGE`, which prints what the
registry holds for that name, exactly as stored, all on one line.
A multi-architecture image's file is an index: a list of manifests, one per
platform, each with a "platform" that names its "os" and "architecture".
An image with no index is a single manifest, which names no platform at all:
it was built for one architecture only.

The fourth, shop-api-3.4.json, is the shop's own image's index, as the
shop's build pipeline wrote it. It is made up for this lab: the shop and
its registry, registry.shop.test, don't exist.

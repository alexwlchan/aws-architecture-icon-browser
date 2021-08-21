#!/usr/bin/env python

import collections
import colorsys
import os
import re
import urllib.request
import zipfile

from flask import Flask, render_template, send_file


# From https://aws.amazon.com/architecture/icons/
ASSET_PACKAGE_URL = "https://d1.awsstatic.com/webteam/architecture-icons/q3-2021/Asset-Package_07302021.533e2e5c12d0759fd00ce35fa70d8418a26f4a90.zip"


app = Flask(__name__)


def ensure_asset_package_downloaded():
    """
    Ensures an asset package is downloaded and unpacker in the
    current directory.

    Returns the name of the asset package directory.
    """
    asset_package_dirname = os.path.basename(ASSET_PACKAGE_URL).split(".")[0]
    if os.path.isdir(asset_package_dirname):
        return asset_package_dirname

    filename = os.path.basename(ASSET_PACKAGE_URL)
    urllib.request.urlretrieve(ASSET_PACKAGE_URL, filename)

    with zipfile.ZipFile(filename) as zf:
        zf.extractall()

    return asset_package_dirname


def get_file_paths_under(root="."):
    """Generates the paths to every file under ``root``."""
    if not os.path.isdir(root):
        raise ValueError(f"Cannot find files under non-existent directory: {root!r}")

    for dirpath, _, filenames in os.walk(root):
        for f in filenames:
            if f == ".DS_Store":
                continue

            if os.path.isfile(os.path.join(dirpath, f)):
                yield os.path.join(dirpath, f)


@app.template_filter("description")
def asset_description(path):
    """
    Given the path to an asset, return a short description.
    """
    # Filenames are of the form
    #
    #     Arch_AWS-App-Mesh_48.svg
    #     Arch_AWS-App-Mesh_64@5x.png
    #     Res_AWS-App-Mesh-Mesh_48_Light.png
    #
    filename = os.path.basename(path)

    size = filename.split("_")[-1].split(".")[0]
    image_format = filename.split(".")[-1]

    return f"{image_format} ({size})"


@app.template_filter("by_size")
def assets_by_size(assets):
    """
    Given a list of assets, return a list of them by format and size.
    """
    asset_filenames = {path: os.path.basename(path) for path in assets}

    # Filenames are of the form
    #
    #     Arch_AWS-App-Mesh_48.svg
    #     Arch_AWS-App-Mesh_64@5x.png
    #     Res_AWS-App-Mesh-Mesh_48_Light.png
    #
    assets_by_size = {
        path: int(
            filename.replace("_Light", "")
            .replace("_Dark", "")
            .split("_")[-1]
            .split(".")[0]
            .replace("64@5x", "320")
        )
        for path, filename in asset_filenames.items()
    }

    return sorted(assets_by_size, key=lambda path: assets_by_size[path], reverse=True)


@app.template_filter("highest_res")
def highest_res_asset(assets):
    """
    Given a list of assets, return the one which is highest resolution.
    """
    return assets_by_size(assets)[0]


@app.route("/")
def index():
    paths = list(get_file_paths_under(asset_package_dirname))

    architecture_icons = collections.defaultdict(list)
    category_icons = collections.defaultdict(list)
    resource_icons = collections.defaultdict(list)

    for p in paths:
        name = (
            os.path.basename(p)
            .replace("_Light", "")
            .replace("_Dark", "")
            .rsplit("_", 1)[0]
            .replace("-", " ")
        )

        if "/Architecture-" in p:
            architecture_icons[name.replace("Arch_", "")].append(p)

        if "/Category-" in p:
            category_icons[name.replace("Arch Category_", "")].append(p)

        if "/Resource-" in p:
            resource_icons[name.replace("Res_", "").replace("_", ": ")].append(p)

    return render_template(
        "index.html",
        paths=paths,
        architecture_icons=architecture_icons,
        category_icons=category_icons,
        resource_icons=resource_icons,
    )


@app.route("/<path:path>")
def serve_asset(path):
    assert path.startswith("Asset-Package_")
    return send_file(path)


@app.template_filter("tint_color")
def choose_color_from_path(assets):
    """
    Makes a rough guess about the colour of this icon.
    """
    path = next(p for p in assets if p.endswith(".svg"))

    with open(path) as infile:
        hex_strings = set(re.findall(r"#[A-F0-9a-f]{6}", infile.read()))

    colors = {
        (
            int(hs[1:3], 16) / 255,
            int(hs[3:5], 16) / 255,
            int(hs[5:7], 16) / 255,
        ): hs  # red-green-blue
        for hs in hex_strings
    }

    colors_to_hls = {(r, g, b): colorsys.rgb_to_hls(r, g, b) for (r, g, b) in colors}

    # Remove any colors which are too light to have sufficient contrast
    usable_colors = {
        (r, g, b): (h, lightness, s)
        for (r, g, b), (h, lightness, s) in colors_to_hls.items()
        if lightness <= 0.8
    }

    try:
        most_saturated_color = max(usable_colors, key=lambda c: usable_colors[c][2])
    except ValueError:
        # no usable color, just use black
        return "#000"

    return colors[most_saturated_color]


if __name__ == "__main__":
    asset_package_dirname = ensure_asset_package_downloaded()

    app.run(debug=True, port=2520)

#!/bin/bash
echo "Setting up Blender file extensions..."
DESKTOP_FILE="$HOME/.local/share/applications/blender_auto_import.desktop"
MIME_DIR="$HOME/.local/share/mime/packages"
PYTHON_SCRIPT="$HOME/.config/blender/blender_auto_open.py"
EXT_LIST="fbx obj 3ds"

mkdir -p $(dirname "$DESKTOP_FILE")
mkdir -p $(dirname "$PYTHON_SCRIPT")

tee $DESKTOP_FILE > /dev/null <<EOF
[Desktop Entry]
Encoding=UTF-8
Name=Blender Auto Import
Exec=blender --python $PYTHON_SCRIPT -- %F
MimeType=application/x-blender_auto_import;
Icon=blender
Terminal=false
Type=Application
Categories=Graphics;3DGraphics;
EOF
echo "  written: '$DESKTOP_FILE'"

# setup file associations
for EXT in $EXT_LIST; do
    XML_FILEPATH="$MIME_DIR/x-blender_auto_import_$EXT.xml"
    tee $XML_FILEPATH > /dev/null <<EOF
<?xml version="1.0" encoding="UTF-8"?>
<mime-info xmlns="http://www.freedesktop.org/standards/shared-mime-info">
    <mime-type type="application/x-blender_auto_import_$EXT">
    <comment>Blender $EXT file</comment>
        <glob pattern="*.$EXT"/>
</mime-type>
</mime-info>
EOF
echo "  written: '$XML_FILEPATH'"
done

# update desktop files
update-desktop-database $(dirname "$DESKTOP_FILE")
update-mime-database $(dirname "$MIME_DIR")

for EXT in $EXT_LIST; do
xdg-mime default ${DESKTOP_FILE##*/} "application/x-blender_auto_import_$EXT"
done

tee $PYTHON_SCRIPT > /dev/null <<EOF
import bpy


# format specific options... change as you like
args_fbx = dict(
    # global_scale=1.0,
    )

args_obj = dict(
    # use_image_search=False,
    )

args_3ds = dict(
    # constrain_size=0.0,
    )

def clear_scene():
    if "Cube" in bpy.data.meshes:
        mesh = bpy.data.meshes["Cube"]
        print("removing mesh", mesh)
        bpy.data.meshes.remove(mesh)

def main():
    import os

    from sys import argv
    argv = argv[argv.index("--") + 1:]

    for f in argv:
        ext = os.path.splitext(f)[1].lower()

        if ext == ".fbx":
            bpy.ops.import_scene.fbx(filepath=f, **args_fbx)
        elif ext == ".obj":
            bpy.ops.import_scene.obj(filepath=f, **args_obj)
        elif ext == ".3ds":
            bpy.ops.import_scene.autodesk_3ds(filepath=f, **args_3ds)
        else:
            print("Extension %r is not known!" % ext)
    else:
        print("No files passed!")

if __name__ == "__main__":
    clear_scene()
    main()
EOF
echo "  written: '$PYTHON_SCRIPT'"

echo "Done!"


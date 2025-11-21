#!/bin/sh
cd github_mirror
python ../repotoolnext.py ../../personalLinks/local_github_backup_list.json
cd ..

cd UnrealEngine
cd zen
git fetch --depth 1
git reset --hard "$(git rev-parse --abbrev-ref --symbolic-full-name '@{u}')"
git clean -dfx
cd ..
cd UnrealEngine
git fetch --depth 1
git reset --hard "$(git rev-parse --abbrev-ref --symbolic-full-name '@{u}')"
git clean -dfx
cd ..
cd ..

cd aseprite
git fetch --depth 1
git reset --hard "$(git rev-parse --abbrev-ref --symbolic-full-name '@{u}')"
git submodule update --depth 1
git clean -dfx
cd ..

cd blender-release-src
git fetch --depth 1
git reset --hard "$(git rev-parse --abbrev-ref --symbolic-full-name '@{u}')"
git clean -dfx
cd ..


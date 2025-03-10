#!/bin/sh
if [ "$#" -ne 1 ]; then
	echo "Usage: $0 <dstfolder>"
	echo "example: $0 '/media/USB Stick'"
	exit 1
fi

runRSync () {
	# -P is equal to --partial --progress
	# -m prune empty directories
	# -a archive mode
	# --delete delete extraneous files from dest dirs

	rsync -a -m --include='**/.git/**' --include='*/' --exclude='*' -P --stats --delete "$1" "$2"
}

runRSync "UnrealEngine/" "$1/UnrealEngine"
runRSync "github_mirror/" "$1/github_mirror"
runRSync "aseprite/" "$1/aseprite"

# the following is expensive....
#tar -cJvf "$1/fuchsia.tar.xz" "fuchsia/"

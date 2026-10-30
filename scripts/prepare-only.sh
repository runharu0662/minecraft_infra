#!/bin/sh
# Isolated installer only; never calls /start or launches Minecraft.
set -eu
. /migration/pack.env
printf '%s  %s\n' "$PACK_SHA256" /modpack/server-pack.zip | sha256sum -c - >/dev/null
exec mc-image-helper install-curseforge "$@"

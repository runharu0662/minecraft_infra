#!/bin/sh
# Check before /start can create a world or modify data.
set -eu
case "${LEVEL:-}" in
  ''|.|..|*[!a-zA-Z0-9_-]*)
    echo 'LEVEL must be a single directory name using letters, digits, _ or -.' >&2
    exit 1 ;;
esac
if [ -L "/data/$LEVEL" ] || [ -L "/data/$LEVEL/level.dat" ]; then
  echo 'World and level.dat must be copies, not symbolic links.' >&2
  exit 1
fi
if [ ! -s "/data/$LEVEL/level.dat" ]; then
  echo 'Existing level.dat missing or empty; refusing world generation.' >&2
  exit 1
fi
if [ ! -f /data/server.properties ] ||
   ! grep -qx "level-name=$LEVEL" /data/server.properties ||
   [ "$(grep -Ec '^[[:space:]]*level-name([[:space:]=:]|$)' /data/server.properties)" != 1 ] ||
   grep -q '\\$' /data/server.properties; then
  echo 'server.properties level-name must exactly match LEVEL.' >&2
  exit 1
fi
# Generated from the inspected local export; never use an unpinned archive.
. /migration/pack.env
if [ "${VERSION:-}" != "$PACK_MINECRAFT" ] ||
   [ "${FORGE_VERSION:-}" != "$PACK_FORGE" ]; then
  echo 'Minecraft/Forge settings differ from the locked export.' >&2
  exit 1
fi
printf '%s  %s\n' "$PACK_SHA256" /modpack/server-pack.zip | sha256sum -c - >/dev/null
if [ "${MODPACK_VERIFIED_SHA256:-}" != "$PACK_SHA256" ]; then
  echo 'Pack not verified against the original instance; refusing to load the world.' >&2
  exit 1
fi
exec /start "$@"

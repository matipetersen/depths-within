#!/bin/bash
# Run Depths Within with GRAPHICAL TILESET
# This uses actual 32x32 pixel graphics from submarine_tileset.png

export USE_TILESET=1
export TW_SW=60    # 60x30 grid = 1920x960 pixels with 32px tiles
export TW_SH=30

echo "==========================================="
echo "  DEPTHS WITHIN - GRAPHICAL TILESET MODE"
echo "==========================================="
echo "Console grid: ${TW_SW}x${TW_SH} (will display as pixels)"
echo "Using 32x32 pixel tileset from submarine_tileset.png"
echo "Each console cell = one 32x32 pixel tile"
echo ""
echo "Estimated window size: $((TW_SW * 32))x$((TW_SH * 32)) pixels"
echo ""

python main.py

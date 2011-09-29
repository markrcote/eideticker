#!/bin/sh
FFMPEG="ffmpeg -vcodec rawvideo -f rawvideo -pix_fmt uyvy422 -r 60 -s hd1080 -i $1.raw --"

$FFMPEG $1.avi
$FFMPEG $1-%d.png
zip -j $1-pngs.zip -- $1-*.png
rm -- $1-*.png

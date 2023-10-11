#!/bin/bash
# exp_time=25
ts=$(date +%s)
outfile_pref=/mnt/usbstick/deeplens/data/$1$ts
tcpdump -i eth0 -tttt -s0 -w $outfile_pref.pcap -Z root &
ffmpeg -nostdin -f v4l2 -i /dev/video0 -y $outfile_pref'_1.mp4' & 
ffmpeg -nostdin -i rtsp://192.168.143.124:554/live.sdp  -acodec copy -vcodec copy -y $outfile_pref'_2.mkv' &
arecord -f S16_LE -r 16000 --device="hw:2,0" $outfile_pref.wav

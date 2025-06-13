URL = "https://www.youtube.com/watch?v=VsF3MsUUu3E&list=PLk6Z3_JllTRwm6Td-S7VUDLQjrxaLLdzE&index=6"
AUDIO = "vietnamese_narration_edge_tts.mp3"
VIDEO = "./Statistics 21 - Lecture 7 [VsF3MsUUu3E].mkv"
ENG_SUB = "./Statistics 21 - Lecture 7 [VsF3MsUUu3E].en-cvfXDfbeED0.srt"
VIE_SUB = "./lec7_vie.srt"
RESULT = "lec7.mp4"

run: trans audio combine

combine:
	ffmpeg -i $(VIDEO) -i $(AUDIO) -filter_complex "[0:a]volume=0.4[a0];[1:a][a0]amix=inputs=2:duration=first[aout]" -map 0:v -map "[aout]" -c:v copy -c:a aac -shortest $(RESULT)

download:
	# en-cvfXDfbeED0 over en because its default caption, try `yt-dlp --list-subs https://www.youtube.com/watch?v=EPrAKgawSnY&t=1053s4`
	uv run yt-dlp --no-playlist --write-subs --write-auto-subs --sub-lang en-cvfXDfbeED0 --convert-subs srt -f bestvideo+bestaudio $(URL)

trans:
	uv run gst translate -i $(ENG_SUB) -l Vietnamese -o $(VIE_SUB) -k "AIzaSyDXpmSZJofZQAge-KDr6ikkxfkKBPABm28"
	
audio:
	uv run make_audio.py --engine edge-tts --voice="vi-VN-HoaiMyNeural" --rate="+20%" --lang="vi" $(VIE_SUB) $(AUDIO)

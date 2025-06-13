URL = "https://www.youtube.com/watch?v=k6YkcX6e8OU&t=9s"
AUDIO = "vietnamese_narration_edge_tts.mp3"
VIDEO = "./Statistics 21 -  Lecture 5 [k6YkcX6e8OU].mkv"
ENG_SUB = "./Statistics 21 -  Lecture 5 [k6YkcX6e8OU].en-cvfXDfbeED0.srt"
VIE_SUB = "./lec5_vie.srt"
RESULT = "lec5.mp4"

run: trans audio combine

combine:
	# ffmpeg -i $(VIDEO) -i $(AUDIO) -filter_complex "[0:a]volume=0.3[a0];[1:a]volume=1.0[a1];[a0][a1]amerge=inputs=2[aout]" -map 0:v -map "[aout]" -c:v copy -c:a aac -b:a 192k $(RESULT)

	ffmpeg -i $(VIDEO) -i $(AUDIO) -filter_complex "[0:a]volume=0.4[a0];[1:a][a0]amix=inputs=2:duration=first[aout]" -map 0:v -map "[aout]" -c:v copy -c:a aac -shortest $(RESULT)

download:
	# en-cvfXDfbeED0 over en because its default caption, try `yt-dlp --list-subs https://www.youtube.com/watch?v=EPrAKgawSnY&t=1053s4`
	uv run yt-dlp --write-subs --write-auto-subs --sub-lang en-cvfXDfbeED0 --convert-subs srt -f bestvideo+bestaudio $(URL)

trans:
	gst translate -i $(ENG_SUB) -l Vietnamese -o $(VIE_SUB) -k "AIzaSyDXpmSZJofZQAge-KDr6ikkxfkKBPABm28"
	
audio:
	uv run make_audio.py --engine edge-tts --voice="vi-VN-HoaiMyNeural" --rate="+30%" --lang="vi" $(VIE_SUB) $(AUDIO)

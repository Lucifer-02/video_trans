import srt
from pydub import AudioSegment
import asyncio
import edge_tts
import os  # Import os for removing temporary file


async def async_generate_edge_tts(
    text, output_filepath, voice="vi-VN-HoaiMyNeural", rate="+50%"
):
    """Asynchronously generates TTS audio using edge-tts and saves it to a file."""
    communicate = edge_tts.Communicate(text=text, voice=voice, rate=rate)
    await communicate.save(output_filepath)


def generate_tts_segment(text, duration_ms):
    """
    Generates TTS audio for the given text using edge-tts and attempts to fit it to duration_ms.
    """
    print(f"Generating TTS for: '{text}' (intended duration: {duration_ms}ms)")
    temp_audio_path = "temp_tts_segment.mp3"

    try:
        # Generate TTS using edge-tts
        asyncio.run(async_generate_edge_tts(text, temp_audio_path))

        # Load the generated audio segment
        segment = AudioSegment.from_file(temp_audio_path, format="mp3")

        # Pad or trim to fit duration_ms (basic approach, speech rate not adjusted)
        if len(segment) < duration_ms:
            padding_needed = duration_ms - len(segment)
            segment = segment + AudioSegment.silent(duration=padding_needed)
        elif len(segment) > duration_ms:
            segment = segment[:duration_ms]  # Trim if too long

        # Clean up the temporary file
        os.remove(temp_audio_path)

        return segment

    except Exception as e:
        print(f"Edge-TTS error: {e}. Ensure you have edge-tts and asyncio installed.")
        # Fallback if edge-tts fails
        if os.path.exists(temp_audio_path):
            os.remove(temp_audio_path)
        return AudioSegment.silent(duration=duration_ms)


def srt_to_audio(srt_filepath, output_audio_filepath):
    with open(srt_filepath, "r", encoding="utf-8") as f:
        subs = list(srt.parse(f.read()))

    full_audio = AudioSegment.silent(duration=0)
    last_end_time_ms = 0

    for i, sub in enumerate(subs):
        start_time_ms = sub.start.total_seconds() * 1000
        end_time_ms = sub.end.total_seconds() * 1000

        # Add silence for the gap before the current subtitle
        gap_duration_ms = start_time_ms - last_end_time_ms
        if gap_duration_ms > 0:
            full_audio += AudioSegment.silent(duration=int(gap_duration_ms))
        elif gap_duration_ms < 0:
            print(
                f"Warning: Overlapping subtitles detected at sub {sub.index}. Adjusting gap."
            )
            # Handle overlaps, e.g., trim previous segment or simply add no gap

        # Generate TTS for the current subtitle text
        subtitle_duration_ms = end_time_ms - start_time_ms
        tts_segment = generate_tts_segment(sub.content, subtitle_duration_ms)

        full_audio += tts_segment

        last_end_time_ms = end_time_ms

        print(f"Processed subtitle {sub.index}/{len(subs)}")

    full_audio.export(output_audio_filepath, format="mp3")
    print(f"Generated complete audio file: {output_audio_filepath}")


# --- How to use the script (example) ---
srt_to_audio("/home/lucifer/Documents/sub.srt", "vietnamese_narration.mp3")

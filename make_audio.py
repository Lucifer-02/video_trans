import asyncio
import os

import click
import edge_tts
import srt
from pydub import AudioSegment
from modulefinder import replacePackageMap


async def async_generate_edge_tts(
    text, output_filepath, voice="vi-VN-HoaiMyNeural", rate="+50%"
):
    """Asynchronously generates TTS audio using edge-tts and saves it to a file."""
    communicate = edge_tts.Communicate(text=text, voice=voice, rate=rate)
    await communicate.save(output_filepath)


def generate_tts_segment(
    text,
    duration_ms,
    engine="edge-tts",
    voice="vi-VN-HoaiMyNeural",
    rate="+50%",
    lang="vi",
):
    """
    Generates TTS audio for the given text using the specified engine and attempts to fit it to duration_ms.
    Only supports edge-tts after gTTS removal.
    """
    print(
        f"Generating TTS for: '{text}' (intended duration: {duration_ms}ms) using engine: {engine}"
    )
    temp_audio_path = "temp_tts_segment.mp3"
    segment = None

    try:
        if engine == "edge-tts":
            asyncio.run(
                async_generate_edge_tts(text, temp_audio_path, voice=voice, rate=rate)
            )
            segment = AudioSegment.from_file(temp_audio_path, format="mp3")
            if os.path.exists(temp_audio_path):
                os.remove(temp_audio_path)

        else:
            print(
                f"Unknown or unsupported TTS engine: {engine}. Only 'edge-tts' is supported. Returning silent segment."
            )
            return AudioSegment.silent(duration=duration_ms)

        if len(segment) < duration_ms:
            padding_needed = duration_ms - len(segment)
            segment = segment + AudioSegment.silent(duration=padding_needed)
        elif len(segment) > duration_ms:
            segment = segment[:duration_ms]

        return segment

    except Exception as e:
        print(f"Error generating TTS with {engine}: {e}.")
        if os.path.exists(temp_audio_path):
            os.remove(temp_audio_path)
        return AudioSegment.silent(duration=duration_ms)


def srt_to_audio(
    srt_filepath,
    output_audio_filepath,
    engine="edge-tts",
    voice="vi-VN-HoaiMyNeural",
    rate="+30%",
    lang="vi",
):
    """
    Converts an SRT file to an audio file using TTS.
    """
    with open(srt_filepath, "r", encoding="utf-8") as f:
        subs = list(srt.parse(f.read()))

    full_audio = AudioSegment.silent(duration=0)
    last_end_time_ms = 0

    for i, sub in enumerate(subs):
        start_time_ms = sub.start.total_seconds() * 1000
        end_time_ms = sub.end.total_seconds() * 1000

        gap_duration_ms = start_time_ms - last_end_time_ms
        if gap_duration_ms > 0:
            full_audio += AudioSegment.silent(duration=int(gap_duration_ms))
        elif gap_duration_ms < 0:
            print(
                f"Warning: Overlapping subtitles detected at sub {sub.index}. Adjusting gap."
            )

        subtitle_duration_ms = end_time_ms - start_time_ms
        tts_segment = generate_tts_segment(
            sub.content.replace("\n", " "),
            subtitle_duration_ms,
            engine=engine,
            voice=voice,
            rate=rate,
            lang=lang,
        )

        full_audio += tts_segment

        last_end_time_ms = end_time_ms

        print(f"Processed subtitle {sub.index}/{len(subs)}")

    full_audio.export(output_audio_filepath, format="mp3")
    print(f"Generated complete audio file: {output_audio_filepath}")


# Define the main command using click
@click.command()
@click.argument(
    "srt_filepath", type=click.Path(exists=True)
)  # Use click.Path for validation
@click.argument("output_audio_filepath", type=click.Path())  # Use click.Path for output
@click.option(
    "--engine",
    default="edge-tts",
    help="TTS engine to use (currently only 'edge-tts' is supported).",
)
@click.option(
    "--voice",
    default="vi-VN-HoaiMyNeural",
    help="Voice to use for the TTS engine.",
)
@click.option(
    "--rate",
    default="+30%",
    help="Speech rate for the TTS engine (e.g., '+50%' for 50% faster).",
)
@click.option(
    "--lang",
    default="vi",
    help="Language code (currently not used by edge-tts but kept for compatibility).",
)
def main(srt_filepath, output_audio_filepath, engine, voice, rate, lang):
    """
    Convert an SRT file to an audio file using TTS.

    SRT_FILEPATH: Path to the input SRT file.
    OUTPUT_AUDIO_FILEPATH: Path for the output audio file (e.g., output.mp3).
    """
    srt_to_audio(
        srt_filepath=srt_filepath,
        output_audio_filepath=output_audio_filepath,
        engine=engine,
        voice=voice,
        rate=rate,
        lang=lang,
    )


if __name__ == "__main__":
    main()

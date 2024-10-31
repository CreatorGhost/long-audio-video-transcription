from openai import OpenAI
import os
import logging
import subprocess
import json
import time
from pydub import AudioSegment
import argparse

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize the OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))



def compress_audio(input_file, output_file):
    try:
        logger.info(f"Compressing audio: {input_file}")
        start_time = time.time()
        command = [
            'ffmpeg',
            '-i', input_file,
            '-vn',
            '-map_metadata', '-1',
            '-ac', '1',
            '-c:a', 'libopus',
            '-b:a', '12k',
            '-application', 'voip',
            output_file
        ]
        result = subprocess.run(command, check=True, capture_output=True, text=True)
        end_time = time.time()
        compression_time = end_time - start_time
        logger.info(f"Compression completed: {output_file}")
        logger.info(f"Compression time: {compression_time:.2f} seconds")
        return result.stdout
    except subprocess.CalledProcessError as e:
        logger.error(f"FFmpeg command failed: {e.stderr}")
        raise
    except Exception as e:
        logger.error(f"An error occurred during audio compression: {str(e)}")
        raise

def split_audio(input_file, chunk_length_ms):  # 30 minutes in milliseconds
    audio = AudioSegment.from_file(input_file)
    chunks = []
    for i, chunk in enumerate(audio[::chunk_length_ms]):
        chunk_name = f"chunk_{i}.ogg"
        chunk.export(chunk_name, format="ogg")
        chunks.append(chunk_name)
    return chunks

def transcribe_chunk(file_path):
    try:
        logger.info(f"Transcribing chunk: {file_path}")
        with open(file_path, "rb") as audio_file:
            transcript = client.audio.transcriptions.create(
                model="whisper-1", 
                file=audio_file,
                response_format="verbose_json"
            )
        return transcript
    except Exception as e:
        logger.error(f"Error transcribing chunk {file_path}: {str(e)}")
        raise

def format_timestamp(seconds):
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    seconds = seconds % 60
    return f"{hours:02d}:{minutes:02d}:{seconds:06.3f}"

def process_audio(input_file, compressed_file):
    if not os.path.exists(compressed_file):
        logger.info("Compressing audio...")
        compress_audio(input_file, compressed_file)
    else:
        logger.info("Compressed file already exists. Skipping compression.")
    return compressed_file

def process_chunks(compressed_file):
    logger.info("Splitting audio into chunks...")
    chunks = split_audio(compressed_file, 30 * 60 * 1000)
    
    all_segments = []
    for i, chunk in enumerate(chunks):
        logger.info(f"Processing chunk {i+1}/{len(chunks)}")
        transcript = transcribe_chunk(chunk)
        chunk_start_time = i * 30 * 60  # 30 minutes in seconds
        for segment in transcript.segments:
            segment.start += chunk_start_time
            segment.end += chunk_start_time
        all_segments.extend(transcript.segments)
    return chunks, all_segments

def save_transcript(segments, output_file):
    logger.info("Combining transcripts...")
    with open(output_file, "w") as f:
        for segment in segments:
            start_time = format_timestamp(segment.start)
            end_time = format_timestamp(segment.end)
            f.write(f"[{start_time} --> {end_time}] {segment.text}\n")
    logger.info(f"Full transcript saved to: {output_file}")

def save_transcript_json(segments, output_file):
    logger.info("Saving transcript to JSON...")
    json_output = output_file.replace('.txt', '.json')
    transcript_data = {
        'segments': [
            {
                'start_time': format_timestamp(segment.start),
                'end_time': format_timestamp(segment.end),
                'text': segment.text,
                'start_seconds': segment.start,
                'end_seconds': segment.end
            }
            for segment in segments
        ]
    }
    
    with open(json_output, 'w', encoding='utf-8') as f:
        json.dump(transcript_data, f, ensure_ascii=False, indent=2)
    logger.info(f"JSON transcript saved to: {json_output}")

def cleanup_chunks(chunks):
    for chunk in chunks:
        os.remove(chunk)

def main():
    # Set up argument parser
    parser = argparse.ArgumentParser(description='Transcribe audio/video files using OpenAI Whisper')
    parser.add_argument('--input', type=str, required=True,
                       help='Path to input audio/video file')
    parser.add_argument('--output', type=str, default='.',
                       help='Path to output directory (default: current directory)')
    parser.add_argument('--model', type=str, default='whisper-1',
                       help='Whisper model to use (default: whisper-1)')
    parser.add_argument('--chunk_size', type=int, default=30,
                       help='Size of chunks in minutes (default: 30)')
    
    args = parser.parse_args()
    
    # Create output directory if it doesn't exist
    os.makedirs(args.output, exist_ok=True)
    
    # Construct file paths
    input_file = args.input
    output_file = os.path.join(args.output, "transcript.txt")
    compressed_file = os.path.join(args.output, "compressed_audio.ogg")
    
    try:
        compressed_file = process_audio(input_file, compressed_file)
        chunks, all_segments = process_chunks(compressed_file)
        save_transcript(all_segments, output_file)
        save_transcript_json(all_segments, output_file)
        cleanup_chunks(chunks)
    except Exception as e:
        logger.error(f"Process failed: {str(e)}")

if __name__ == "__main__":
    main()
      
# Audio Video Transcriber

A robust tool for transcribing long audio and video files into text using OpenAI's Whisper model. This tool handles large media files by automatically compressing, chunking, and processing them efficiently.

## Features

- 🎥 Supports both audio and video file formats
- ⚡ Efficient processing of large files through smart chunking
- 🔄 Automatic compression to reduce processing time
- 📝 Outputs in both TXT and JSON formats
- 🎯 High accuracy using OpenAI's Whisper model
- 💪 Memory-efficient processing of long-duration files

## Prerequisites

- Python 3.11 or higher
- FFmpeg installed on your system
- Required Python packages (see `requirements.txt`)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/audio-video-transcriber.git
cd audio-video-transcriber
```

2. Install the required dependencies:
```bash
pip install -r requirements.txt
```

3. Ensure FFmpeg is installed on your system:
- **Windows**: Download from [FFmpeg website](https://ffmpeg.org/download.html)
- **Mac**: `brew install ffmpeg`
- **Linux**: `sudo apt-get install ffmpeg`

## Usage

```bash
python transcribe.py --input path/to/your/file.mp4 --output path/to/output
```

### Options

- `--input`: Path to input audio/video file (required)
- `--output`: Path to output directory (default: current directory)
- `--model`: Whisper model size (default: base)
- `--chunk_size`: Size of chunks in minutes (default: 10)
- `--format`: Output format (txt, json, or both) (default: both)

## Output

The tool generates two types of output files:
- `transcript.txt`: Plain text transcription
- `transcript.json`: JSON format with timestamps and confidence scores

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- [OpenAI Whisper](https://github.com/openai/whisper) for the transcription model
- FFmpeg for media processing

Project Link: [https://github.com/yourusername/audio-video-transcriber](https://github.com/yourusername/audio-video-transcriber)
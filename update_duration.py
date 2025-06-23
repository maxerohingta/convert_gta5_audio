import json
import subprocess
import re
from pathlib import Path

# Directory containing audio files
AUDIO_DIR = Path('converted_m4a')

# Read JSON file
with open('new_sim_radio_stations.json', 'r', encoding='utf-8') as file:
    data = json.load(file)

def get_total_duration(path: Path) -> float:
    cmd = [
        'ffprobe',
        '-v', 'error',
        '-show_entries', 'format=duration',
        '-of', 'default=noprint_wrappers=1:nokey=1',
        str(path)
    ]
    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if result.stderr:
        print(f"ffprobe error for {path}: {result.stderr}")
        return -1.0
    return float(result.stdout.strip())

def get_audible_duration(file_path: Path, total_duration: float, silence_threshold="-14dB", silence_duration="0.5", analysis_tail=8) -> float:
    try:
        start_time = max(0, total_duration - analysis_tail)

        command = [
            "ffmpeg", "-ss", str(start_time), "-i", str(file_path),
            "-af", f"silencedetect=noise={silence_threshold}:d={silence_duration}",
            "-f", "null", "-"
        ]

        result = subprocess.run(command, stderr=subprocess.PIPE, stdout=subprocess.PIPE, text=True)
        output = result.stderr

        silence_start_matches = re.findall(r"silence_start: (\d+\.?\d*)", output)
        if not silence_start_matches:
            return total_duration  # If no silence is detected, return full duration

        silence_start = float(silence_start_matches[-1])
        audible_duration = start_time + silence_start
        return min(audible_duration, total_duration)

    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return -1.0

# Update duration for tracks with duration == -1
for track_list in data['trackLists']:
    for track in track_list['tracks']:
        if 'duration' in track and track['duration'] == -1:
            track_path = track.get('path', '')
            if track_path == 'N/A':
                print(f"Skipping track {track['id']} with invalid path")
                continue

            # Construct full path to the audio file
            audio_file = AUDIO_DIR / f"{track_path}.m4a"
            
            if not audio_file.exists():
                print(f"File not found: {audio_file}")
                continue

            # Get total duration
            total_duration = get_total_duration(audio_file)
            if total_duration == -1.0:
                print(f"Failed to get total duration for {audio_file}")
                continue

            # Get audible duration (excluding silence)
            audible_duration = get_audible_duration(audio_file, total_duration)
            if audible_duration == -1.0:
                print(f"Failed to get audible duration for {audio_file}")
                continue

            # Round duration to 3 decimal places and strip trailing zeros
            formatted_duration = f"{audible_duration:.3f}".rstrip('0').rstrip('.')
            track['duration'] = float(formatted_duration)
            print(f"Updated track {track['id']}: duration set to {formatted_duration} seconds")

# Save updated JSON
with open('new_sim_radio_stations.json', 'w', encoding='utf-8') as file:
    json.dump(data, file, indent=2, ensure_ascii=False)

print("Processing complete. Updated JSON saved.")

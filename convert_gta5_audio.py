import json
import os
import re
import subprocess
from concurrent.futures import ProcessPoolExecutor, as_completed

def check_track_files(json_file_path, base_directory):
    """
    Checks for the presence of track files listed in the JSON within the specified directory.
    Skips tracks whose paths start with directories from the exclusion list.

    :param json_file_path: Path to the JSON file containing track data
    :param base_directory: Base directory for searching track files
    :return: List of dictionaries with information about found/missing files and the number of skipped tracks
    """
    # List of excluded directories
    EXCLUDED_DIRS = {
        # 'dlc_23_2',
        # 'dlc_24-1',
        # 'dlc_battle_music',
        # 'dlc_christmas2017',
        # 'dlc_hei4',
        # 'dlc_hei4_music',
        # 'dlc_heist3',
        # 'dlc_mpsum2',
        # 'dlc_radio_19_user',
        # 'dlc_security_music',
        # 'dlc_smuggler',
        # 'dlc_thelab',
        # 'dlc_tuner_music',
        # 'dlc_update',
        # 'radio_01_class_rock',
        # 'radio_02_pop',
        # 'radio_03_hiphop_new',
        # 'radio_04_punk',
        # 'radio_05_talk_01',
        # 'radio_06_country',
        # 'radio_07_dance_01',
        # 'radio_08_mexican',
        # 'radio_09_hiphop_old',
        # 'radio_11_talk_02',
        # 'radio_12_reggae',
        # 'radio_13_jazz',
        # 'radio_14_dance_02',
        # 'radio_15_motown',
        # 'radio_16_silverlake',
        # 'radio_17_funk'     
        # 'radio_18_90s_rock',
        # 'radio_adverts',
        # 'radio_news'        
    }
    
    # Load the JSON file
    with open(json_file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    results = []
    skipped = 0
    
    # Iterate through all trackLists in the JSON
    for track_list in data.get('trackLists', []):
        # Check for the presence of the 'tracks' key in the current trackList
        tracks = track_list.get('tracks', [])
        
        for track in tracks:
            # Get the track path
            path = track.get('path')
            if not path:
                continue
            
            # Check if the path starts with an excluded directory
            first_dir = path.split('/')[0]
            if first_dir in EXCLUDED_DIRS:
                skipped += 1
                continue
            
            src_audio_info = get_src_audio_filenames(path, base_directory)

            # Add information to results
            results.append({
                'id': track.get('id', 'N/A'),
                'original_path': path,
                'src_audio': [info['found_path'] for info in src_audio_info if info['found_path']],
                'original_filenames': [info['original_name'] for info in src_audio_info if info['found_path']],
                'track_list_id': track_list.get('id', 'N/A')
            })
    
    return results, skipped

def get_src_audio_filenames(path, base_directory):
    """
    Retrieves possible file paths for the given track and checks their existence.

    :param path: Track path from the JSON
    :param base_directory: Base directory for searching files
    :return: List of dictionaries with original and hashed file names and their found paths
    """
    # Split the path into directories and file name
    dir_path, file_name = os.path.split(path)
    
    # Get possible file names
    possible_files = possible_src_audio_names(dir_path, file_name)
    
    # Create a list of all possible paths and check their existence
    results = []
    for file_info in possible_files:
        check_name = file_info['hashed_name'] if file_info['hashed_name'] else file_info['original_name']
        if 'dir_path' in file_info:
            os.path.join(base_directory, dir_path, check_name)
            path = os.path.join(file_info['dir_path'], file_name)
        possible_paths = [
            os.path.join(base_directory, dir_path, check_name),
            os.path.join(base_directory, path, check_name)
        ]
        
        found_path = None
        for possible_path in possible_paths:
            if os.path.exists(possible_path):
                found_path = possible_path
                break
                
        results.append({
            'original_name': file_info['original_name'],
            'hashed_name': file_info['hashed_name'],
            'found_path': found_path
        })

    return results

def check_hardcoded_hash(dir_path, file_name):
    mappings = {
        ("dlc_update", "tape_loop_alt"): ["0x04A1DDBA.wav", "0x185C7B1E.wav"],
        ("dlc_update", "wwfm_p3_start"): ["0x0A99A529.wav", "0x02A4FDD0.wav"],
        ("radio_13_jazz", "wwfm_p1"): ["0x04A02233.wav", "0x120DAFC1.wav"],
        ("radio_13_jazz", "wwfm_p2"): ["0x1EDECB2F.wav", "0x117A33D2.wav"],
        ("radio_13_jazz", "wwfm_p3"): ["0x15ED4708.wav", "0x032BC446.wav"],
        ("radio_13_jazz", "wwfm_p4"): ["0x1E4AFD9D.wav", "0x1E66F1A0.wav"],
        ("radio_14_dance_02", "flylo_part1"): ["0x0A818E80.wav", "0x17E2800E.wav"],
        ("radio_14_dance_02", "flylo_part2"): ["0x0339EC32.wav", "0x08194D53.wav"]
    }
    
    hashed_names = mappings.get((dir_path, file_name), [])
    if not hashed_names:
        return []
    
    return [
        {"original_name": f"{file_name}_left.wav", "hashed_name": hashed_names[0]},
        {"original_name": f"{file_name}_right.wav", "hashed_name": hashed_names[1]}
    ]

def check_hardcoded(dir_path, file_name):
    hardcoded_hash = check_hardcoded_hash(dir_path, file_name)
    if hardcoded_hash:
        return hardcoded_hash

    if dir_path == "radio_02_pop" and file_name == "circle_in_the_sand":
        return [
            {'dir_path': "radio_01_class_rock", 'original_name': "circle_in_the_sand.wav", 'hashed_name': None}
        ]
    
    if dir_path == 'radio_02_pop/intro':
        match = re.match(r'^tell_to_my_heart_(\d{2})$', file_name)
        if match:
            number = match.group(1)
            new_name = f"tell_it_to_my_heart_{number}"
            return [{'original_name': f"{new_name}.wav", 'hashed_name': None}]

    if dir_path == 'radio_17_funk/intro':
        match = re.match(r'^heart_beat_(\d{2})$', file_name)
        if match:
            number = match.group(1)
            new_name = f"heartbeat_{number}"
            return [{'original_name': f"{new_name}.wav", 'hashed_name': None}]

    if dir_path == 'radio_02_pop/intro':
        match = re.match(r'^tape_loop_alt_(\d{2})$', file_name)
        if match:
            number = match.group(1)
            new_name = f"tape_loop_{number}"
            return [{'original_name': f"{new_name}.wav", 'hashed_name': None}]


def possible_src_audio_names(dir_path, file_name):
    """
    Generates possible file names for a given track, including hashed versions.

    :param file_name: Original file name from the JSON
    :return: List of dictionaries with original and hashed file names
    """
    result = []

    hardcoded = check_hardcoded(dir_path, file_name)
    if hardcoded:
        return hardcoded
    
    # Check if the file name matches the pattern motomami_dj_solo_##
    match = re.match(r'^motomami_dj_solo_(\d{2})$', file_name)
    if match:
        number = match.group(1)
        left_name = f"dj_solo_{number}_left"
        right_name = f"dj_solo_{number}_right"
        return [
            {'original_name': f"{left_name}.wav", 'hashed_name': f"{rockstar_audio_name_hash(left_name)}.wav"},
            {'original_name': f"{right_name}.wav", 'hashed_name': f"{rockstar_audio_name_hash(right_name)}.wav"}
        ]
    
    # Check if the file name matches the pattern (text_)takeover_djsolo_##
    match = re.match(r'^(?:(.*?)_)?takeover_djsolo_(\d{2})$', file_name)
    if match:
        prefix = match.group(1) or ''
        number = match.group(2)
        new_name = f"{prefix.upper() + '_' if prefix else ''}MONO_TAKEOVER_SOLO_{number}.wav"
        return [{'original_name': new_name, 'hashed_name': None}]
    
    # Check if the file name matches the pattern (text_)djsolo_##
    match = re.match(r'^(?:(.*?)_)?djsolo_(\d{2})$', file_name)
    if match:
        prefix = match.group(1) or ''
        number = match.group(2)
        new_name = f"{prefix.upper() + '_' if prefix else ''}MONO_SOLO_{number}.wav"
        return [{'original_name': new_name, 'hashed_name': None}]
    
    # Check if the file name matches the pattern dj_mono_solo_rls_launch_##
    match = re.match(r'^dj_mono_solo_rls_launch_(\d{2})$', file_name)
    if match:
        number = match.group(1)
        new_name = f"dj_mono_solo_launch_{number}"
        return [{'original_name': f"{new_name}.wav", 'hashed_name': f"{rockstar_audio_name_hash(new_name)}.wav"}]
    
    # Check if the file name matches the pattern dj_mono_solo_rls_post_launch_##
    match = re.match(r'^dj_mono_solo_rls_post_launch_(\d{2})$', file_name)
    if match:
        number = match.group(1)
        new_name = f"dj_mono_solo_post_launch_{number}"
        return [{'original_name': f"{new_name}.wav", 'hashed_name': f"{rockstar_audio_name_hash(new_name)}.wav"}]

    # If the file name does not match any pattern
    return [
        {'original_name': file_name.upper() + '.wav', 'hashed_name': None},
        {'original_name': file_name, 'hashed_name': f"{rockstar_audio_name_hash(file_name)}.wav"},
        {'original_name': f"{file_name}_left", 'hashed_name': f"{rockstar_audio_name_hash(file_name + '_left')}.wav"},
        {'original_name': f"{file_name}_right", 'hashed_name': f"{rockstar_audio_name_hash(file_name + '_right')}.wav"}
    ]

def joaat(s: str) -> int:
    """
    Implements the joaat hash function for generating file name hashes.

    :param s: Input string to hash
    :return: Integer hash value
    """
    k = s.lower()
    h = 0

    for char in k:
        h += ord(char)
        h &= 0xFFFFFFFF
        h += (h << 10)
        h &= 0xFFFFFFFF
        h ^= (h >> 6)

    h += (h << 3)
    h &= 0xFFFFFFFF
    h ^= (h >> 11)
    h += (h << 15)
    h &= 0xFFFFFFFF

    return h

def rockstar_audio_name_hash(name):
    """
    Generates a hashed file name using the joaat algorithm, formatted as a hexadecimal string.

    :param name: Input file name to hash
    :return: Hexadecimal string of the hashed value
    """
    hash_value = joaat(name) & 0x1fffffff
    result = f"0x{hash_value:08X}"
    return result

def run_ffmpeg_conversion(input_files, output_file):
    """
    Runs FFmpeg to convert one or two input WAV files to M4A format.
    For one input file, performs direct conversion with bitrate 192k for stereo or 128k for mono.
    For two input files, merges them into a stereo output with 192k bitrate.
    Prints filename (without path) and channel format (mono/stereo).
    Suppresses FFmpeg console output.

    :param input_files: List of one or two input WAV file paths
    :param output_file: Path for the output M4A file
    :raises subprocess.CalledProcessError: If FFmpeg conversion fails
    """
    if len(input_files) == 1:
        channels = get_audio_channels(input_files[0])
        filename = os.path.basename(input_files[0])
        print(f"Processing {filename} ({channels})")
        
        # Single file conversion with dynamic bitrate
        bitrate = '192k' if channels == 'stereo' else '128k'
        command = [
            'ffmpeg', '-i', input_files[0],
            '-y', '-c:a', 'libfdk_aac', '-b:a', bitrate,
            output_file
        ]
    elif len(input_files) == 2:
        filename1 = os.path.basename(input_files[0])
        filename2 = os.path.basename(input_files[1])
        print(f"Processing {filename1} and {filename2} (merging to stereo)")
        
        # Stereo merge from two mono files
        command = [
            'ffmpeg', '-i', input_files[0], '-i', input_files[1],
            '-y', '-filter_complex', '[0:a][1:a]amerge=inputs=2[a]',
            '-map', '[a]',
            '-c:a', 'libfdk_aac', '-b:a', '192k',
            output_file
        ]
    else:
        raise ValueError(f"Expected 1 or 2 input files, got {len(input_files)}")

    # Run FFmpeg with suppressed output
    subprocess.run(
        command,
        check=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )

def convert_to_m4a(results, output_directory, max_workers=os.cpu_count()):
    """
    Converts found WAV files to M4A format in parallel and saves them in the specified output directory,
    preserving the directory structure from the original path.

    :param results: List of dictionaries with track information and found file paths
    :param output_directory: Directory where the converted M4A files will be saved
    :param max_workers: Maximum number of parallel FFmpeg processes (default: 4)
    """
    # Pre-create all necessary output directories to avoid race conditions
    tasks = []
    for result in results:
        if not result['src_audio']:
            print(f"Skipping track {result['id']} (no files found)")
            continue

        # Normalize the original path for OS compatibility
        norm_path = os.path.normpath(result['original_path'])
        # Split into directory and base name
        dir_path, base_name = os.path.split(norm_path)
        # Remove any existing extension
        base_name, _ = os.path.splitext(base_name)
        # Form the output filename with .m4a extension
        output_base_name = base_name + '.m4a'
        # Form the relative path
        relative_path = os.path.join(dir_path, output_base_name)
        # Form the full output path
        output_path = os.path.join(output_directory, relative_path)
        # Create necessary directories
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        tasks.append((result['id'], result['src_audio'], output_path))

    # Run conversions in parallel using ProcessPoolExecutor
    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        future_to_track = {
            executor.submit(run_ffmpeg_conversion, src_audio, output_path): track_id
            for track_id, src_audio, output_path in tasks
        }
        
        for future in as_completed(future_to_track):
            track_id = future_to_track[future]
            try:
                future.result()  # Wait for the conversion to complete
                print(f"Successfully converted track {track_id} to {output_path}")
            except (subprocess.CalledProcessError, ValueError) as e:
                print(f"Failed to convert track {track_id}: {e}")

def get_audio_channels(filename):
    """
    Determines if an audio file is mono or stereo using FFmpeg.

    :param filename: Path to the audio file (e.g., WAV)
    :return: str, either 'mono' or 'stereo'
    :raises ValueError: If the channel layout cannot be determined or FFmpeg fails
    """
    try:
        # Run FFmpeg command to get file info, capturing stderr
        result = subprocess.run(
            ['ffmpeg', '-i', filename],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.PIPE,
            text=True,
            check=False  # Don't raise an error, as FFmpeg returns non-zero exit code due to no output file
        )

        # Parse stderr for channel layout
        stderr_output = result.stderr
        channel_match = re.search(r'Stream #0:0: Audio:.*?, \d+ Hz, (mono|stereo),', stderr_output)

        if channel_match:
            return channel_match.group(1)
        else:
            raise ValueError(f"Could not determine channel layout for {filename}")

    except subprocess.CalledProcessError as e:
        raise ValueError(f"FFmpeg failed to process {filename}: {e}")
    except FileNotFoundError:
        raise ValueError("FFmpeg executable not found. Ensure FFmpeg is installed and accessible.")

def print_detailed_results(results):
    """
    Prints detailed information about the track file check results.

    :param results: List of dictionaries with track information and found file paths
    """
    for result in results:
        status = "Found" if result['src_audio'] else "Missing"
        print(f"{status}:")
        if result['src_audio']:
            for src, orig in zip(result['src_audio'], result['original_filenames']):
                print(f"  Found file: {src}")
                print(f"  Original name: {orig}")
        print(f"  Original path: {result['original_path']}")
        print(f"  ID: {result['id']}, TrackList: {result['track_list_id']}")
        print("-" * 50)
    
# Example usage
if __name__ == "__main__":
    json_file = "new_sim_radio_stations.json"
    base_dir = "/Users/alexeyvorobyov/Developer/My/SimRadio_TODO/raw_gta5_sounds"
    output_dir = "/Users/alexeyvorobyov/Downloads/converted_m4a"

    results, skipped = check_track_files(json_file, base_dir)
    
    # Print results
    found = sum(1 for r in results if r['src_audio'])
    print(f"Checked {len(results)} tracks. Found: {found}, Missing: {len(results) - found}")
    print(f"Skipped {skipped} tracks (excluded directories)")
    
    # Print detailed information
    print_detailed_results(results)

    # Convert found files to M4A in parallel
    convert_to_m4a(results, output_dir)
    
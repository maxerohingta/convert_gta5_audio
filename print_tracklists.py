import json
from collections import defaultdict

def load_json_data(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return json.load(file)

def find_tracklists(tracklist_ids, data):
    results = {}
    for tracklist in data['trackLists']:
        if tracklist['id'] in tracklist_ids:
            track_ids = []
            for track in tracklist['tracks']:
                if 'id' in track:
                    track_ids.append(track['id'])
                elif 'trackList' in track:
                    track_ids.append(f"{track['trackList']} (reference)")
            
            sorted_tracks = sorted(track_ids)
            results[tracklist['id']] = {
                'track_count': len(tracklist['tracks']),
                'track_ids': sorted_tracks
            }
    return results

def find_shared_tracks(results):
    track_to_tracklists = defaultdict(list)
    for tracklist_id, info in results.items():
        for track_id in info['track_ids']:
            if not track_id.endswith('(reference)'):
                track_to_tracklists[track_id].append(tracklist_id)
    return {track: tracklists for track, tracklists in track_to_tracklists.items() if len(tracklists) > 1}

def find_unique_tracks(results):
    # Создаем словарь для хранения уникальных треков по треклистам
    tracklist_to_unique_tracks = defaultdict(list)
    all_tracks = defaultdict(int)
    
    # Сначала подсчитываем общее количество вхождений каждого трека
    for tracklist_id, info in results.items():
        for track_id in info['track_ids']:
            if not track_id.endswith('(reference)'):
                all_tracks[track_id] += 1
    
    # Затем находим уникальные треки (которые встречаются только в одном треклисте)
    for tracklist_id, info in results.items():
        for track_id in info['track_ids']:
            if not track_id.endswith('(reference)') and all_tracks[track_id] == 1:
                tracklist_to_unique_tracks[tracklist_id].append(track_id)
    
    return tracklist_to_unique_tracks

def main():
    data = load_json_data('converted_m4a/new_sim_radio_stations.json')
    
    tracklist_ids = [
        # "dlc_security_music_hiphop_new_dd_general",
        # "dlc_security_music_hiphop_new_pl_general",
        # "radio_03_hiphop_new_core_music",
        # "radio_03_hiphop_new_core_music_intro",
        "radio_03_hiphop_new_dd_djsolo_launch",
        "radio_03_hiphop_new_dd_djsolo_post_launch",
        # "radio_03_hiphop_new_dd_music_launch",
        # "radio_03_hiphop_new_dd_music_launch_intro",
        # "radio_03_hiphop_new_dd_music_post_launch",
        # "radio_03_hiphop_new_dd_music_post_launch_intro",
        # "radio_03_hiphop_new_dd_music_post_launch_update",
        # "radio_03_hiphop_new_djsolo",
        # "radio_03_hiphop_new_general",
        # "radio_03_hiphop_new_idents",
        # "radio_03_hiphop_new_time_evening",
        # "radio_03_hiphop_new_time_morning",
        # "radio_03_hiphop_new_to_ad",
        # "radio_03_hiphop_new_to_news"
    ]
    
    results = find_tracklists(tracklist_ids, data)
    
    if not results:
        print("Ни один из указанных треклистов не найден.")
        return
    
    print("\nРезультаты:")
    for tracklist_id, info in results.items():
        print(f"\nТреклист: {tracklist_id}")
        print(f"Количество треков: {info['track_count']}")
        print("ID треков (отсортировано):")
        for i, track_id in enumerate(info['track_ids'], 1):
            print(f"  {i}. {track_id}")
    
    # Вывод общих треков
    shared_tracks = find_shared_tracks(results)
    if shared_tracks:
        print("\nТреки, встречающиеся в нескольких треклистах:")
        for track, tracklists in shared_tracks.items():
            print(f"\nТрек: {track}")
            print("Встречается в треклистах:")
            for tracklist in tracklists:
                print(f"  - {tracklist}")
    else:
        print("\nНет треков, которые встречаются в нескольких треклистах.")
    
    # Вывод уникальных треков
    unique_tracks = find_unique_tracks(results)
    if unique_tracks:
        print("\nУникальные треки по треклистам:")
        for tracklist_id, tracks in unique_tracks.items():
            print(f"\nТреклист: {tracklist_id}")
            print("Уникальные треки:")
            for i, track in enumerate(sorted(tracks), 1):
                print(f"  {i}. {track}")
    else:
        print("\nНет уникальных треков (все треки встречаются в нескольких треклистах).")

if __name__ == "__main__":
    main()
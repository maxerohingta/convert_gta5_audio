import json

def load_json_data(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return json.load(file)

def find_tracklists(tracklist_ids, data):
    results = {}
    for tracklist in data['trackLists']:
        if tracklist['id'] in tracklist_ids:
            track_ids = []
            for track in tracklist['tracks']:
                # Проверяем разные форматы треков (некоторые имеют прямой ID, другие ссылаются через trackList)
                if 'id' in track:
                    track_ids.append(track['id'])
                elif 'trackList' in track:  # Для ссылок на другие треклисты
                    track_ids.append(f"{track['trackList']} (reference)")
            
            results[tracklist['id']] = {
                'track_count': len(tracklist['tracks']),
                'track_ids': track_ids
            }
    return results

def main():
    # Загрузка данных из файла
    data = load_json_data('converted_m4a/new_sim_radio_stations.json')
    
    tracklist_ids = [
        "dlc_security_music_hiphop_new_dd_general",
        "dlc_security_music_hiphop_new_pl_general",
        "radio_03_hiphop_new_core_music",
        "radio_03_hiphop_new_core_music_intro",
        "radio_03_hiphop_new_dd_djsolo_launch",
        "radio_03_hiphop_new_dd_djsolo_post_launch",
        "radio_03_hiphop_new_dd_music_launch",
        "radio_03_hiphop_new_dd_music_launch_intro",
        "radio_03_hiphop_new_dd_music_post_launch",
        "radio_03_hiphop_new_dd_music_post_launch_intro",
        "radio_03_hiphop_new_dd_music_post_launch_update",
        "radio_03_hiphop_new_djsolo",
        "radio_03_hiphop_new_general",
        "radio_03_hiphop_new_idents",
        "radio_03_hiphop_new_time_evening",
        "radio_03_hiphop_new_time_morning",
        "radio_03_hiphop_new_to_ad",
        "radio_03_hiphop_new_to_news"
    ]
    
    # Находим и выводим информацию
    results = find_tracklists(tracklist_ids, data)
    
    if not results:
        print("Ни один из указанных треклистов не найден.")
        return
    
    print("\nРезультаты:")
    for tracklist_id, info in results.items():
        print(f"\nТреклист: {tracklist_id}")
        print(f"Количество треков: {info['track_count']}")
        print("ID треков:")
        for i, track_id in enumerate(info['track_ids'], 1):
            print(f"  {i}. {track_id}")

if __name__ == "__main__":
    main()
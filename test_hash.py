import ctypes
def joaat(s: str) -> int:
    k = s.lower()
    h = 0

    for char in k:
        h += ord(char)
        h &= 0xFFFFFFFF  # Ensure 32-bit
        h += (h << 10)
        h &= 0xFFFFFFFF
        h ^= (h >> 6)

    h += (h << 3)
    h &= 0xFFFFFFFF
    h ^= (h >> 11)
    h += (h << 15)
    h &= 0xFFFFFFFF

    return h

def rockstar_audio_name_hash(name) :
    return joaat(name) & 0x1fffffff


#  dj_mono_solo_rls_launch_ -> dj_mono_solo_launch_
# ищем dj_mono_solo_rls_post_launch_01/0x1A2B6A28
test = [
    'dj_mono_solo_rls_post_launch_01',
    'dj_mono_solo_post_launch_01',
    ]

# Вычисляем и выводим хэши в шестнадцатеричном виде
for s in test:
    hash_value = rockstar_audio_name_hash(s)
    hex_value = f"0x{hash_value:08X}"  # Форматируем как 8-значное шестнадцатеричное число с префиксом 0x
    print(f"'{s}': {hex_value}")

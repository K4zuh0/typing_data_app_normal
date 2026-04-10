import time
import csv
from pynput import keyboard
import pygame  # 音声再生用

# --- 設定 ---
AUDIO_FILE = "long_stress_audio_target1_9.mp3"  # 再生する音声ファイル名
OUTPUT_FILENAME = "N13_stress.csv" # 保存するCSV名

# --- 初期化 ---
pygame.mixer.init()
try:
    pygame.mixer.music.load(AUDIO_FILE)
except FileNotFoundError:
    print(f"エラー: 音声ファイル '{AUDIO_FILE}' が見つかりません！同じフォルダに置いてください。")
    exit()

log_data = []
pressed_keys = set()
recording = False
start_time = 0

print(f"--- ストレス実験用収集ツール ---")
print(f"保存先: {OUTPUT_FILENAME}")
print(f"音声: {AUDIO_FILE}")
print("------------------------------------------------")
print("【Space】キーを押すと、音楽と記録が同時にスタートします。")
print("【Esc】  キーを押すと、終了して保存します。")
print("------------------------------------------------")

def get_key_name(key):
    try:
        return key.char
    except AttributeError:
        return str(key).replace('Key.', '')

def on_press(key):
    global recording, start_time

    # --- 開始トリガー (Space) ---
    if not recording:
        if key == keyboard.Key.space:
            print("\n>>> 実験スタート！音楽再生中... <<<")
            recording = True
            start_time = time.time()
            # ★ここで音楽スタート
            pygame.mixer.music.play()
            return
        else:
            # 開始前は他のキーを無視
            return

    # --- 記録中 ---
    if key in pressed_keys: return
    pressed_keys.add(key)

    # 経過時間 (ミリ秒) で記録
    current_time = (time.time() - start_time) * 1000

    log_data.append([get_key_name(key), 'press', current_time])

def on_release(key):
    global recording

    if not recording: return

    if key in pressed_keys:
        pressed_keys.remove(key)

    # 終了トリガー (Esc)
    if key == keyboard.Key.esc:
        print("\n>>> 実験終了・保存中... <<<")
        pygame.mixer.music.stop() # ★音楽ストップ
        return False # リスナー停止

    current_time = (time.time() - start_time) * 1000
    log_data.append([get_key_name(key), 'release', current_time])

# --- 実行 ---
with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
    listener.join()

# --- 保存 ---
with open(OUTPUT_FILENAME, 'w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    writer.writerow(['key', 'event_type', 'timestamp_ms'])
    writer.writerows(log_data)

print(f"保存完了！ (所要時間: {log_data[-1][2]/1000:.2f}秒)")
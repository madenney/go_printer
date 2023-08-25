
import os
import re

import time
import math
import asyncio
import subprocess


from PIL import Image, ImageOps, ImageDraw, ImageFont

import pyclip
import pygame
pygame.mixer.init()
piece_sound = pygame.mixer.Sound('assets/mixkit-typewriter-soft-click.wav')

import pyautogui
# pygetwindow fork that works on linux:
import pywinctl as gw

import common as c

GAME_FILTER = "Lee Sedol"
LIMIT = 1100
SORT_BY_DATE = True

AUDIO_SOURCE = 'alsa_output.usb-Razer_Razer_BlackShark_V2_Pro-00.analog-stereo.monitor'
#AUDIO_SOURCE = 'alsa_output.pci-0000_00_1f.3.analog-stereo.monitor'
BIGO_PATH = "C:/Program Files (x86)/BiGo/BiGo Assistant Full/BiGoAssistant.exe"
OUTPUT_DIR = "/home/matt/Projects/garkiver/output"

PRE_GAME_BUFFER = 1.2
POST_GAME_BUFFER = 2

CONTROL_WINDOW_TITLE = "BiGo Assistant Full Edition - Control Panel"
GAMES_WINDOW_TITLE = "Games List"
CONTROL_X = 2000
CONTROL_Y = 100
GAMES_X = 2000
GAMES_Y = 800
GAME_WINDOW_HEIGHT = 1012
GAME_WINDOW_WIDTH = 994

def get_window(window_name):
    print("Getting ", window_name)
    window = None
    count = 0
    while window is None:
        try:
            window = gw.getWindowsWithTitle(window_name)[0]
            print(f'Found {window_name}')
            return window
        except Exception:
            print(f"waiting for {window_name} to load... {count}",end='\r')
            time.sleep(0.2)
            count += 1   

def filter_data(games_window):
    print("filter data")

def create_game():
    print("Create game")

def start_recording():
    print("Starting recording")

def play_game(params):
    print("Play game")
    print("params: ", params)

def add_overlay(index, video_path, white_player, black_player, date):
    
    image = Image.new("RGBA", (GAME_WINDOW_WIDTH, GAME_WINDOW_HEIGHT), color=(0,0,0,0))
    draw = ImageDraw.Draw(image)
    
    draw.rectangle([0,GAME_WINDOW_HEIGHT-20,GAME_WINDOW_WIDTH,GAME_WINDOW_HEIGHT],fill=(0,0,0))
    font = ImageFont.truetype("./assets/cour_bold.ttf", 14)
    text_color = (255, 255, 255)  # White
    player_text_position = (20, GAME_WINDOW_HEIGHT - 15)
    player_text = f"W - {white_player}   vs   B - {black_player}"
    date_text_position = (GAME_WINDOW_WIDTH - 90, GAME_WINDOW_HEIGHT - 16)
    draw.text(player_text_position, player_text, fill=text_color, font=font)
    draw.text(date_text_position, date, fill=text_color, font=font )

    image_path = os.path.join(os.path.dirname(video_path),f"{str(index)}.png")
    output_path = os.path.join(os.path.dirname(video_path),f"{str(index)}.mkv")
    image.save(image_path)

    overlay_cmd = ['ffmpeg', '-i', video_path, '-i', image_path, '-b:v', '15000k', \
        '-filter_complex', '[0:v][1:v]overlay', output_path ]
    print(" ".join(overlay_cmd))
    subprocess.run(overlay_cmd,stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    os.remove(video_path)
    os.remove(image_path)



def main():

    # add_overlay(1, '/home/matt/Projects/garkiver/output/test/test.mkv', 'joe boberson 9000 (asdf)', 'steve butterbutt (393939)', '23/13/3002')
    # exit()

    print("Opening BiGo")
    process = subprocess.Popen(["wine", BIGO_PATH])
    time.sleep(1)
    control_window = get_window(CONTROL_WINDOW_TITLE)
    control_window.moveTo(CONTROL_X,CONTROL_Y)
    
    print("Opening Games List")
    pyautogui.moveTo(CONTROL_X + 63, CONTROL_Y + 53, 0.5)
    pyautogui.click()
    pyautogui.moveTo(CONTROL_X + 63, CONTROL_Y + 135, 0.5)
    pyautogui.moveTo(CONTROL_X + 245, CONTROL_Y + 135, 0.5)
    pyautogui.click()


    games_window = get_window(GAMES_WINDOW_TITLE)
    time.sleep(0.1)
    games_window.moveTo(GAMES_X, GAMES_Y)

    # apply filter 
    pyautogui.moveTo(GAMES_X + 700, GAMES_Y + 50, 0.5)
    pyautogui.click()
    pyautogui.moveTo(GAMES_X + 163, GAMES_Y + 270, 0.5)
    pyautogui.click()

    # move to bottom filter
    for i in range(10):
        pyautogui.press('down')
    pyautogui.press('enter')

    # wait for filter to filter
    time.sleep(5)

    # Sort by date?
    if SORT_BY_DATE:
        pyautogui.moveTo(GAMES_X + 160, GAMES_Y + 88, 0.5)
        pyautogui.click()
        time.sleep(0.2)

    # create output directory
    output_dir = c.create_output_dir(OUTPUT_DIR)

    game_count = 0
    pages = math.floor(LIMIT / 100)
    print("Pages: ", pages)
    for page_index in range(pages):
        # iterate through games list
        for game_index in range(3):

            print(f"{game_count}/{LIMIT}")
            pyautogui.moveTo(GAMES_X + 15, GAMES_Y + 15, 0.5)
            pyautogui.click()
            pyautogui.press('down')
            time.sleep(0.1)

            # get game info
            pyautogui.hotkey('ctrl', 'c')
            line = pyclip.paste(text=True)

            # get date first
            regex_pattern = r'\d{1,2}[/]\d{1,2}[/]\d{4}'
            match = re.search(regex_pattern, line)
            date = None
            if match:
                date = match.group()
                print("Found date:", date)
            else:
                print("Date not found.")
                continue

            # get black player
            num_moves = line.split(" ")[-2]
            black_player = line[1:line.find(date)]
            white_player = line[line.find(date)+len(date):line.find(num_moves)]
            black_player = black_player.strip()
            white_player = white_player.strip()

            # start game
            pyautogui.press('Enter')
            time.sleep(0.5)

            # find game window
            windows = gw.getAllWindows()
            game_window = None
            for window in windows:
                if black_player[0:5] in window.title:
                    game_window = window
            if not game_window:
                print("No game window found :(")
                continue
        
            # move and resize game window
            game_window.moveTo(0,0)
            time.sleep(0.1)
            game_window.resize(1000,1000)
            time.sleep(0.1)
            
            #click on game window for focus
            pyautogui.moveTo(80,660,0.5)
            pyautogui.click()

            coords = [74,692,GAME_WINDOW_WIDTH,GAME_WINDOW_HEIGHT]
            file_name = os.path.join(output_dir,f"{game_count}-pre-overlay.mkv")
            recording_process = c.start_recording(file_name, coords, AUDIO_SOURCE)
            time.sleep(PRE_GAME_BUFFER)

            # play game
            for i in range(int(num_moves) + 1):
                if i > 20:
                    break
                pygame.mixer.Sound.play(piece_sound)
                pyautogui.press("down")
                
            time.sleep(POST_GAME_BUFFER)
            c.end_recording(recording_process)
            game_window.close()
            time.sleep(0.2)

            add_overlay(game_count,file_name,white_player,black_player,date)

            game_count = game_count + 1
            
        # click to next page
        pyautogui.moveTo(GAMES_X + 730, GAMES_Y + 720, 0.5)
        pyautogui.click()

    print("Done.")
    process.kill()
    exit()


if __name__ == "__main__":
    asyncio.run(main())



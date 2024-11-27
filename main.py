import pydub.playback
import pygame
import tkinter as tk
import os
import sys
from collections import deque
import keyboard
import random
import cv2
from pathlib import Path
import pydub
import threading
import time

kp = keyboard.is_pressed
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (100, 100, 100)
RED = (255, 0, 0)

class YSSBGame:
    def __init__(self): ...
        # try:
        #     return getattr(self, gamemode)()
        # except AttributeError:
        #     raise ValueError(f"Wrong GameMode: {gamemode}")

    class OsuMania: ...
    class PianoTiles: 
        def __init__(self) -> None:
            pygame.init()
            pygame.mixer.init()
            self.set_up_window()

            self.keys = 'zx./'
            self.keys_count = len(self.keys)
            self.keys_prev = [False for _ in range(self.keys_count)]
            self.click_counter = [0 for _ in range(self.keys_count)]
            self.tile_size = (80, 100) # width, heigth
            self.yssb_normal = self.convert_img('yssb_normal.png', size=self.tile_size)
            self.yssb_orgasm = self.convert_img('yssb_orgasm.png', size=self.tile_size)
            self.tile_queue = deque(maxlen=10)
            self.error_click = []
            self.tile_queue.append({'key': random.randint(0, self.keys_count - 1), 'pic': self.yssb_orgasm})
            self.score = 0
            self.root.after(0, self.game_loop)
            # self.hitsound = pydub.AudioSegment.from_file(Path(__file__).parent/'hit.wav')
            # pydub.playback.play(pydub.AudioSegment.silent(duration=50))
            self.hitsound = pygame.mixer.Sound(Path(__file__).parent/'hit.wav')
            self.threads_queue = deque()
            
            self.game_over = False
            self.play_gg_sound = False

            while not len(self.tile_queue) >= self.tile_queue.maxlen: 
                self.generate_a_tile()

            for t in range(12):
                threading.Thread(target=self.play_hitsound, daemon=True).start()

        def set_up_window(self):
            self.root = tk.Tk()
            self.root.title("YSSB")
            self.window_size = (1000, 800)
            self.root.geometry(f"{self.window_size[0]}x{self.window_size[1]}")

            embed = tk.Frame(self.root, width=self.window_size[0], height=self.window_size[1])
            embed.pack()

            os.environ['SDL_WINDOWID'] = str(embed.winfo_id())
            os.environ['SDL_VIDEODRIVER'] = 'windib'

            # 創建 Pygame 視窗
            self.screen = pygame.display.set_mode((self.window_size[0], self.window_size[1]))
            self.title = pygame.font.Font(None, 74)
            self.key_input_display = pygame.font.Font(None, 48)
            self.numbers = pygame.font.Font(None, 24)
            self.clock = pygame.time.Clock()
        
        def convert_img(self, file_name, size):
            img = cv2.imread((str(Path(__file__).parent/file_name)))
            img = cv2.resize(img, size, interpolation=cv2.INTER_AREA)
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            img_surface = pygame.surfarray.make_surface(img)
            img_surface = pygame.transform.rotate(img_surface, 270)
            img_surface = pygame.transform.flip(img_surface, flip_x=True, flip_y=False)
            return img_surface
        
        def generate_a_tile(self):
            self.tile_queue.append({'key': random.randint(0, self.keys_count - 1), 'pic': self.yssb_normal})

        def draw_tiles(self):
            for i in range(0, len(self.tile_queue)):
                tile_rect = self.yssb_normal.get_rect(
                    center=(
                        x_pos := self.window_size[0] / 2 + (-(self.keys_count / 2) + 0.5 + self.tile_queue[i]['key']) * self.tile_size[0], 
                        y_pos := self.window_size[1] - (0.5 + i) * self.tile_size[1]
                    )
                )
                # print(x_pos, y_pos)
                self.screen.blit(self.tile_queue[i]['pic'], tile_rect)

        def play_hitsound(self):
            while True:
                if len(self.threads_queue) > 0:
                    self.threads_queue.pop().play()
                    # pydub.playback.play(self.hitsound)
                else:
                    time.sleep(1/60)

        def judge_key_input(self):
            keys_input = [kp(i) for i in self.keys]

            for i in range(len(keys_input)):
                if keys_input[i] == True and self.keys_prev[i] == False:
                    if i == self.tile_queue[1]['key']:
                        self.tile_queue[1]['pic'] = self.yssb_orgasm
                        self.generate_a_tile()
                        self.keys_prev[i] = True
                        self.threads_queue.append(self.hitsound)
                        self.click_counter[i] += 1
                        self.score += 1
                    
                    elif i != self.tile_queue[1]['key']:
                        self.game_over = True

                    text = self.key_input_display.render(self.keys[i], True, BLACK)
                    text_rect = text.get_rect(center=(self.window_size[0] * 0.95, self.window_size[1] * (0.5 + 0.1 * (-self.keys_count / 2 + i))))
                    self.screen.blit(text, text_rect)

                elif keys_input[i] == False and self.keys_prev[i] == True:
                    self.keys_prev[i] = False

                counter = self.numbers.render(str(self.click_counter[i]), True, BLACK)
                counter_rect = counter.get_rect(center=(self.window_size[0] * 0.95, self.window_size[1] * (0.55 + 0.1 * (-self.keys_count / 2 + i))))
                self.screen.blit(counter, counter_rect)

        def draw_border(self):
            pygame.draw.line(
                self.screen, BLACK, 
                (self.window_size[0] / 2 - (self.keys_count / 2) * self.tile_size[0], self.window_size[1] - self.tile_size[1]),
                (self.window_size[0] / 2 + (self.keys_count / 2) * self.tile_size[0], self.window_size[1] - self.tile_size[1]),
                width=8
            ) # judge line

            for i in range(0, self.keys_count + 1):
                pygame.draw.line(
                    self.screen, GRAY, 
                    (self.window_size[0] / 2 - (self.keys_count / 2 - i) * self.tile_size[0], 0),
                    (self.window_size[0] / 2 - (self.keys_count / 2 - i) * self.tile_size[0], self.window_size[1]),
                    width=2
                ) # borders
        
        def draw_score(self):
            score = self.title.render(f'score: {self.score}', True, BLACK)
            self.screen.blit(score, (10, 10))
                
        def draw(self):
            self.screen.fill(WHITE)
            self.judge_key_input()
            self.draw_tiles()
            self.draw_border()
            self.draw_score()
            pygame.display.flip()
            self.clock.tick(60)
        
        def gg_sound(self):
            pydub.playback.play(pydub.AudioSegment.from_wav(Path(__file__).parent/'yssb_roaring.wav'))
            self.terminate()

        def terminate(self):
            pygame.quit()
            self.root.quit()
            sys.exit()

        def game_loop(self):
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.terminate()

            if self.game_over:
                if not self.play_gg_sound: 
                    threading.Thread(target=self.gg_sound, daemon=True).start()
                    self.play_gg_sound = True

                big_yssb_orgasm = pygame.transform.scale(self.yssb_orgasm, (self.tile_size[0] * 10, self.tile_size[1] * 10))
                rect = big_yssb_orgasm.get_rect(center=(self.window_size[0] / 2, self.window_size[1] / 2))
                self.screen.blit(big_yssb_orgasm, rect)
                self.draw_score()
                pygame.display.flip()
                self.clock.tick(60)

            elif not self.game_over:
                self.play_gg_sound = False
                self.draw()
            
            self.root.after(16, self.game_loop)

if __name__ == '__main__':
    game = YSSBGame.PianoTiles()
    game.root.mainloop()
import pygame
import pytmx
import pyscroll
from dialog import DialogBox
from player import Player
from map import MapManager
from start_menu import StartMenu


class Game:
    def __init__(self):

        self.screen = pygame.display.set_mode((480, 480))
        pygame.display.set_caption('Eternal Run')

        # generer un joueur
        self.player = Player()
        self.map_manager = MapManager(self.screen, self.player, self.end_timer)
        self.dialog_box = DialogBox()
        self.start_menu = StartMenu(self.start_game)
        self.game_started = False
        self.space_sound = pygame.mixer.Sound('../audio/sfx/DIALOGSOUND.wav')

    def start_game(self):
        self.game_started = True

    def handle_input(self):
        pressed = pygame.key.get_pressed()

        if pressed[pygame.K_UP] or pressed[pygame.K_z]:
            self.player.move_up()
        elif pressed[pygame.K_DOWN] or pressed[pygame.K_s]:
            self.player.move_down()
        elif pressed[pygame.K_LEFT] or pressed[pygame.K_q]:
            self.player.move_left()
        elif pressed[pygame.K_RIGHT] or pressed[pygame.K_d]:
            self.player.move_right()

    def update(self):
        self.map_manager.update()

    def end_timer(self):
        current_time = pygame.time.get_ticks()
        delta_time = current_time - self.timer_start
        return delta_time

    def run(self):

        clock = pygame.time.Clock()

        self.timer_start = pygame.time.get_ticks()
        running = True
        while running:
            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYUP:
                    if event.key == pygame.K_SPACE:
                        if self.map_manager.endgame is False:
                            self.map_manager.check_npc_collisions(self.dialog_box)
                            self.map_manager.check_interaction_collisions()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        if self.dialog_box.input_box.active is False and self.map_manager.endgame is False:
                            self.space_sound.play()

            self.player.save_location()
            if self.game_started:
                if self.dialog_box.reading:
                    self.dialog_box.handle_input(events)
                elif not self.map_manager.sign_active:
                    self.handle_input()
            self.update()
            self.map_manager.draw()
            self.dialog_box.render(self.screen)

            if not self.game_started:
                self.start_menu.update()
                self.start_menu.draw(self.screen)

            pygame.display.flip()
            dt = clock.tick(60)

        pygame.quit()

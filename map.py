from dataclasses import dataclass
import random
import pygame
import pytmx
import pyscroll
from player import NPC, Boss, LightsGuy, DiskGiver
from dialog import Sign


@dataclass
class Portal:
    from_world: str
    origin_point: str
    target_world: str
    teleport_point: str


@dataclass
class Map:
    name: str
    walls: list[pygame.Rect]
    group: pyscroll.PyscrollGroup
    tmx_data: pytmx.TiledMap
    portals: list[Portal]
    npcs: list[NPC]
    interactions: list
    music_name: str


class MapManager:

    def __init__(self, screen, player, end_timer):
        self.maps = dict()  # "house" -> Map("house", walls, group)
        self.screen = screen
        self.player = player
        self.current_map = "Spawn"
        self.end_timer = end_timer

        # Lights in level 1
        self.lights_on = True
        self.lightswitch_time = pygame.time.get_ticks()
        self.lightswitch_sound = pygame.mixer.Sound('../audio/sfx/light-switch.mp3')
        self.lightswitch_sound.set_volume(0.05)
        self.chimney_sound = pygame.mixer.Sound('../audio/sfx/chimney_sound.mp3')
        self.chimney_sound.set_volume(0.05)

        # player inventory display:
        self.cd1 = pygame.image.load('../graphics/Tools/Morceau de CD.png').convert_alpha()
        self.cd1.set_colorkey((0, 0, 0))
        self.cd2 = pygame.image.load('../graphics/Tools/Morceau de CD2.png').convert_alpha()
        self.cd2.set_colorkey((0, 0, 0))
        self.cd3 = pygame.image.load('../graphics/Tools/Morceau de CD3.png').convert_alpha()
        self.cd3.set_colorkey((0, 0, 0))
        self.cd4 = pygame.image.load('../graphics/Tools/Morceau de CD4.png').convert_alpha()
        self.cd4.set_colorkey((0, 0, 0))
        self.cd_parts = [self.cd1, self.cd2, self.cd3, self.cd4]
        w = 32
        for index, image in enumerate(self.cd_parts):
            self.cd_parts[index] = pygame.transform.scale(image, (w, w))
        xoffset = 10
        yoffset = 5
        screen_w = 480
        self.cd1pos = (screen_w - xoffset - w / 2, yoffset)
        self.cd2pos = (self.cd1pos[0] - xoffset - w, yoffset)
        self.cd3pos = (self.cd2pos[0] - xoffset - w / 2, yoffset - w / 4)
        self.cd4pos = (self.cd3pos[0] - xoffset - w / 4, self.cd3pos[1])

        # Endgame
        self.endgame = False
        self.endgame_time = 0
        self.endgame_image = pygame.image.load('../graphics/labo/endgame_image.jpg')
        self.endgame_image = pygame.transform.scale(self.endgame_image, (480, 480))
        self.endgame_sound = pygame.mixer.Sound('../audio/music/MEDLEY.mp3')
        self.endgame_sound.set_volume(0.1)

        self.sign = None
        self.sign_active = False

        self.register_map('Spawn',
                          portals=[
                              Portal(from_world="Spawn", origin_point="passage_spawn_entry",
                                     target_world="Passage_Spawn",
                                     teleport_point="spawn_road_from_spawn"),
                              Portal(from_world="Spawn", origin_point="enter_chill_place", target_world="Chill_Place",
                                     teleport_point="spawn_chill_place_from_spawn")
                          ],
                          npcs=[
                              NPC("AI", nb_points=2, dialog=["Tu arrives de nulle part on dirait..."])
                          ],
                          music_name='dacadac.mp3')

        self.register_map('Chill_Place',
                          portals=[
                              Portal(from_world="Chill_Place", origin_point="exit_chill_place", target_world="Spawn",
                                     teleport_point="spawn_spawn_from_chill_place")
                          ],
                          music_name='dacadac.mp3')

        self.register_map('First_Level_City',
                          portals=[
                              Portal(from_world="First_Level_City", origin_point="enter_passage_spawn",
                                     target_world="Passage_Spawn",
                                     teleport_point="spawn_road_from_city"),
                              Portal(from_world="First_Level_City", origin_point="enter_secondlevel",
                                     target_world="Second_Level_City",
                                     teleport_point="spawn_sl_from_fl"),
                              Portal(from_world='First_Level_City', origin_point="parc_sl",
                                     target_world="Second_Level_City",
                                     teleport_point='spawn_parcsl'),

                              # houses and level 1
                              Portal(from_world="First_Level_City", origin_point="entry_flhouse4",
                                     target_world="flhouse4",
                                     teleport_point="spawn_flhouse4"),
                              Portal(from_world="First_Level_City", origin_point="outsidenter_flhouse4",
                                    target_world="flhouse4",
                                    teleport_point="spawn_insideflh4"),
                              Portal(from_world="First_Level_City", origin_point="entry_flhouse3",
                                     target_world="flhouse3",
                                     teleport_point="spawn_flhouse3"),
                              Portal(from_world='First_Level_City', origin_point="entry_flhouse2",
                                     target_world="flhouse2",
                                     teleport_point='spawn_flhouse2'),
                              Portal(from_world="First_Level_City", origin_point="entry_flhouse1",
                                     target_world="flhouse1",
                                     teleport_point="spawn_flhouse1"),
                              Portal(from_world='First_Level_City', origin_point="entry_firstlevel",
                                     target_world="First_Level",
                                     teleport_point='spawn_firstlevel')
                          ],
                          music_name='dacadac.mp3')

        # inside houses of lvl1 and level 1
        self.register_map('flhouse4',
                          portals=[
                              Portal(from_world="flhouse4", origin_point="exit_flhouse4",
                                     target_world="First_Level_City",
                                     teleport_point="spawn_exit_flhouse4"),
                              Portal(from_world="flhouse4", origin_point="go_outside",
                                   target_world="First_Level_City",
                                   teleport_point="spawn_outsideflh4")
                          ],
                          music_name='dacadac.mp3')

        self.register_map('flhouse3',
                          portals=[
                              Portal(from_world="flhouse3", origin_point="exit_flhouse3",
                                     target_world="First_Level_City",
                                     teleport_point="spawn_exit_flhouse3"),
                          ],
                          music_name='dacadac.mp3')

        self.register_map('flhouse2',
                          portals=[
                              Portal(from_world='flhouse2', origin_point="exit_flhouse2",
                                     target_world="First_Level_City",
                                     teleport_point='spawn_exit_flhouse2'),
                          ],
                          music_name='dacadac.mp3')

        self.register_map('flhouse1',
                          portals=[
                              Portal(from_world="flhouse1", origin_point="exit_flhouse1",
                                     target_world="First_Level_City",
                                     teleport_point="spawn_exit_flhouse1"),
                          ],
                          music_name='dacadac.mp3')

        self.register_map('First_Level',
                          portals=[
                              Portal(from_world='First_Level', origin_point="exit_firstlevel",
                                     target_world="First_Level_City",
                                     teleport_point='spawn_exit_firstlevel'),
                          ],
                          npcs=[
                              LightsGuy("AI", nb_points=1)],
                          music_name='dacadac.mp3')

        self.register_map('Passage_Spawn',
                          portals=[
                              Portal(from_world='Passage_Spawn', origin_point="enter_spawn", target_world="Spawn",
                                     teleport_point="passage_spawn_exit"),
                              Portal(from_world='Passage_Spawn', origin_point="enter_flcity",
                                     target_world="First_Level_City",
                                     teleport_point="spawn_first_level")
                          ],
                          npcs=[
                              NPC("AI", nb_points=4, dialog=["    ."])
                          ],
                          music_name='dacadac.mp3')

        self.register_map('Second_Level_City',
                          portals=[
                              Portal(from_world='Second_Level_City', origin_point="sl_enter_flcity",
                                     target_world="First_Level_City",
                                     teleport_point='spawn_sl_to_fl'),
                              Portal(from_world='Second_Level_City', origin_point="parc_fl",
                                     target_world="First_Level_City",
                                     teleport_point="spawn_parcfl"),
                              Portal(from_world='Second_Level_City', origin_point="enter_secondlevel",
                                     target_world="Second_Level",
                                     teleport_point="spawn_sl_from_slcity"),
                              Portal(from_world='Second_Level_City', origin_point="enter_passagetl",
                                     target_world="Third_Level_Start",
                                     teleport_point="spawn_passagetl_from_sl")
                          ],
                          music_name='Prod #1.mp3')

        self.register_map('Second_Level',
                          portals=[
                              Portal(from_world='Second_Level', origin_point="exit_second_level",
                                     target_world="Second_Level_City",
                                     teleport_point='spawn_slcity_from_sl'),
                          ],
                          npcs=[
                              DiskGiver("AI", nb_points=1, dialog=[
                                  "Hehey tu passe par ici pour le Cdey ?\nRépond juste à ces trois énigmes et\nje te le donnerey...",
                                  "PEUT-ÊTRE!!...",
                                  "QUESTION :",
                                  ["Parmi ces trois rimes,\nlaquelle est riche?", 2, 
                                   
                                   "Les soeurs des gens sont dans les tel-hô"
                                   "\nLes toxixos sont dans les bureaux", 
                                   "J'parle de rien comme de tout"
                                   "\npersonne n'en voit le bout",
                                   "Ça sera la même fin à tous les débuts" 
                                   "\nje cours encore après que j'ai trébuché"],

                                  ["Parmi ces trois rimes,\nlaquelle est pauvre?", 0, 
                                   
                                   "Ma baby mama me dit que j'abuse"
                                   "\nJ'récupère la balle je distribue", 
                                   'En petite tenue, ton joli collant'
                                   '\nDéfile au tel-hô, défile en talon',
                                   'La plus value, ils se la font sur le dos'
                                   '\n des plus à nu' ' des ados des adultes'],

                                  ["Parmi ces trois rimes,\nlaquelle est suffisante?", 1, 
                                   
                                   "La réussite se compte en années, les défaites en heures"
                                   "\nMais la patience est carrée donc le chemnin est d'or",
                                   "Toujours à l'affut, j'aiguise ma lame"
                                   "\nJ'écris je ne parle plus, j'ai mal à l'âme",
                                   "Le temps est là mais je ne l'ai pas entre les mains"
                                   "\nJe tends les bras mais y a que toi pour me le donner"],

                                  "Bravo! c'est important de savoir ce qu'on\nécoute. Voilà un cadeau pour te\nrécompenser. Puisse-t-il te servir."],
                                        reward='cd2')
                          ],
                          music_name='Prod #1.mp3')

        self.register_map('Third_Level_Start',
                          portals=[
                              Portal(from_world='Third_Level_Start', origin_point="enter_sl_from_passagetl",
                                     target_world="Second_Level_City", teleport_point='spawn_sl_passagetl'),
                              Portal(from_world='Third_Level_Start', origin_point="enter_tl_from_passagetl",
                                     target_world="Third_Level",
                                     teleport_point="spawn_tl_from_passagetl"),
                          ],
                          music_name='Prod #1.mp3')

        self.register_map('Third_Level',
                          portals=[
                              Portal(from_world='Third_Level', origin_point="enter_passagetl_from_tl",
                                     target_world="Third_Level_Start",
                                     teleport_point="spawn_passagetl_from_tl"),
                              Portal(from_world='Third_Level', origin_point="enter_coast_from_tl", target_world="Coast",
                                     teleport_point="spawn_coast_from_tl"),
                              Portal(from_world='Third_Level', origin_point="enter_trap_from_tl",
                                     target_world="TrapTown",
                                     teleport_point="spawn_trap_from_tl")
                          ],
                          music_name='Prod #1.mp3')

        self.register_map('TrapTown',
                          portals=[
                              Portal(from_world='TrapTown', origin_point="enter_tl_from_trap",
                                     target_world="Third_Level",
                                     teleport_point='spawn_tl_from_trap'),
                          ],
                          music_name='Fores(piri)t.mp3')

        self.register_map('Coast',
                          portals=[
                              Portal(from_world='Coast', origin_point="enter_tl_from_coast", target_world="Third_Level",
                                     teleport_point='spawn_tl_from_coast'),
                              Portal(from_world='Coast', origin_point="enter_foulcity_from_coast",
                                     target_world="Fourth_Level_City",
                                     teleport_point="spawn_foulcity_from_coast"),
                          ],
                          npcs=[
                              DiskGiver('AI', nb_points=1,
                                        dialog=["Tu as réussi à parvenir jusqu'ici,\ntu mérites bien ça"],
                                        reward='cd3')
                          ],
                          music_name='ebala!denrutcon.mp3')

        self.register_map('Fourth_Level_City',
                          portals=[
                              Portal(from_world='Fourth_Level_City', origin_point="enter_coast_from_foulcity",
                                     target_world="Coast",
                                     teleport_point="spawn_coast_from_foulcity"),
                              Portal(from_world='Fourth_Level_City', origin_point="enter_lastlevel",
                                     target_world="Last_Level",
                                     teleport_point="spawn_lastlevel_from_foulcity"),
                              Portal(from_world='Fourth_Level_City', origin_point="enter1_fourth_level",
                                     target_world="Fourth_Level",
                                     teleport_point="spawn_foul_from_foulcity1"),
                              Portal(from_world='Fourth_Level_City', origin_point="enter2_fourth_level",
                                     target_world="Fourth_Level",
                                     teleport_point="spawn_foul_from_foulcity2"),
                          ],
                          music_name='ebala!denrutcon.mp3')

        self.register_map('Fourth_Level',
                          portals=[
                              Portal(from_world='Fourth_Level', origin_point="exit_foul1",
                                     target_world="Fourth_Level_City",
                                     teleport_point="spawn_foulcity_from_foul1"),
                              Portal(from_world='Fourth_Level', origin_point="exit_foul2",
                                     target_world="Fourth_Level_City",
                                     teleport_point="spawn_foulcity_from_foul2")
                          ],
                          npcs=[
                              DiskGiver('AI', nb_points=1,
                                        dialog=["HAHAHAHA, JE VEUX JUSTE SAVOIR COMMENT\nTU VAS TE SENTIR APRÈS ÇA",
                                                "Je sens que ton flair est aiguisé,\npas besoin de parler. Je te le donne.",
                                                "    !",
                                                "QUOI ?!!",
                                                "TU T'ATTENDAIS À UN TEST ENCORE ??", "FILE !"],
                                        reward='cd4')
                          ],
                          music_name='ebala!denrutcon.mp3')

        self.register_map('Last_Level',
                          portals=[
                              Portal(from_world='Last_Level', origin_point="enter_foulcity_from_lastlevel",
                                     target_world="Fourth_Level_City", teleport_point="spawn_foulcity_from_lastlevel"),
                              Portal(from_world='Last_Level', origin_point="enter_lab", target_world="Lab",
                                     teleport_point="spawn_lab")
                          ],npcs=[
                              NPC("AI", nb_points=1, dialog=["J'espère que tu passes un bon moment!\nHésites pas à partager ton expérience",
                                                             "Horus et Hifumi."])
                          ],
                          music_name='ebala!denrutcon.mp3')

        self.register_map('Lab',
                          portals=[
                              Portal(from_world='Lab', origin_point="exit_lab_for_laslvl", target_world="Last_Level",
                                     teleport_point="spawn_laslvl_from_lab"),
                              Portal(from_world='Lab', origin_point="exit_lab_for_spawn", target_world="Spawn",
                                     teleport_point="player")
                          ],
                          npcs=[
                              Boss('AI', nb_points=1)
                          ],
                          music_name='blahtgrf.mp3')

        self.teleport_player("player")
        self.teleport_npcs()

        # if self.register_map(['Spawn', 'Passage_Spawn', 'First_Level_City']):
        # l= ['GUITARE 5 (solo guitarre)', 'dacadac','blahtgrf', 'dimensionard',
        # 'newone - Horus', 'NO TITLE', 'NOTITLEYET', 'Prod #1', 'reve trznsi', 'SUPERMAN',
        # 'Fore(spiri)t', 'how to chill']

        self.music_list = ['dacadac.mp3', 'Prod #1.mp3', 'Fores(piri)t.mp3', 'ebala!denrutcon.mp3', 'blahtgrf.mp3']
        self.music_dict = {}
        for music_name in self.music_list:
            music = pygame.mixer.Sound(f'../audio/music/{music_name}')
            self.music_dict[music_name] = music
        self.music_name = self.maps[self.current_map].music_name
        self.music = self.music_dict[self.music_name]
        self.music.set_volume(0.07)
        self.music.play(loops=-1)

        self.cd_sound = pygame.mixer.Sound('../audio/sfx/BROKENCDSOUND.mp3')

    def reset_game(self):
        self.player.inventory = []
        self.current_map = "Spawn"
        self.music.stop()
        self.endgame_sound.stop()
        self.music_name = self.maps[self.current_map].music_name
        self.music = self.music_dict[self.music_name]
        self.music.set_volume(0.1)
        self.music.play(loops=-1)
        self.teleport_player("player")
        self.player.lights_on = False
        self.endgame = False
        self.endgame_time = 0

    def check_cd(self):
        inventory = self.player.inventory
        if 'cd1' in inventory and 'cd2' in inventory and 'cd3' in inventory and 'cd4' in inventory:
            return True
        else:
            return False

    def read_sign(self):
        self.sign = Sign(text='    ?')
        self.sign_active = True

    def check_npc_collisions(self, dialog_box):
        for sprite in self.get_group().sprites():
            if sprite.feet.colliderect(self.player.rect) and isinstance(sprite, NPC):

                if type(sprite) is NPC:
                    dialog = sprite.get_dialog()

                if type(sprite) is Boss:

                    mission_complete = self.check_cd()
                    dialog = sprite.get_dialog(mission_complete=mission_complete, end_timer=self.end_timer)

                    if mission_complete:
                        # Lorsque le dialogue est terminé, on lance le son et on affiche l'image
                        if dialog_box.text_index == len(dialog_box.texts) - 1 and dialog_box.main_dialog_index == 0:
                            self.music.stop()
                            self.endgame_sound.play()
                            self.endgame_time = pygame.time.get_ticks()
                            self.endgame = True

                        if dialog_box.text_index == 9 and dialog_box.main_dialog_index == 0:
                            self.cd_sound.play()

                elif type(sprite) is LightsGuy:

                    mission_complete = self.player.lights_on
                    dialog = sprite.get_dialog(mission_complete=mission_complete)

                    # Lorsque le dialogue est terminé et si la mission est accompli, on donne un disque au joueur
                    if dialog_box.text_index == len(dialog_box.texts) - 1:
                        if mission_complete:
                            if 'cd1' not in self.player.inventory:
                                self.player.inventory.append('cd1')

                elif type(sprite) is DiskGiver:

                    dialog = sprite.get_dialog()

                    # Lorsque le dialogue est terminé, on donne un disque au joueur
                    if dialog_box.text_index == len(dialog_box.texts) - 1:
                        disk = sprite.reward
                        if disk not in self.player.inventory:
                            self.player.inventory.append(disk)

                dialog_box.execute(dialog)

    def check_interaction_collisions(self):
        interactions = self.get_map().interactions
        for obj in interactions:
            obj_rect = pygame.Rect(obj.x, obj.y, obj.width, obj.height)
            if self.player.rect.colliderect(obj_rect):
                # Level 1 lightswich:
                if obj.name == 'turnlight_on':
                    self.player.lights_on = True
                    self.chimney_sound.play()

                # Panneau:
                if obj.name == 'read_sign':
                    if self.sign_active:
                        self.sign_active = False
                    else:
                        self.read_sign()
    def check_collisions(self):

        # portails
        for portal in self.get_map().portals:
            if portal.from_world == self.current_map:
                point = self.get_object(portal.origin_point)
                rect = pygame.Rect(point.x, point.y, point.width, point.height)

                if self.player.feet.colliderect(rect):
                    self.current_map = portal.target_world
                    if self.maps[self.current_map].music_name != self.music_name:
                        self.music_name = self.maps[self.current_map].music_name
                        self.music.stop()
                        self.music = self.music_dict[self.maps[self.current_map].music_name]
                        self.music.set_volume(0.07)
                        self.music.play(loops=-1)
                    self.teleport_player(portal.teleport_point)

        # collision
        for sprite in self.get_group().sprites():

            if isinstance(sprite, NPC):
                if sprite.feet.colliderect(self.player.rect):
                    sprite.speed = 0

                else:
                    sprite.speed = 0.5

            if sprite.feet.collidelist(self.get_walls()) > -1:
                sprite.move_back()

    def teleport_player(self, name):
        point = self.get_object(name)
        self.player.position[0] = point.x
        self.player.position[1] = point.y
        self.player.save_location()

    def register_map(self, name, music_name, portals=[], npcs=[]):

        # charger la carte tmx
        tmx_data = pytmx.util_pygame.load_pygame(f'../data/tmx/{name}.tmx')
        map_data = pyscroll.data.TiledMapData(tmx_data)
        map_layer = pyscroll.orthographic.BufferedRenderer(map_data, self.screen.get_size())
        map_layer.zoom = 2

        # definir une liste qui stocke les rect de collision

        walls = []
        interactions = []

        for obj in tmx_data.objects:
            if obj.type == "collision":
                walls.append(pygame.Rect(obj.x, obj.y, obj.width, obj.height))
            elif obj.type == "interaction":
                interactions.append(obj)

        # dessiner le groupe de calque
        group = pyscroll.PyscrollGroup(map_layer=map_layer, default_layer=10)
        group.add(self.player)

        # recup les npcs pour les ajouter au groupe

        for npc in npcs:
            group.add(npc)

        # creer la map
        self.maps[name] = Map(name, walls, group, tmx_data, portals, npcs, interactions, music_name)

    def get_map(self):
        return self.maps[self.current_map]

    def get_group(self):
        return self.get_map().group

    def get_walls(self):
        return self.get_map().walls

    def get_object(self, name):
        return self.get_map().tmx_data.get_object_by_name(name)

    def teleport_npcs(self):
        for map in self.maps:
            map_data = self.maps[map]
            npcs = map_data.npcs

            for npc in npcs:
                npc.load_points(map_data.tmx_data)
                npc.teleport_spawn()

    def blinking_lights(self):

        now = pygame.time.get_ticks()
        if self.lights_on:
            if now - self.lightswitch_time > 1000:
                self.lightswitch_time = now
                self.lights_on = False
                self.lightswitch_sound.play()
        else:
            self.screen.fill((0, 0, 0))
            if now - self.lightswitch_time > 2000:
                self.lightswitch_time = now
                self.lights_on = True
                self.lightswitch_sound.play()

    def display_cd(self, screen):
        inv = self.player.inventory

        if 'cd1' in inv:
            screen.blit(self.cd_parts[0], self.cd1pos)
        if 'cd2' in inv:
            screen.blit(self.cd_parts[1], self.cd2pos)
        if 'cd3' in inv:
            screen.blit(self.cd_parts[2], self.cd3pos)
        if 'cd4' in inv:
            screen.blit(self.cd_parts[3], self.cd4pos)

    def draw(self):
        self.get_group().draw(self.screen)
        self.get_group().center(self.player.rect.center)

        if self.get_map().name == 'First_Level':
            if not self.player.lights_on:
                self.blinking_lights()

        self.display_cd(self.screen)

        if self.sign_active:
            self.sign.draw(self.screen)

        if self.endgame:
            self.screen.blit(self.endgame_image, (0, 0))


    def update(self):
        self.get_group().update()
        self.check_collisions()

        for npc in self.get_map().npcs:
            npc.move()

        if self.endgame:
            now = pygame.time.get_ticks()
            time_since_endgame = now - self.endgame_time
            if time_since_endgame > 27000:
                self.reset_game()

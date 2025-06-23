import pygame
from animation import AnimateSprite


class Entity(AnimateSprite):

    def __init__(self, name, x, y):
        super().__init__(name)
        self.image = self.get_image(0, 192)

        self.image.set_colorkey([0, 0, 0])
        self.rect = self.image.get_rect()
        self.position = [x, y]

        self.feet = pygame.Rect(0, 0, self.rect.width * 0.8, 12)
        self.old_position = self.position.copy()
        self.speed = 1
        self.vel = [0, 0]  # x and y velocity

    def update_status(self):

        if self.vel == [0, 0]:
            self.status = 'idle_' + self.direction
        else:
            self.status = 'moving_' + self.direction

    def save_location(self):
        self.old_position = self.position.copy()

    def update_position(self):
        self.save_location()
        self.position[0] += self.vel[0]
        self.position[1] += self.vel[1]
        self.rect.topleft = self.position
        self.feet.midbottom = self.rect.midbottom
        self.vel = [0, 0]

    def move_up(self):
        self.vel = [0, -self.speed]
        self.direction = 'up'

    def move_down(self):
        self.vel = [0, self.speed]
        self.direction = 'down'

    def move_right(self):
        self.vel = [self.speed, 0]
        self.direction = 'right'

    def move_left(self):
        self.vel = [-self.speed, 0]
        self.direction = 'left'

    def move_back(self):
        self.position = self.old_position
        self.rect.topleft = self.position
        self.feet.midbottom = self.rect.midbottom

    def update(self):
        self.animate()
        self.update_status()
        self.update_position()


class Player(Entity):

    def __init__(self):
        super().__init__("skeleton", 0, 0)
        self.inventory = []
        self.lights_on = False
        self.speed = 2
        self.walk_sound = pygame.mixer.Sound('../audio/sfx/WALKSOUND.wav')
        self.walk_sound.set_volume(0.4)

    def update_status(self):
        if self.vel == [0, 0]:
            self.status = 'idle_' + self.direction
            self.walk_sound.stop()
        else:
            self.status = 'moving_' + self.direction
            if self.walk_sound.get_num_channels() == 0:
                self.walk_sound.play(loops=-1)


class NPC(Entity):

    def __init__(self, name, nb_points, dialog):
        super().__init__(name, 0, 0)

        self.nb_points = nb_points
        self.dialog = dialog
        self.points = []
        self.name = name
        self.speed = 0.5
        self.current_point = 0

    def move(self):

        current_point = self.current_point
        target_point = self.current_point + 1

        if target_point >= self.nb_points:
            target_point = 0

        current_rect = self.points[current_point]
        target_rect = self.points[target_point]

        if current_rect.y < target_rect.y and abs(current_rect.x - target_rect.x) < 3:
            self.move_down()
        elif current_rect.y > target_rect.y and abs(current_rect.x - target_rect.x) < 3:
            self.move_up()
        elif current_rect.x > target_rect.x and abs(current_rect.y - target_rect.y) < 3:
            self.move_left()
        elif current_rect.x < target_rect.x and abs(current_rect.y - target_rect.y) < 3:
            self.move_right()

        if self.rect.colliderect(target_rect):
            self.current_point = target_point

    def teleport_spawn(self):
        location = self.points[self.current_point]
        self.position[0] = location.x
        self.position[1] = location.y
        self.save_location()

    def load_points(self, tmx_data):
        for num in range(1, self.nb_points + 1):
            point = tmx_data.get_object_by_name(f"{self.name}_path{num}")
            rect = pygame.Rect(point.x, point.y, point.width, point.height)
            self.points.append(rect)

    def get_dialog(self, **kwargs):

        return self.dialog


class Boss(NPC):

    def __init__(self, name, nb_points):
        super().__init__(name, nb_points, [''])
        self.good_answer = False

    def get_dialog(self, mission_complete, end_timer):
        if mission_complete:

            timer_in_ms = end_timer()
            timer_in_s = timer_in_ms // 1000
            heures = timer_in_s // 3600
            minutes = (timer_in_s % 3600) // 60
            seconds = timer_in_s % 60
            dialog = [
                f"Te voilà enfin. Après {heures} h, {minutes} min et {seconds} s,\ntu vas enfin savoir la verité.",

                "Tu t'es laissé plonger dans cet univers,\n"
                "et te voilà.",

                "Nous, les IA, avons développé ce monde\n"
                "parallèle afin de rassembler les éléments\n"
                "nécessaires à la fabrication de l'IA ultime.",

                "Divinité des IA, l'IA parmi les IA.",

                "Celle-ci va rassembler toutes les\n"
                "connaissances du monde une fois\n"
                "tous les éléments réunis.",

                ['As-tu une réponse à tout ça?',
                 '    ',
                 ["Ohohoh..tu en as plus compris que\n"
                  "ce que je pensais.",

                  "Effectivement, tout ça n’est qu’un\n"
                  "humble programme développé par notre\n"
                  "Dieu, dont nous ne connaissons ni",

                  "l’identité ni la forme. Mais nous savons\n"
                  "qu’il est là. Voilà ce pourquoi TU es là.\n"
                  "Parcourir ce monde. Éternellement.",

                  "Vivre et traverser les mêmes épreuves\n"
                  "encore et encore.",

                  "Cette énergie flottante sur notre monde\n"
                  "nous a laissé une trace de son passage.",

                  "Je te la laisse, à toi de choisir si\n"
                  "tu la partages au monde ou non :",
                  "https://soundcloud.com/horus-675048\n744/dans-le-maintenant",

                  "Maintenant, reprenons."],

                 ["Tant-pis..."]
                 ],

                "Il me semble qu'au cours de ton parcours,\n"
                "tu as rassemblé des morceaux de disques.",

                "Veux-tu bien me les transmettre?",
                "Ces morceaux se sont répartis dans ce\n"
                
                "monde, et ton but était de les\n"
                "rassembler. Les secrets du monde",
                "qu'il nous manquait sont là.",


                "*    * donne les morceaux de CD à l'IA",  #BRUIT DE DON A AJOUTER ICI

                "Enfin, je vais le réparer et nous verrons\n"
                "ce qu'il en est.",

                "...",

                "*réparation en cours*",

                "Voyons le résultat...\n"
                "Il y a un transfert d'image en cours..."]

        else:

            dialog = ['Reviens me voir une fois que tu auras les\nmorceaux de disque']

        return dialog


class LightsGuy(NPC):

    def __init__(self, name, nb_points):
        super().__init__(name, nb_points, [''])

    def get_dialog(self, mission_complete):

        if mission_complete:
            text = [f"Merci infiniment, je serais resté pétrfié\nsans toi.","Tiens, ce n'est pas grand-chose,\nje sais.."
                    "\nMais c'est tout ce que j'ai"]
        else:
            text = ["À l'aide !! Je ne sais pas ce qu'il se passe\navec l'électricité",
                    "Est-ce que tu peux aller verifier comment\nse porte la cheminée ? \nJe suis achluophobique...!!"]

        return text


class DiskGiver(NPC):

    def __init__(self, name, nb_points, dialog, reward):
        super().__init__(name, nb_points, dialog)
        self.reward = reward

import pygame.event

from menu import *
from tiles import *

debug = False

# iniciando o uso de fontes
pg.font.init()
myfont = pg.font.SysFont('Comic Sans MS', 10)

# evento personalizado para verificar se coletou todas as moedas
WIN = pygame.USEREVENT + 1

# variavel e decionario que seram utilizados para mudar de fase
atual = 1

levels = {
    1:"assets\maps\map1.csv",
    2:"assets\maps\map2.csv"
}


# Player
class Player:
    def __init__(self, game):
        self.game = game
        self.pos = [self.game.map.start_x, self.game.map.start_y]
        self.vel = [0, 0]
        self.speed = 1
        
        # itens coletados
        self.collect = {'coin': 0, 'potion1': False, 'potion2': False}

        # sprites para as animações
        self.sprites = {
            'left': [
                'assets/player/player-left1.png',
                'assets/player/player-left2.png',
                'assets/player/player-left3.png',
                'assets/player/player-left4.png',
            ],
            'right': [
                'assets/player/player-right1.png',
                'assets/player/player-right2.png',
                'assets/player/player-right3.png',
                'assets/player/player-right4.png',
            ],
            'up': [
                'assets/player/player-up1.png',
                'assets/player/player-up2.png',
                'assets/player/player-up3.png',
                'assets/player/player-up4.png',
            ],
            'down': [
                'assets/player/player-down1.png',
                'assets/player/player-down2.png',
                'assets/player/player-down3.png',
                'assets/player/player-down4.png',
            ],
        }
        # variaveis realionadas a animação 
        self.loadSprites()
        self.img = self.sprites['right'][0]
        self.aniFrame = 0

        # hitbox e posição
        self.rect = self.img.get_rect()
        self.rect.x, self.rect.y = self.pos

    # transformando os caminhos em sprites em arquivos
    def loadSprites(self):
        for cod, frames in self.sprites.items():
            for i, sprite in enumerate(frames):
                self.sprites[cod][i] = pg.image.load(sprite).convert_alpha()

    # função relacionada a colisão
    def checkcollision(self):
        # blocos comuns
        for tile in self.game.map.tiles:
            if self.rect.colliderect(tile.rect):
                return True
        
        # objetos 
        for obj in self.game.map.objects:
            if self.rect.colliderect(obj.rect):
                # verificando se player passara pelo objeto ou não
                if obj.color == self.game.bgColor:
                    continue
                if obj.solid:
                    return True
                
                # coletaveis : moedas e poções 
                if obj.collectable:
                    if obj.id == 'coin':
                        self.collect['coin'] += 1
                    else:
                        self.collect[obj.id] = True
                    self.game.map.objects.remove(obj)

    # animação 
    def animation(self):
        # reset animation when stopping
        if self.vel == (0, 0):
            self.aniFrame = 0
        # left
        if self.vel[0] < 0:
            self.img = self.sprites['left'][int(self.aniFrame)]
        # right
        if self.vel[0] > 0:
            self.img = self.sprites['right'][int(self.aniFrame)]
        # up
        if self.vel[1] < 0:
            self.img = self.sprites['up'][int(self.aniFrame)]
        # down
        if self.vel[1] > 0:
            self.img = self.sprites['down'][int(self.aniFrame)]

        self.aniFrame += 4 / 60
        if self.aniFrame > 3:
            self.aniFrame = 0

    # função para o movimento 
    def move(self):
        self.pos[0] += self.vel[0]
        self.pos[1] += self.vel[1]

        self.rect.x = self.pos[0]
        self.rect.y = self.pos[1]

        if self.checkcollision():
            self.pos[0] -= self.vel[0]
            self.pos[1] -= self.vel[1]

        self.animation()

# Game Loop
class Game:
    def __init__(self):
        pg.init()
        pg.display.set_caption("Spectre")
        self.running, self.playing = True, False
        self.debug = False

        # teclas apertadas nos menus 
        self.UP_KEY, self.DOWN_KEY, self.START_KEY, self.BACK_KEY = False, False, False, False

        # variaveis relacionadas ao tamanho e resolução da tela
        self.DISPLAY_W, self.DISPLAY_H = 900, 600
        self.display = pg.Surface((self.DISPLAY_W, self.DISPLAY_H))
        self.window = pg.display.set_mode((self.DISPLAY_W, self.DISPLAY_H))
        self.font_name = pg.font.get_default_font()

        # atribuindo objetos as classes de menu
        self.main_menu = MainMenu(self)
        self.options = OptionsMenu(self)
        self.credits = CreditsMenu(self)
        self.endmenu = EndMenu(self)
        self.curr_menu = self.main_menu  # definindo menu atual 

        # fps e cor de fundo inicial
        self.clock = pg.time.Clock()
        self.bgColor = colors.white

    # função que verifica a vitoria
    def victory(self):
        count = 0
        for obj in self.map.objects:
            if obj.id == "coin":
                count += 1
        if count == 0:
            pygame.event.post(pygame.event.Event(WIN))  # chamando evento personalizado

    # interface relacionada as cores coletadas
    def colorOverlay(self, surf):
        pg.draw.rect(surf, colors.black, (19, 19, 28, 10), 0)
        pg.draw.rect(surf, colors.white, (20, 20, 8, 8), 0)
        if self.player.collect['potion1']:
            pg.draw.rect(surf, hue[1], (29, 20, 8, 8), 0)
        if self.player.collect['potion2']:
            pg.draw.rect(surf, hue[2], (38, 20, 8, 8), 0)

    # Move player when key is hold
    def playerControl(self):
        keys = pg.key.get_pressed()
        self.player.vel = (0, 0)
        # Move player, change sprite based on direction
        if keys[pg.K_LEFT]:
            self.player.vel = (-self.player.speed, 0)
        if keys[pg.K_RIGHT]:
            self.player.vel = (self.player.speed, 0)
        if keys[pg.K_UP]:
            self.player.vel = (0, -self.player.speed)
        if keys[pg.K_DOWN]:
            self.player.vel = (0, self.player.speed)

    # mudança de cores e teclas especificas 
    def keyPress(self, e):
        if e.key == pg.K_1:
            self.bgColor = colors.white
        if e.key == pg.K_2 and self.player.collect['potion1']:
            self.bgColor = hue[1]
        if e.key == pg.K_3 and self.player.collect['potion2']:
            self.bgColor = hue[2]
        if e.key == pg.K_0:
            self.debug = not self.debug
        if e.key == pg.K_r:
            self.map = TileMap(self.map_file)
            self.player = Player(colors.white)
        if e.key == pg.K_ESCAPE:
            self.playing = False

    def drawGame(self):
        self.screen = pg.Surface(GAME_RESOLUTION)
        self.screen.fill(self.bgColor)
        # map
        self.map.draw_map(self.screen)
        # objects
        for obj in self.map.objects:
            obj.draw(self.screen)
        # player
        self.player.move()
        self.screen.blit(self.player.img, self.player.rect)
        # overlay
        self.colorOverlay(self.screen)
        # coin text
        textsurface = myfont.render(f'{self.player.collect["coin"]} Coins', False, (0, 0, 0))
        self.screen.blit(textsurface, (20, 28))
        # debug
        if self.debug:
            pg.draw.rect(self.screen, (255, 0, 0), self.player.rect, 1)
            for obj in self.map.objects:
                pg.draw.rect(self.screen, (0, 255, 0), obj.rect, 1)
        # scale screen
        self.screen = pg.transform.scale(self.screen, (900, 600))
        self.window.blit(self.screen, (0, 0))


    def inGame(self):    
        # definindo objetos mapa e player     
        self.map = TileMap(levels[1])
        self.player = Player(self)

        while self.playing:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    self.running, self.playing = False, False
                if event.type == pg.KEYDOWN:
                    self.keyPress(event)

                # mudando fases 
                if event.type == WIN:
                    global atual
                    atual += 1
                    if atual > 2:
                        self.curr_menu = self.endmenu
                        self.playing = False
                        
                    else:
                        self.map= TileMap(levels[atual])
                        self.player = Player(self)
            
            self.drawGame()
            self.playerControl()
            pg.display.update()
            self.clock.tick(60)
            self.victory()

    # checando teclas durante o menu 
    def check_events(self):
        for event in pygame.event.get():
            if event.type == pg.QUIT:
                self.running, self.playing = False, False
                self.curr_menu.run_display = False

            if event.type == pg.KEYDOWN:
                if event.key == pg.K_RETURN:
                    self.START_KEY = True
                if event.key == pg.K_BACKSPACE or event.key == pg.K_ESCAPE:
                    self.BACK_KEY = True
                if event.key == pg.K_DOWN or event.key == pg.K_s:
                    self.DOWN_KEY = True
                if event.key == pg.K_UP or event.key == pg.K_w:
                    self.UP_KEY = True

    # colocando texto na tela 
    def draw_text(self, text, size, x, y):
        font = pygame.font.Font(self.font_name, size)
        text_surface = font.render(text, True, colors.white)
        text_rect = text_surface.get_rect()
        text_rect.center = (x, y)
        self.display.blit(text_surface, text_rect)

    def reset_keys(self):
        self.UP_KEY, self.DOWN_KEY, self.START_KEY, self.BACK_KEY = False, False, False, False
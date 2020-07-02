import time, random
import pygame
pygame.init()


WIDTH, HEIGHT = 450, 500
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock  = pygame.time.Clock()
FPS    = 60


# Colours
BLACK = (0,     0,   0)
RED   = (255, 120,   0)
GREEN = (40,  220, 130)
BLUE  = (180, 100, 225)
WHITE = (255, 255, 255)
# ALLCOLOURS = [BLACK, GREEN, BLUE, WHITE]


# checks whether the movement by entity is within the screen or not
# entity can be a class Player object or class Brick/Enemy Object
def ValidPlayerMovement(entity, x: int, y: int) -> list:
    result = [True, True]
    if x < 0 or x + entity.width > WIDTH:
        result[0] = False
    if y < 0 or y + entity.height > HEIGHT:
        result[1] = False

    return result


class Laser:
    width = 5
    height = 10

    def __init__(self, x: int, y: int, shooter = None, colour: tuple = WHITE):
        self.x = x
        self.y = y
        self.shooter = shooter
        self.colour = colour
        self.vy = -5

    def draw(self):
        pygame.draw.aaline(screen, self.colour, (self.x + self.shooter.width // 2, self.y),
                           (self.x + self.shooter.width // 2, self.y + Laser.height))
        self.y += self.vy

class Player:
    width = 10
    height = 10
    velocity = 2

    def __init__(self, x: int, y: int, color: tuple = BLUE):
        self.x = x
        self.y = y
        self.colour = color
        self.lasers = []
        self.cooldown = 0.2  # Time interval between two lasers (seconds)
        self._property = pygame.Rect(
            self.x, self.y, Player.width, Player.height)

    def draw(self):
        pygame.draw.rect(screen, self.colour, self._property)
        self._property.x = self.x
        self._property.y = self.y

    def shoot(self):    
        player.lasers.append(Laser(player.x, player.y - Laser.height, self))
            

class Brick:
    width = 10
    height = 5
    spacing = 10

    def __init__(self, x: int, y: int, colour: tuple = GREEN):
        self.x = x
        self.y = y
        self.colour = colour
        self._property = pygame.Rect(self.x, self.y, Brick.width, Brick.height)

    def draw(self):
        pygame.draw.rect(screen, self.colour, self._property)


class Enemy(Brick):
    shooting_probability = 1e-4

    def __init__(self, x: int, y: int, colour: tuple = GREEN, vx=0, vy=0):
        super().__init__(x, y, colour=colour)
        self.vx = vx
        self.vy = vy
        self.lasers = []

    def move(self):
        x, y = self.x, self.y
        x += self.vx
        y += self.vy

        validity = ValidPlayerMovement(self, x, y)
        if validity[0]:
            self.x = x
            self._property.x = self.x
        if validity[1]:
            self.y = y
            self._property.y = self.y

    def draw(self):
        pygame.draw.rect(screen, self.colour, self._property)
        for laser in self.lasers:
            laser.draw()
        self.move()

    def shoot(self):
        laser = Laser(self.x, self.y, self, RED)
        laser.vy *= -1
        self.lasers.append(laser)
        return laser

    def unsure_shoot(self):
        if random.random() <= Enemy.shooting_probability:
            return self.shoot()


class EnemyGenerator:

    @staticmethod
    def rectangle(
            x:         int,
            y:         int,
            rows:      int,
            cols:      int,
            vx:        int = 0,
            vy:        int = 0,
            vspacing:  int = 10,
            hspacing:  int = 15):

        enemies = []
        for i in range(rows):
            for j in range(cols):
                enemies.append(Enemy((i + 1) * (x + hspacing),
                                     (j + 1) * (y + vspacing), vx=vx, vy=vy))

        return enemies


class ShieldGenerator:

    @staticmethod
    def basic(
        x:    int,
        y:    int,
        rows: int,
        cols: int,
        packs=1,  # number of shield "packages" to draw
        vspacing=0,
        hspacing=50,
    ) -> list:
        # EnemyGenerator.rectangle(x,y,rows,cols,vspacing=0, hspacing=50)
        shields = []
        for i in range(rows):
            for j in range(cols):
                shields.append(Brick((i + 1) * (rows + hspacing),
                                     (j + 1) * (cols + vspacing)))
        return shields


player = Player(WIDTH // 2, HEIGHT - Player.height)
enemies = EnemyGenerator.rectangle(0, 0, 20, 5, vx=0, vy=0)
last_laser_time = time.time()
shields = ShieldGenerator.basic(WIDTH // 2, HEIGHT // 2, 10, 10)
last_laser_time = time.time()


def main():
    global last_laser_time
    screen.fill(BLACK)

    if pygame.event.poll().type == pygame.QUIT:
        pygame.quit()
        exit(0)
    
    # check whether lasers are within the screen
    for laser in player.lasers: 
        if laser.x < 0 or laser.y < 0 or laser.x > WIDTH or laser.y > HEIGHT:
            player.lasers.remove(laser)

    # if player presses mouse button M1
    if pygame.mouse.get_pressed()[0]:
        current_time = time.time()
        if current_time - last_laser_time > player.cooldown:
            player.shoot()
            last_laser_time = current_time

    # collision detection for lasers and enemies
    for enemy in enemies:
        for laser in player.lasers:
            if (enemy.x <= laser.x <= enemy.x + Brick.width or  \
               laser.x <= enemy.x <= laser.x + Laser.width) and \
               (enemy.y <= laser.y <= enemy.y + Brick.height or \
                laser.y <= enemy.y <= laser.y + Laser.width):
                try:
                    enemies.remove(enemy)
                    player.lasers.remove(laser)
                except: pass

    for enemy in enemies:
        enemy.move() 

    if len(enemies) == 0:
        print("Congradulations you won!")
        pygame.quit()
        exit(0)
    
    keys = pygame.key.get_pressed()
    x, y = player.x, player.y

    if keys[pygame.K_a]:
        x -= Player.velocity
    if keys[pygame.K_d]:
        x += Player.velocity
    if keys[pygame.K_w]:
        y -= Player.velocity
    if keys[pygame.K_s]:
        y += Player.velocity

    validity = ValidPlayerMovement(player, x, y)
    if validity[0]:
        player.x = x
    if validity[1]:
        player.y = y

    player.draw()
    for enemy in enemies:
        # for upfront_enemies in enemies[-1]:
        enemies.unsure_shoot()
        enemy.draw()
    for laser in player.lasers:
        laser.draw()
    for shield in shields:
        pass

    clock.tick(FPS)
    pygame.display.flip()


if __name__ == "__main__":
    while True:
        main()

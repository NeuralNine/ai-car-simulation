# Car Racing AI

import math
import sys

import neat
import pickle
import pygame

pygame.init()

# Constants
# WIDTH = 1600
# HEIGHT = 880

WIDTH = 1920
HEIGHT = 1080

CAR_SIZE_X = 60
CAR_SIZE_Y = 60

MAP = "map3"
SAVE = "from_map3"

BORDER_COLOR = (255, 255, 255, 255)  # Color To Crash on Hit

current_generation = 0  # Generation counter


class Car:

    def __init__(self, name=""):
        # Load Car Sprite and Rotate
        self.sprite = pygame.image.load('car.png').convert()  # Convert Speeds Up A Lot
        self.sprite = pygame.transform.scale(self.sprite, (CAR_SIZE_X, CAR_SIZE_Y))
        self.rotated_sprite = self.sprite

        # self.position = [690, 740] # Starting Position
        self.position = [830, 920]  # Starting Position
        self.angle = 0
        self.speed = 0

        self.speed_set = False  # Flag For Default Speed Later on

        self.center = [self.position[0] + CAR_SIZE_X / 2, self.position[1] + CAR_SIZE_Y / 2]  # Calculate Center

        self.radars = []  # List For Sensors / Radars
        self.drawing_radars = []  # Radars To Be Drawn

        self.alive = True  # Boolean To Check If Car is Crashed

        self.distance = 0  # Distance Driven
        self.time = 0  # Time Passed
        self.name = name

    def __str__(self):
        if self.name != "":
            return self.name
        else:
            return "No name given"

    def draw(self, screen, sensor = False):
        screen.blit(self.rotated_sprite, self.position)  # Draw Sprite
        if sensor:
            self.draw_radar(screen)  # OPTIONAL FOR SENSORS

    def draw_radar(self, screen):
        # Optionally Draw All Sensors / Radars
        for radar in self.radars:
            position = radar[0]
            pygame.draw.line(screen, (0, 255, 0), self.center, position, 1)
            pygame.draw.circle(screen, (0, 255, 0), position, 5)

    def check_collision(self, game_map):
        self.alive = True
        for point in self.corners:
            # If Any Corner Touches Border Color -> Crash
            # Assumes Rectangle
            if game_map.get_at((int(point[0]), int(point[1]))) == BORDER_COLOR:
                self.alive = False
                break

    def check_radar(self, degree, game_map):
        length = 0
        x = int(self.center[0] + math.cos(math.radians(360 - (self.angle + degree))) * length)
        y = int(self.center[1] + math.sin(math.radians(360 - (self.angle + degree))) * length)

        # While We Don't Hit BORDER_COLOR AND length < 300 (just a max) -> go further and further
        while not game_map.get_at((x, y)) == BORDER_COLOR and length < 300:
            length = length + 1
            x = int(self.center[0] + math.cos(math.radians(360 - (self.angle + degree))) * length)
            y = int(self.center[1] + math.sin(math.radians(360 - (self.angle + degree))) * length)

        # Calculate Distance To Border And Append To Radars List
        dist = int(math.sqrt(math.pow(x - self.center[0], 2) + math.pow(y - self.center[1], 2)))
        self.radars.append([(x, y), dist])

    def update(self, game_map):
        # Set The Speed To 20 For The First Time
        # Only When Having 4 Output Nodes With Speed Up and Down
        if not self.speed_set:
            self.speed = 5
            self.speed_set = True

        # Get Rotated Sprite And Move Into The Right X-Direction
        # Don't Let The Car Go Closer Than 20px To The Edge
        self.rotated_sprite = self.rotate_center(self.sprite, self.angle)
        self.position[0] += math.cos(math.radians(360 - self.angle)) * self.speed
        self.position[0] = max(self.position[0], 20)
        self.position[0] = min(self.position[0], WIDTH - 120)

        # Increase Distance and Time
        self.distance += self.speed
        self.time += 1

        # Same For Y-Position
        self.position[1] += math.sin(math.radians(360 - self.angle)) * self.speed
        self.position[1] = max(self.position[1], 20)
        self.position[1] = min(self.position[1], WIDTH - 120)

        # Calculate New Center
        self.center = [int(self.position[0]) + CAR_SIZE_X / 2, int(self.position[1]) + CAR_SIZE_Y / 2]

        # Calculate Four Corners
        # Length Is Half The Side
        length = 0.5 * CAR_SIZE_X
        left_top = [self.center[0] + math.cos(math.radians(360 - (self.angle + 30))) * length,
                    self.center[1] + math.sin(math.radians(360 - (self.angle + 30))) * length]
        right_top = [self.center[0] + math.cos(math.radians(360 - (self.angle + 150))) * length,
                     self.center[1] + math.sin(math.radians(360 - (self.angle + 150))) * length]
        left_bottom = [self.center[0] + math.cos(math.radians(360 - (self.angle + 210))) * length,
                       self.center[1] + math.sin(math.radians(360 - (self.angle + 210))) * length]
        right_bottom = [self.center[0] + math.cos(math.radians(360 - (self.angle + 330))) * length,
                        self.center[1] + math.sin(math.radians(360 - (self.angle + 330))) * length]
        self.corners = [left_top, right_top, left_bottom, right_bottom]

        # Check Collisions And Clear Radars
        self.check_collision(game_map)
        self.radars.clear()

        # From -90 To 120 With Step-Size 45 Check Radar
        for d in range(-90, 120, 45):
            self.check_radar(d, game_map)

    def get_data(self):
        pass

    def is_alive(self):
        pass

    def get_reward(self):
        pass

    def rotate_center(self, image, angle):
        # Rotate The Rectangle
        rectangle = image.get_rect()
        rotated_image = pygame.transform.rotate(image, angle)
        rotated_rectangle = rectangle.copy()
        rotated_rectangle.center = rotated_image.get_rect().center
        rotated_image = rotated_image.subsurface(rotated_rectangle).copy()
        return rotated_image


# human player
def play():
    # Human player

    # Initialize The Display
    screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)
    fps = 60

    # Clock Settings
    # Font Settings & Loading Map
    clock = pygame.time.Clock()
    game_map = pygame.image.load(f'./maps/{MAP}.png').convert()  # Convert Speeds Up A Lot

    car = Car()

    run = True
    while run:
        # Exit On Quit Event
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                break

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    car.angle += 10  # Left
                elif event.key == pygame.K_RIGHT:
                    car.angle -= 10  # Right
                elif event.key == pygame.K_UP:
                    car.speed += 2  # Speed Up
                elif event.key == pygame.K_DOWN:
                    if car.speed - 2 >= 12:
                        car.speed -= 2  # Slow Down

        screen.blit(game_map, (0, 0))

        if car.is_alive():
            car.update(game_map)
            car.draw(screen)
        else:
            car = Car()

        pygame.display.flip()
        clock.tick(fps)  # 60 FPS

    pygame.quit()
    sys.exit()


def run_simulation(genomes, config):
    pass


if __name__ == "__main__":
    pass

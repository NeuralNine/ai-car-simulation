# This Code is Heavily Inspired By The YouTuber: Cheesy AI
# Code Changed, Optimized And Commented By: NeuralNine (Florian Dedov)
import time
import math
import random
import sys
import os
import time
import neat
import pygame
import pickle
# Constants
# WIDTH = 3243
# HEIGHT = 1824

WIDTH = 3243
HEIGHT = 1824

CAR_SIZE_X = 60
CAR_SIZE_Y = 60

maxspeedp = 120

BORDER_COLOR = (255, 255, 255, 255) # Color To Crash on Hit

current_generation = 0 # Generation counter
def time_convert(sec):
  mins = sec // 60
  sec = sec % 60
  hours = mins // 60
  mins = mins % 60
  print("Time Lapsed = {0}:{1}:{2}".format(int(hours),int(mins),sec))
hat = 900
class Car:

    def __init__(self):
        # Load Car Sprite and Rotate
        self.sprite = pygame.image.load('car.png').convert() # Convert Speeds Up A Lot
        self.sprite = pygame.transform.scale(self.sprite, (CAR_SIZE_X, CAR_SIZE_Y))
        self.rotated_sprite = self.sprite

        # self.position = [690, 740] # Starting Position
        self.position = [830, 920] # Starting Position
        self.angle = 0
        self.speed = 0

        self.speed_set = False # Flag For Default Speed Later on

        self.center = [self.position[0] + CAR_SIZE_X / 2, self.position[1] + CAR_SIZE_Y / 2] # Calculate Center

        self.radars = [] # List For Sensors / Radars
        self.drawing_radars = [] # Radars To Be Drawn

        self.alive = True # Boolean To Check If Car is Crashed

        self.distance = 0 # Distance Driven
        self.time = 0 # Time Passed

    def draw(self, screen):
        screen.blit(self.rotated_sprite, self.position) # Draw Sprite
        self.draw_radar(screen) #OPTIONAL FOR SENSORS

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

                for i, car in enumerate(cars):
                    output = nets[i].activate(car.get_data())
                    choice = output.index(max(output))
                    hat = choice

    def check_radar(self, degree, game_map):
        length = 0
        x = int(self.center[0] + math.cos(math.radians(360 - (self.angle + degree))) * length)
        y = int(self.center[1] + math.sin(math.radians(360 - (self.angle + degree))) * length)

        # While We Don't Hit BORDER_COLOR AND length < 300 (just a max) -> go further and further
        while not game_map.get_at((x, y)) == BORDER_COLOR and length < hat:
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
            self.speed = 20
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
        left_top = [self.center[0] + math.cos(math.radians(360 - (self.angle + 30))) * length, self.center[1] + math.sin(math.radians(360 - (self.angle + 30))) * length]
        right_top = [self.center[0] + math.cos(math.radians(360 - (self.angle + 150))) * length, self.center[1] + math.sin(math.radians(360 - (self.angle + 150))) * length]
        left_bottom = [self.center[0] + math.cos(math.radians(360 - (self.angle + 210))) * length, self.center[1] + math.sin(math.radians(360 - (self.angle + 210))) * length]
        right_bottom = [self.center[0] + math.cos(math.radians(360 - (self.angle + 330))) * length, self.center[1] + math.sin(math.radians(360 - (self.angle + 330))) * length]
        self.corners = [left_top, right_top, left_bottom, right_bottom]

        # Check Collisions And Clear Radars
        self.check_collision(game_map)
        self.radars.clear()

        # From -90 To 120 With Step-Size 45 Check Radar
        for d in range(-90, 120, 45):
            self.check_radar(d, game_map)

    def get_data(self):
        # Get Distances To Border
        radars = self.radars
        return_values = [0, 0, 0, 0, 0]
        for i, radar in enumerate(radars):
            return_values[i] = int(radar[1] / 30)

        return return_values

    def is_alive(self):
        # Basic Alive Function
        return self.alive

    def get_reward(self):
        # Calculate Reward (Maybe Change?)
        # return self.distance / 50.0
        return self.distance / (CAR_SIZE_X / 2)

    def rotate_center(self, image, angle):
        # Rotate The Rectangle
        rectangle = image.get_rect()
        rotated_image = pygame.transform.rotate(image, angle)
        rotated_rectangle = rectangle.copy()
        rotated_rectangle.center = rotated_image.get_rect().center
        rotated_image = rotated_image.subsurface(rotated_rectangle).copy()
        return rotated_image


def run_simulation(genomes, config):

    # Empty Collections For Nets and Cars
    nets = []
    cars = []

    # Initialize PyGame And The Display
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)

    # For All Genomes Passed Create A New Neural Network
    for i, g in genomes:
        net = neat.nn.FeedForwardNetwork.create(g, config)
        nets.append(net)
        g.fitness = 0

        cars.append(Car())

    # Clock Settings
    # Font Settings & Loading Map
    clock = pygame.time.Clock()
    generation_font = pygame.font.SysFont("Arial", 30)
    alive_font = pygame.font.SysFont("Arial", 20)
    game_map = pygame.image.load('map2.png').convert() # Convert Speeds Up A Lot

    global current_generation
    current_generation += 1

    # Simple Counter To Roughly Limit Time (Not Good Practice)
    counter = 0

    while True:
        # Exit On Quit Event
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit(0)

        # For Each Car Get The Acton It Takes
        for i, car in enumerate(cars):
          output = nets[i].activate(car.get_data())
          choice = output.index(max(output))
          if choice == 0:
              car.angle += 10
          if choice == 1:
              car.angle -= 0 # Left
          if choice == 2:
                 car.angle -= 10 # Left
          if choice == 3:
              if car.speed >= 1:
                  car.speed += 1
              else:
                  car.speed -= 1# Slow Down
          if choice == 4:
                  car.speed += 1 # Speed Up
          if choice == 5:
                  list4 = [5,5]
                  car.angle -= random.choice(list4) # Left
          if choice == 6:
                  car.angle += 0 # Left
          if choice == 7:
                  car.angle -= 0
          if choice == 8:
                  car.angle -= 1
          if choice == 9:
                  car.angle -= 2
          if choice == 10:
                  car.angle -= 3
          if choice == 11:
                  car.angle -= 4
          if choice == 12:
                  car.angle -= 5
          if choice == 13:
                  car.angle -= 6
          if choice == 14:
                  car.angle -= 7
          if choice == 15:
                  car.angle -= 8
          if choice == 16:
                  car.angle -= 9
          if choice == 17:
                  car.angle -= 10
          if choice == 18:
                  car.angle -= 11
          if choice == 19:
                  car.angle -= 12
          if choice == 20:
                  car.angle -= 13
          if choice == 21:
                  car.angle -= 14
          if choice == 22:
                  car.angle -= 15
          if choice == 23:
                  car.angle -= 16
          if choice == 24:
                  car.angle -= 17
          if choice == 25:
                  car.angle -= 18
          if choice == 26:
                  car.angle -= 19
          if choice == 27:
                  car.angle -= 20
          if choice == 28:
                  car.angle -= 21
          if choice == 29:
                  car.angle -= 22
          if choice == 30:
                  car.angle -= 23
          if choice == 31:
                  car.angle -= 24
          if choice == 32:
                  car.angle -= 25
          if choice == 33:
                  car.angle -= 26
          if choice == 34:
                  car.angle -= 27
          if choice == 35:
                  car.angle -= 28
          if choice == 36:
                  car.angle -= 29
          if choice == 37:
                  car.angle -= 30
          if choice == 38:
                  car.angle += 0
          if choice == 39:
                  car.angle += 1
          if choice == 40:
                  car.angle += 2
          if choice == 41:
                  car.angle += 3
          if choice == 42:
                  car.angle += 4
          if choice == 43:
                  car.angle += 5
          if choice == 44:
                  car.angle += 6
          if choice == 45:
                  car.angle += 7
          if choice == 46:
                  car.angle += 8
          if choice == 47:
                  car.angle += 9
          if choice == 48:
                  car.angle += 10
          if choice == 49:
                  car.angle += 11
          if choice == 50:
                  car.angle += 12
          if choice == 51:
                  car.angle += 13
          if choice == 52:
                  car.angle += 14
          if choice == 53:
                  car.angle += 15
          if choice == 54:
                  car.angle += 16
          if choice == 55:
                  car.angle += 17
          if choice == 56:
                  car.angle += 18
          if choice == 57:
                  car.angle += 19
          if choice == 58:
                  car.angle += 20
          if choice == 59:
                  car.angle += 21
          if choice == 60:
                  car.angle += 22
          if choice == 61:
                  car.angle += 23
          if choice == 62:
                  car.angle += 24
          if choice == 63:
                  car.angle += 25
          if choice == 64:
                  car.angle += 26
          if choice == 65:
                  car.angle += 27
          if choice == 66:
                  car.angle += 28
          if choice == 67:
                  car.angle += 29
          if choice == 68:
                  car.angle += 30
          if choice == 69:
                  car.speed -= 0
          if choice == 70:
                  car.speed -= 1
          if choice == 71:
                  car.speed -= 2
          if choice == 72:
                  car.speed -= 3
          if choice == 73:
                  car.speed -= 4
          if choice == 74:
                  car.speed -= 5
          if choice == 75:
                  car.speed -= 6
          if choice == 76:
                  car.speed -= 7
          if choice == 77:
                  car.speed -= 8
          if choice == 78:
                  car.speed -= 9
          if choice == 79:
                  car.speed -= 10
          if choice == 80:
                  car.speed -= 11
          if choice == 81:
                  car.speed -= 12
          if choice == 82:
                  car.speed -= 13
          if choice == 83:
                  car.speed -= 14
          if choice == 84:
                  car.speed -= 15
          if choice == 85:
                  car.speed -= 16
          if choice == 86:
                  car.speed -= 17
          if choice == 87:
                  car.speed -= 18
          if choice == 88:
                  car.speed -= 19
          if choice == 89:
                  car.speed -= 20
          if choice == 90:
                  car.speed -= 21
          if choice == 91:
                  car.speed -= 22
          if choice == 92:
                  car.speed -= 23
          if choice == 93:
                  car.speed -= 24
          if choice == 94:
                  car.speed -= 25
          if choice == 95:
                  car.speed -= 26
          if choice == 96:
                  car.speed -= 27
          if choice == 97:
                  car.speed -= 28
          if choice == 98:
                  car.speed -= 29
          if choice == 99:
                  car.speed -= 30
          if choice == 100:
                  car.speed -= 31
          if choice == 101:
                  car.speed -= 32
          if choice == 102:
                  car.speed -= 33
          if choice == 103:
                  car.speed -= 34
          if choice == 104:
                  car.speed -= 35
          if choice == 105:
                  car.speed -= 36
          if choice == 106:
                  car.speed -= 37
          if choice == 107:
                  car.speed -= 38
          if choice == 108:
                  car.speed -= 39
          if choice == 109:
                  car.speed -= 40
          if choice == 110:
                  car.speed -= 41
          if choice == 111:
                  car.speed -= 42
          if choice == 112:
                  car.speed -= 43
          if choice == 113:
                  car.speed -= 44
          if choice == 114:
                  car.speed -= 45
          if choice == 115:
                  car.speed -= 46
          if choice == 116:
                  car.speed -= 47
          if choice == 117:
                  car.speed -= 48
          if choice == 118:
                  car.speed -= 49
          if choice == 119:
                  car.speed -= 50
          if choice == 120:
                  car.speed -= 51
          if choice == 121:
                  car.speed -= 52
          if choice == 122:
                  car.speed -= 53
          if choice == 123:
                  car.speed -= 54
          if choice == 124:
                  car.speed -= 55
          if choice == 125:
                  car.speed -= 56
          if choice == 126:
                  car.speed -= 57
          if choice == 127:
                  car.speed += 0
          if choice == 128:
                  car.speed += 1
          if choice == 129:
                  car.speed += 2
          if choice == 130:
                  car.speed += 3
          if choice == 131:
                  car.speed += 4
          if choice == 132:
                  car.speed += 5
          if choice == 133:
                  car.speed += 6
          if choice == 134:
                  car.speed += 7
          if choice == 135:
                  car.speed += 8
          if choice == 136:
                  car.speed += 9
          if choice == 137:
                  car.speed += 10
          if choice == 138:
                  car.speed += 11
          if choice == 139:
                  car.speed += 12
          if choice == 140:
                  car.speed += 13
          if choice == 141:
                  car.speed += 14
          if choice == 142:
                  car.speed += 15
          if choice == 143:
                  car.speed += 16
          if choice == 144:
                  car.speed += 17
          if choice == 145:
                  car.speed += 18
          if choice == 146:
                  car.speed += 19
          if choice == 147:
                  car.speed += 20
          if choice == 148:
                  car.speed += 21
          if choice == 149:
                  car.speed += 22
          if choice == 150:
                  car.speed += 23
          if choice == 151:
                  car.speed += 24
          if choice == 152:
                  car.speed += 25
          if choice == 153:
                  car.speed += 26
          if choice == 154:
                  car.speed += 27
          if choice == 155:
                  car.speed += 28
          if choice == 156:
                  car.speed += 29
          if choice == 157:
                  car.speed += 30
          if choice == 158:
                  car.speed += 31
          if choice == 159:
                  car.speed += 32
          if choice == 160:
                  car.speed += 33
          if choice == 161:
                  car.speed += 34
          if choice == 162:
                  car.speed += 35
          if choice == 163:
                  car.speed += 36
          if choice == 164:
                  car.speed += 37
          if choice == 165:
                  car.speed += 38
          if choice == 166:
                  car.speed += 39
          if choice == 167:
                  car.speed += 40
          if choice == 168:
                  car.speed += 41
          if choice == 169:
                  car.speed += 42
          if choice == 170:
                  car.speed += 43
          if choice == 171:
                  car.speed += 44
          if choice == 172:
                  car.speed += 45
          if choice == 173:
                  car.speed += 46
          if choice == 174:
                  car.speed += 47
          if choice == 175:
                  car.speed += 48
          if choice == 176:
                  car.speed += 49
          if choice == 177:
                  car.speed += 50
          if choice == 178:
                  car.speed += 51
          if choice == 179:
                  car.speed += 52
          if choice == 180:
                  car.speed += 53
          if choice == 181:
                  car.speed += 54
          if choice == 182:
                  car.speed += 55
          if choice == 183:
                  car.speed += 56
          if choice == 184:
                  car.speed += 57
          if choice == 185:
                  car.speed += 58
          if choice == 186:
                  car.speed += 59
          if choice == 187:
                  car.speed += 60
          if choice == 188:
                  car.speed += 61
          if choice == 189:
                  car.speed += 62
          if choice == 190:
                  car.speed += 63
          if choice == 191:
                  car.speed += 64
          if choice == 192:
                  car.speed += 65
          if choice == 193:
                  car.speed += 66
          if choice == 194:
                  car.speed += 67
          if choice == 195:
                  car.speed += 68
          if choice == 196:
                  car.speed += 69
          if choice == 197:
                  car.speed += 70
          if choice == 198:
                  car.speed += 71
          if choice == 199:
                  car.speed += 72
          if choice == 200:
                  car.speed += 73
          if choice == 201:
                  car.speed += 74
          if choice == 202:
                  car.speed += 75
          if choice == 203:
                  car.speed += 76
          if choice == 204:
                  car.speed += 77
          if choice == 205:
                  car.speed += 78
          if choice == 206:
                  car.speed += 79
          if choice == 207:
                  car.speed += 80
          if choice == 208:
                  car.speed += 81
          if choice == 209:
                  car.speed += 82
          if choice == 210:
                  car.speed += 83
          if choice == 211:
                  car.speed += 84
          if choice == 212:
                  car.speed += 85
          if choice == 213:
                  car.speed += 86
          if choice == 214:
                  car.speed += 87
          if choice == 215:
                  car.speed += 88
          if choice == 216:
                  car.speed += 89
          if choice == 217:
                  car.speed += 90
          if choice == 218:
                  car.speed += 91
          if choice == 219:
                  car.speed += 92
          if choice == 220:
                  car.speed += 93
          if choice == 221:
                  car.speed += 94
          if choice == 222:
                  car.speed += 95
          if choice == 223:
                  car.speed += 96
          if choice == 224:
                  car.speed += 97
          if choice == 225:
                  car.speed += 98
          if choice == 226:
                  car.speed += 99
          if choice == 227:
                  car.speed += 100
          if choice == 228:
                  car.speed += 101
          if choice == 229:
                  car.speed += 102
          if choice == 230:
                  car.speed += 103
          if choice == 231:
                  car.speed += 104
          if choice == 232:
                  car.speed += 105
          if choice == 233:
                  car.speed += 106
          if choice == 234:
                  car.speed += 107
          if choice == 235:
                  car.speed += 108
          if choice == 236:
                  car.speed += 109
          if choice == 237:
                  car.speed += 110
          if choice == 238:
                  car.speed += 111
          if choice == 239:
                  car.speed += 112
          if choice == 240:
                  car.speed += 113
          if choice == 241:
                  car.speed += 114
          if choice == 242:
                  car.speed += 115
          if choice == 243:
                  car.speed += 116
          if choice == 244:
                  car.speed += 117
          if choice == 245:
                  car.speed += 118
          if choice == 246:
                  car.speed += 119
          if choice == 247:
                  car.speed += 120
          if choice == 248:
                  car.speed += 121
          if choice == 249:
                  car.speed += 122
          if choice == 250:
                  car.speed += 123
          if choice == 251:
                  car.speed += 124
          if choice == 252:
                  car.speed += 125
          if choice == 253:
                  car.speed += 126
          if choice == 254:
                  car.speed += 127
          if choice == 255:
                  car.speed += 128
          if choice == 256:
                  car.speed += 129
          if choice == 257:
                  car.speed += 130
          if choice == 258:
                  car.speed += 131
          if choice == 259:
                  car.speed += 132
          if choice == 260:
                  car.speed += 133
          if choice == 261:
                  car.speed += 134
          if choice == 262:
                  car.speed += 135
          if choice == 263:
                  car.speed += 136
          if choice == 264:
                  car.speed += 137
          if choice == 265:
                  car.speed += 138
          if choice == 266:
                  car.speed += 139
          if choice == 267:
                  car.speed += 140
          if choice == 268:
                  car.speed += 141
          if choice == 269:
                  car.speed += 142
          if choice == 270:
                  car.speed += 143
          if choice == 271:
                  car.speed += 144
          if choice == 272:
                  car.speed += 145
          if choice == 273:
                  car.speed += 146
          if choice == 274:
                  car.speed += 147
          if choice == 275:
                  car.speed += 148
          if choice == 276:
                  car.speed += 149
          if choice == 277:
                  car.speed += 150
          if choice == 278:
                  car.speed += 151
          if choice == 279:
                  car.speed += 152
          if choice == 280:
                  car.speed += 153
          if choice == 281:
                  car.speed += 154
          if choice == 282:
                  car.speed += 155
          if choice == 283:
                  car.speed += 156
          if choice == 284:
                  car.speed += 157
          if choice == 285:
                  car.speed += 158
          if choice == 286:
                  car.speed += 159
          if choice == 287:
                  car.speed += 160
          if choice == 288:
                  car.speed += 161
          if choice == 289:
                  car.speed += 162
          if choice == 290:
                  car.speed += 163
          if choice == 291:
                  car.speed += 164
          if choice == 292:
                  car.speed += 165
          if choice == 293:
                  car.speed += 166
          if choice == 294:
                  car.speed += 167
          if choice == 295:
                  car.speed += 168
          if choice == 296:
                  car.speed += 169
          if choice == 297:
                  car.speed += 170
          if choice == 298:
                  car.speed += 171
          if choice == 299:
                  car.speed += 172
          if choice == 300:
                  car.speed += 173
          if choice == 301:
                  car.speed += 174
          if choice == 302:
                  car.speed += 175
          if choice == 303:
                  car.speed += 176
          if choice == 304:
                  car.speed += 177
          if choice == 305:
                  car.speed += 178
          if choice == 306:
                  car.speed += 179
          if choice == 307:
                  car.speed += 180
          if choice == 308:
                  car.speed += 181
          if choice == 309:
                  car.speed += 182
          if choice == 310:
                  car.speed += 183
          if choice == 311:
                  car.speed += 184
          if choice == 312:
                  car.speed += 185
          if choice == 313:
                  car.speed += 186
          if choice == 314:
                  car.speed += 187
          if choice == 315:
                  car.speed += 188
          if choice == 316:
                  car.speed += 189
          if choice == 317:
                  car.speed += 190
          if choice == 318:
                  car.speed += 191
          if choice == 319:
                  car.speed += 192
          if choice == 320:
                  car.speed += 193
          if choice == 321:
                  car.speed += 194
          if choice == 322:
                  car.speed += 195
          if choice == 323:
                  car.speed += 196
          if choice == 324:
                  car.speed += 197
          if choice == 325:
                  car.speed += 198
          if choice == 326:
                  car.speed += 199
          if choice == 327:
                  car.speed += 200
          if car.speed <= 0:
                  car.speed += 200
        # Check If Car Is Still Alive
        # Increase Fitness If Yes And Break Loop If Not
        still_alive = 0
        for i, car in enumerate(cars):
            if car.is_alive():
                still_alive += 1
                car.update(game_map)
                genomes[i][1].fitness += car.get_reward()

        if still_alive == 0:
            break

        counter += 1
        if counter == 30 * 40: # Stop After About 20 Seconds
            break

        # Draw Map And All Cars That Are Alive
        screen.blit(game_map, (0, 0))
        for car in cars:
            if car.is_alive():
                car.draw(screen)

        # Display Info
        text = generation_font.render("Generation: " + str(current_generation), True, (0,0,0))
        text_rect = text.get_rect()
        text_rect.center = (900, 450)
        screen.blit(text, text_rect)

        text = alive_font.render("Still Alive: " + str(still_alive), True, (0, 0, 0))
        text_rect = text.get_rect()
        text_rect.center = (900, 490)
        screen.blit(text, text_rect)

        pygame.display.flip()
        clock.tick(60) # 60 FPS

if __name__ == "__main__":

    # Load Config
    config_path = "./config.txt"
    config = neat.config.Config(neat.DefaultGenome,
                                neat.DefaultReproduction,
                                neat.DefaultSpeciesSet,
                                neat.DefaultStagnation,
                                config_path)

    # Create Population And Add Reporters
    population = neat.Population(config)
    population.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    population.add_reporter(stats)

    # Run Simulation For A Maximum of 1000 Generations
population.run(run_simulation, 1000000)

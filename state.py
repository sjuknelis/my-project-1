import json, math
from typing import List

from constants import WIDTH, HEIGHT, CAR_SIZE
STATE_FILE = "small_loop.json"

class Car:
    pos = (WIDTH // 2, HEIGHT // 2)
    speed = 0
    angle = 0
    turn_speed = 0
    crash_speed = None

    def get_points(self):
        return [
            (
                self.pos[0] + CAR_SIZE * math.cos(math.radians(self.angle + offset_angle)),
                self.pos[1] - CAR_SIZE * math.sin(math.radians(self.angle + offset_angle))
            )
            for offset_angle in range(-120, 120 + 120, 120)
        ]

class Action:
    def __init__(self, acc: int, steer: int):
        self.acc = acc
        self.steer = steer

    def __str__(self):
        return f"Action({self.acc}, {self.steer})"

class State:
    car = Car()

    tracks = []
    checkpoints = []
    checkpoint_index = 0

    rays = []
    reward = 0

    actions = [
        Action(0, 0),  # none
        Action(1, 0),  # acc
        Action(0, -1), # left
        Action(0, 1)   # right
    ]

    def __init__(self):
        self.reset()

    def reset(self):
        with open(STATE_FILE, "r") as f:
            data = json.load(f)

            self.car.pos = data["pos"][0:2]
            self.car.angle = data["pos"][2]

            self.tracks = data["tracks"]
            self.checkpoints = data["checkpoints"]

    def save_to_file(self):
        with open("track.json", "w") as f:
            json.dump({
                "pos": list(self.car.pos) + [self.car.angle],
                "tracks": self.tracks,
                "checkpoints": self.checkpoints
            }, f)

    def get_ai_features(self) -> List[float]:
        line_magnitude = lambda line: math.sqrt((line[0][0] - line[1][0]) ** 2 + (line[0][1] - line[1][1]) ** 2)

        features = [self.car.speed] + [line_magnitude(ray) for ray in self.rays]
        if len([length for length in features[1:] if length > 500]) > 0:
            self.reset()
        return features
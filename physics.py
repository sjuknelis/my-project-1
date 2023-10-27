import math

from state import State, Action
from constants import CAR_SIZE, CHECKPOINT_SIZE

MAX_SPEED = 5
ACCELERATION = 0.2
DECELERATION = 0.05
MAX_TURN_SPEED = 3
TURN_ACCELERATION = 0.5
COLLISION_SPEED = 1.5

"""
10/25
Daily Duotrigordle #602
Guesses: 37/37
2️⃣1️⃣ 0️⃣6️⃣ 2️⃣0️⃣ 1️⃣5️⃣
1️⃣4️⃣ 3️⃣7️⃣ 3️⃣6️⃣ 1️⃣3️⃣
2️⃣3️⃣ 2️⃣2️⃣ 1️⃣6️⃣ 3️⃣5️⃣
2️⃣5️⃣ 2️⃣4️⃣ 0️⃣7️⃣ 3️⃣4️⃣
0️⃣8️⃣ 3️⃣3️⃣ 0️⃣9️⃣ 2️⃣6️⃣
1️⃣7️⃣ 1️⃣9️⃣ 1️⃣8️⃣ 1️⃣0️⃣
2️⃣9️⃣ 2️⃣7️⃣ 2️⃣8️⃣ 1️⃣2️⃣
3️⃣2️⃣ 3️⃣0️⃣ 3️⃣1️⃣ 1️⃣1️⃣
https://duotrigordle.com/
"""

def find_intersection(segment1, segment2):
    # Unpack the endpoints of the line segments
    (x1, y1), (x2, y2) = segment1
    (x3, y3), (x4, y4) = segment2

    # Calculate the determinants
    det = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)

    # Check if the lines are parallel (det == 0)
    if det == 0:
        return None  # No intersection

    # Calculate the intersection point
    intersection_x = ((x1 * y2 - y1 * x2) * (x3 - x4) - (x1 - x2) * (x3 * y4 - y3 * x4)) / det
    intersection_y = ((x1 * y2 - y1 * x2) * (y3 - y4) - (y1 - y2) * (x3 * y4 - y3 * x4)) / det

    # Check if the intersection point is within the segments
    if (
        min(x1, x2) - 1 <= intersection_x <= max(x1, x2) + 1 and
        min(x3, x4) - 1 <= intersection_x <= max(x3, x4) + 1 and
        min(y1, y2) - 1 <= intersection_y <= max(y1, y2) + 1 and
        min(y3, y4) - 1 <= intersection_y <= max(y3, y4) + 1
    ):
        return (intersection_x, intersection_y)
    else:
        return None
    
def physics_transform_state(state: State, action: Action):
    state.reward = 0

    car = state.car

    # Accelerate and steer with finite limits
    if action.acc == 1:
        car.speed = min(car.speed + ACCELERATION, MAX_SPEED)
    elif action.acc == -1:
        car.speed = max(car.speed - DECELERATION, -MAX_SPEED)
    else:
        if car.speed > 0:
            car.speed = max(car.speed - DECELERATION, 0)
        elif car.speed < 0:
            car.speed = min(car.speed + DECELERATION, 0)

    if action.steer == -1:
        car.turn_speed = min(car.turn_speed + TURN_ACCELERATION, MAX_TURN_SPEED)
    elif action.steer == 1:
        car.turn_speed = max(car.turn_speed - TURN_ACCELERATION, -MAX_TURN_SPEED)
    else:
        if car.turn_speed > 0:
            car.turn_speed = max(car.turn_speed - TURN_ACCELERATION, 0)
        elif car.turn_speed < 0:
            car.turn_speed = min(car.turn_speed + TURN_ACCELERATION, 0)

    # Move the car
    car.angle += car.turn_speed

    car.pos = (
        car.pos[0] + car.speed * math.cos(math.radians(car.angle)),
        car.pos[1] - car.speed * math.sin(math.radians(car.angle))
    )

    # Get checkpoint reward
    if len(state.checkpoints) != 0:
        checkpoint = state.checkpoints[state.checkpoint_index]
        if (
            car.pos[0] >= checkpoint[0] - CHECKPOINT_SIZE and
            car.pos[0] <= checkpoint[0] + CHECKPOINT_SIZE and
            car.pos[1] >= checkpoint[1] - CHECKPOINT_SIZE and
            car.pos[1] <= checkpoint[1] + CHECKPOINT_SIZE
        ):
            state.reward = 10
            state.checkpoint_index = (state.checkpoint_index + 1) % len(state.checkpoints)

    car_points = car.get_points()

    # Find coordinates of raycasting lines
    state.rays = []
    for offset_angle in range(-60, 60 + 30, 30):
        ray = (
            car_points[1],
            (
                car.pos[0] + 1000 * math.cos(math.radians(car.angle + offset_angle)),
                car.pos[1] - 1000 * math.sin(math.radians(car.angle + offset_angle))
            )
        )

        for track in state.tracks:
            intersection = find_intersection(track, ray)
            if intersection is not None:
                ray = (car_points[1], intersection)

        state.rays.append(ray)

    # Don't allow collisions
    did_crash = False
    for track in state.tracks:
        if find_intersection(track, car_points[0:2]) is not None or find_intersection(track, car_points[1:]) is not None:
            if car.crash_speed is None:
                car.crash_speed = car.speed
            car.speed = -COLLISION_SPEED * (1 if car.crash_speed > 0 else -1)
            car.turn_speed = 0
            did_crash = True
            if state.reward == 0:
                state.reward = -1
    if not did_crash:
        car.crash_speed = None
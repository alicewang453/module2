import serial
import datetime
import json
import pygame
import sys
import math


pygame.init()
ser = serial.Serial('/dev/cu.usbserial-56230075411', 115200, timeout=1)


# Window settings
screen_size = (800, 600)
screen = pygame.display.set_mode(screen_size)
pygame.display.set_caption('Plant Simulation')

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 128, 0)
SICK_GREEN = (128, 140, 128)
BROWN = (165, 42, 42)
BLUE = (0, 0, 255)
LIGHTGREY = (192,192,192)
LIGHTBLUE = (173, 216, 230)
YELLOW = (255, 255, 0)
GOLD = (224, 153, 0)
DARK_GREY = (64, 78, 77)


# Initial game state

def initialize_game_state():
    global game_state, start_time, current_day
    start_time = datetime.datetime.now()
    loaded_state = load_game_state()
    if loaded_state:
        game_state = loaded_state 
        current_day = game_state.get('current_day', 0)
    else:
        game_state = {
            'plant_height': 0,
            'plant_color': GREEN,
            'last_watered': datetime.datetime.now().isoformat(),
            'last_checked': datetime.datetime.now().isoformat(),
            'watered_today': False
        }
        current_day = 0

def reset():
    global game_state, start_time, current_day
    start_time = datetime.datetime.now()
    game_state = {
        'plant_height': 0,
        'plant_color': GREEN,
        'last_watered': datetime.datetime.now().isoformat(),
        'last_checked': datetime.datetime.now().isoformat(),
        'watered_today': False
    }
    current_day = 0

    # Add any other initializations needed here


# Update threshold for potentiometer
UPDATE_THRESHOLD = 200
last_significant_pot_value = 0
# leaf threshold 
LEAF1_DRAW_THRESHOLD = 50  # Example threshold for plant height to start drawing leaves
LEAF2_DRAW_THRESHOLD = 80

# initial curtain coverage
curtain_coverage = 100
optimal_curtain_coverage_range = (30, 70)

# Calculate max coverage of curtains
max_coverage_per_side = screen_size[0] // 2

# watering can variables  
watering_can_pos = (600, 470)
watering_animation = False 
frame_count = 0

def lerp(start, end, alpha):
    return (1 - alpha) * start + alpha * end

# Functions for game state
def load_game_state():
    try:
        with open('game_state.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return game_state

def save_game_state(state, curtain_coverage):
    state['curtain_coverage'] = curtain_coverage
    state['current_day'] = current_day
    # state['start_time'] = start_time.isoformat()  # Save as ISO format string
    # state['current_day'] = current_day

    with open('game_state.json', 'w') as f:
        json.dump(state, f)

# def update_plant_growth(state, curtain_coverage):
#     current_time = datetime.datetime.now()
#     last_checked = datetime.datetime.fromisoformat(state['last_checked'])
#     last_watered = datetime.datetime.fromisoformat(state['last_watered'])

#     time_difference = (current_time - last_checked).total_seconds() / 60.0

#     # Check if a week has passed since last check
#     # if (current_time - last_checked).days >= 7:

#     if time_difference >= 1:
#         # Determine if care was adequate
#         # watered_recently = (current_time - last_watered).days <= 7
#         watered_recently = (current_time - datetime.datetime.fromisoformat(state['last_watered'])).total_seconds() / 60.0 <= 1

#         # light_was_optimal = True  # Placeholder, adjust based on your curtain logic
        
#         curtain_coverage_percent = (curtain_coverage / (screen_size[0] / 2)) * 100
#         light_was_optimal = optimal_curtain_coverage_range[0] <= curtain_coverage_percent <= optimal_curtain_coverage_range[1]
        
#         if watered_recently and light_was_optimal:
#             state['plant_height'] += 10  # Grow a bit
#             state['plant_color'] = GREEN
#         else:
#             state['plant_height'] = max(10, state['plant_height'] - 10)  # Shrink a bit but not below 10
#             state['plant_color'] = SICK_GREEEN  # Change color to greyish
        
#         state['last_checked'] = current_time.isoformat()  # Update the last checked time
    
#     return state
        
def update_plant_growth():
    # This function now simply checks if conditions were met yesterday for growth.
    # Assuming this function is called right after the day advances.
    if game_state['watered_today']:
        # Check if light conditions were also optimal yesterday.
        curtain_coverage_percent = (curtain_coverage / (screen_size[0] / 2)) * 100
        light_was_optimal = optimal_curtain_coverage_range[0] <= curtain_coverage_percent <= optimal_curtain_coverage_range[1]
        
        if light_was_optimal:
            game_state['plant_height'] += 10  # Grow a bit
            game_state['plant_color'] = GREEN
        else:
            # Conditions were not optimal for growth; apply any penalties or maintain current state.
            game_state['plant_height'] += 5  # Grow a bit
            game_state['plant_color'] = SICK_GREEN
    else:
        # No watering happened yesterday; apply any penalties or maintain current state.
        game_state['plant_height'] = max(0, game_state['plant_height'] - 10)  # Example penalty
        game_state['plant_color'] = SICK_GREEN


def draw_sun_rays(surface, center, radius, num_rays, ray_length, ray_width, color):
    angle_between_rays = 360 / num_rays
    for i in range(num_rays):
        # Calculate the angle for this ray
        angle = math.radians(angle_between_rays * i)
        # Calculate the start point (on the circle) and end point (outside the circle) of the ray
        start_point = (
            center[0] + radius * math.cos(angle),
            center[1] + radius * math.sin(angle)
        )
        end_point = (
            center[0] + (radius + ray_length) * math.cos(angle),
            center[1] + (radius + ray_length) * math.sin(angle)
        )
        # Draw the ray
        pygame.draw.line(surface, color, start_point, end_point, ray_width)


# Function to draw the initial scene
def draw_scene(curtain_coverage, plant_height, plant_color, watering_can_x, watering_can_y):
    screen.fill(LIGHTBLUE) 

    # Draw the sun
    sun_center = (screen_size[0] - 250, 150)
    sun_radius = 75
    pygame.draw.circle(screen, YELLOW, sun_center, sun_radius)

    # Draw the sun rays
    draw_sun_rays(screen, sun_center, sun_radius, 12, 20, 4, YELLOW)

    # Curtains 
    pygame.draw.rect(screen, DARK_GREY, pygame.Rect(0, 0, curtain_coverage, screen_size[1]))
    pygame.draw.rect(screen, DARK_GREY, pygame.Rect(screen_size[0] - curtain_coverage, 0, curtain_coverage, screen_size[1]))

    # POT 
    pygame.draw.rect(screen, BROWN, pygame.Rect(335, 420, 130, 30))
    pygame.draw.rect(screen, BROWN, pygame.Rect(350, 450, 100, 50))

    # Plant Growth  
    pygame.draw.rect(screen, plant_color, pygame.Rect(395, 420 - plant_height, 10, plant_height))

    if plant_height > LEAF1_DRAW_THRESHOLD:
        # Define points for a simple leaf shape using polygons
        leaf_points = [(395 -15, 420 - LEAF1_DRAW_THRESHOLD + 10),  # Leaf base, adjust positioning as needed
                       (395 - 30, 420 - LEAF1_DRAW_THRESHOLD),  # Top left of the leaf
                       (395, 420 - LEAF1_DRAW_THRESHOLD)]  # Top right of the leaf
        pygame.draw.polygon(screen, plant_color, leaf_points)

    if plant_height > LEAF2_DRAW_THRESHOLD:
        # Define points for a simple leaf shape using polygons
        leaf_points = [(405 + 15, 420 - LEAF2_DRAW_THRESHOLD + 10),  # Leaf base, adjust positioning as needed
                       (405, 420 - LEAF2_DRAW_THRESHOLD),  # Top left of the leaf
                       (405 + 30, 420 - LEAF2_DRAW_THRESHOLD)]  # Top right of the leaf
        pygame.draw.polygon(screen, plant_color, leaf_points)
    
    # Watering can
    pygame.draw.rect(screen, BLUE, pygame.Rect(watering_can_x, watering_can_y, 50, 30))
    # pygame.draw.polygon(screen, BLUE, [(650, 100), (700, 100), (720, 130), (630, 130)])
    
    # Ledge 
    pygame.draw.rect(screen, GOLD, pygame.Rect(0, 500, 800, 100))

    # counter 
    pygame.draw.rect(screen, GOLD, pygame.Rect(30, 30, 290, 120))
    pygame.draw.rect(screen, WHITE, pygame.Rect(40, 40, 270, 100))
    font = pygame.font.SysFont(None, 36)
    day_counter_text = font.render(f"Day {current_day}", True, BLACK)
    screen.blit(day_counter_text, (60, 60))
    watered_text = "Yes" if game_state['watered_today'] else "No"
    watered_today_text = font.render(f"Watered today: {watered_text}", True, BLACK)
    screen.blit(watered_today_text, (60, 100))


    # instructions 
    pygame.draw.rect(screen, WHITE, pygame.Rect(510, 520, 250, 60))
    # pygame.draw.rect(screen, GOLD , pygame.Rect(610, 530, 160, 40))
    font = pygame.font.SysFont(None, 22)
    reset_text = font.render(f"Press 'r' to reset", True, BLACK)
    screen.blit(reset_text, (520, 530))
    skip_text = font.render(f"Press 's' to skip forward in time", True, BLACK)
    screen.blit(skip_text, (520, 555))

def update_day_counter():
    global current_day, start_time
    current_time = datetime.datetime.now()
    elapsed_time = current_time - start_time
    new_day = int(elapsed_time.total_seconds() / 60.0)  # Assuming 1 game day per minute for demonstration

    # Check if a new day has started
    if new_day > current_day:
        update_plant_growth()
        current_day = new_day
        game_state['watered_today'] = False  # Reset watering indicator for the new day
        

def advance_to_next_day():
    global current_day
    update_plant_growth()
    current_day += 1
    game_state['watered_today'] = False
    game_state['last_checked'] = datetime.datetime.now().isoformat()
    # Optionally trigger daily growth or other checks here
    # update_plant_growth(curtain_coverage)
    print(f"Advanced to day {current_day}.")



# Main game loop
initialize_game_state()
# game_state = load_game_state()
last_print_time = datetime.datetime.now()

# if 'start_time' in game_state and 'current_day' in game_state:
#     start_time = datetime.datetime.fromisoformat(game_state['start_time'])
#     current_day = game_state['current_day']
# else:
#     # If starting a new game
#     start_time = datetime.datetime.now()
#     current_day = 0
#     # Update game_state dictionary if you plan to save these values
#     game_state['start_time'] = start_time.isoformat()
#     game_state['current_day'] = current_day


running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            # if event.key == pygame.K_w:  # Press 'W' to water the plant
                # game_state['last_watered'] = datetime.datetime.now().isoformat()
                # print("watered")
                # game_state['watered_today'] = True
                # watering_can_target_y = 420 - game_state['plant_height'] - 50  # 50 pixels above the current plant height
                # watering_can_target = (375, watering_can_target_y)

                # watering_animation = True
                # frame_count = 0
            if event.key == pygame.K_s:  # If 'S' is pressed, speed up to the next day
                advance_to_next_day()
            if event.key == pygame.K_r:  # Let's use 'R' for reset
                reset()
                print("Game reset!")


    # # i think this is just printing the current game state
    # current_time = datetime.datetime.now()
    # if (current_time - last_print_time).total_seconds() >= 60:  # Checks if at least one minute has passed
    #     # Print the current game state
    #     print("Current game state:", game_state)
    #     print(f"Current plant height: {game_state['plant_height']}, Color: {game_state['plant_color']}, Last Watered: {game_state['last_watered']}")
        
    #     # Update last_print_time to the current time
    #     last_print_time = current_time
    update_day_counter()
    
    # Read serial data
    if ser.in_waiting > 0:
        pot_line = ser.readline().decode('utf-8').rstrip()
        print("line:", pot_line)
        
        pot_line_clean = pot_line.lower().strip()
        _, value = pot_line_clean.split("potentiometer value: ", 1) 
        potValue = int(value.strip())  
        print("potValue", potValue)

        button_line = ser.readline().decode('utf-8').rstrip()
        print("line:", button_line)
        
        button_line_clean = button_line.lower().strip()
        _, value = button_line_clean.split("button state: ", 1) 
        butValue = int(value.strip())  
        print("butVal", butValue)

        # Only update curtain_coverage if change exceeds threshold
        change_since_last_update = abs(potValue - last_significant_pot_value)
        if change_since_last_update > UPDATE_THRESHOLD:
            curtain_coverage = (potValue * max_coverage_per_side) // 4096
            last_significant_pot_value = potValue

        if butValue == 0: 
            game_state['last_watered'] = datetime.datetime.now().isoformat()
            print("watered")
            game_state['watered_today'] = True
            watering_can_target_y = 420 - game_state['plant_height'] - 50  # 50 pixels above the current plant height
            watering_can_target = (375, watering_can_target_y)

            watering_animation = True
            frame_count = 0

    if watering_animation:
        print("water animation")
        frame_count += 1
        if frame_count <= 30:  # Move towards the plant for 30 frames
            watering_can_x = lerp(watering_can_pos[0], watering_can_target[0], frame_count / 30.0)
            watering_can_y = lerp(watering_can_pos[1], watering_can_target[1], frame_count / 30.0)
        elif frame_count <= 60:  # Pause over the plant for 30 frames
            watering_can_x, watering_can_y = watering_can_target
        elif frame_count <= 90:  # Return to original position for 30 frames
            watering_can_x = lerp(watering_can_target[0], watering_can_pos[0], (frame_count - 60) / 30.0)
            watering_can_y = lerp(watering_can_target[1], watering_can_pos[1], (frame_count - 60) / 30.0)
        else:  # Reset animation state
            watering_animation = False
            frame_count = 0
    else:
        watering_can_x, watering_can_y = watering_can_pos

    # update_day_counter()

    # update_plant_growth()


    draw_scene(curtain_coverage, game_state['plant_height'], game_state['plant_color'], watering_can_x, watering_can_y)
    
    pygame.display.flip()

save_game_state(game_state, curtain_coverage)
pygame.quit()
sys.exit()

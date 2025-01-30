import random
from enum import Enum
import pygame
import sys
from os import path
import numpy as np
import random


class MoveAction(Enum):
    LEFT = 0  
    DOWN = 1   
    RIGHT = 2  
    UP = 3     



class DeliveryRobotAndCars:
    def __init__(self, grid_rows=5, grid_cols=30, fps=5, obstacles=None, num_cars=None, obstacle_matrix = None):
        self.grid_rows = grid_rows
        self.grid_cols = grid_cols
        self.obstacle_matrix = obstacle_matrix if obstacle_matrix else []
        self.num_cars = num_cars
        self.reset()
        self.fps = fps
        self.last_action_robot = ''
        self.last_action_cars = [''] * self.num_cars  
        self.total_reward = 0
        self._init_pygame()

    def _init_pygame(self):
        pygame.init()
        pygame.display.init()
        self.clock = pygame.time.Clock()
        self.action_font = pygame.font.SysFont("Calibre", 30)
        self.action_info_height = self.action_font.get_height()

        self.cell_height = 30
        self.cell_width = 30
        self.cell_size = (self.cell_width, self.cell_height)

        self.window_size = (self.cell_width * self.grid_cols,
                            self.cell_height * self.grid_rows + self.action_info_height)
        self.window_surface = pygame.display.set_mode(self.window_size)

        # Load images
        file_name = path.join(path.dirname(__file__), "sprites/bot_blue.png")
        img = pygame.image.load(file_name)
        self.robot_img = pygame.transform.scale(img, self.cell_size)

        file_name = path.join(path.dirname(__file__), "sprites/car.png")
        img = pygame.image.load(file_name)
        self.car_img = pygame.transform.scale(img, self.cell_size)

        file_name = path.join(path.dirname(__file__), "sprites/floor.png")
        img = pygame.image.load(file_name)
        self.floor_img = pygame.transform.scale(img, self.cell_size)

        file_name = path.join(path.dirname(__file__), "sprites/package.png")
        img = pygame.image.load(file_name)
        self.goal_img = pygame.transform.scale(img, self.cell_size)

        file_name = path.join(path.dirname(__file__), "sprites/obstacle.png")
        img = pygame.image.load(file_name)
        self.obstacle_img = pygame.transform.scale(img, self.cell_size)

    def reset(self, seed=None):
        self.robot_pos = [ 1, 1]
        self.cars_pos = [[3, 6]] 
        self.car_steps = [random.randint(30, 85) for _ in range(self.num_cars)]
        random.seed(seed)

        
        self.target_pos = [ 1,29]
            

        self.obstacles = []
        for r in range(self.grid_rows):
            for c in range(self.grid_cols):
                if self.obstacle_matrix[r][c] == 1:
                    self.obstacles.append([r, c])

        while not self._is_path_clear():
            self.reset(seed)
        
    def _is_path_clear(self):
        from collections import deque
        visited = set()
        queue = deque([tuple(self.robot_pos)])
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]

        while queue:
            current = queue.popleft()
            if current == tuple(self.target_pos):
                return True

            for dr, dc in directions:
                new_pos = (current[0] + dr, current[1] + dc)

                if (0 <= new_pos[0] < self.grid_rows and
                        0 <= new_pos[1] < self.grid_cols and
                        new_pos not in visited and
                        list(new_pos) not in self.obstacles):
                    visited.add(new_pos)
                    queue.append(new_pos)

        return False

    def perform_action(self, entity, action):
        new_pos = entity[:]
        if action == MoveAction.LEFT:
            new_pos[1] -= 1
        elif action == MoveAction.RIGHT:
            new_pos[1] += 1
        elif action == MoveAction.UP:
            new_pos[0] -= 1
        elif action == MoveAction.DOWN:
            new_pos[0] += 1

        if self.is_valid_position(new_pos):
            entity[:] = new_pos
    def perform_car_action(self, car_index):
        """
        Car
        """
        car_pos = self.cars_pos[car_index]
        steps_left = self.car_steps[car_index]
        
        if steps_left <= 0:  
            return

        
        directions = [MoveAction.UP, MoveAction.DOWN, MoveAction.LEFT, MoveAction.RIGHT]
        random.shuffle(directions)  


        for action in directions:
          
            new_pos = car_pos[:]
            if action == MoveAction.LEFT:
                new_pos[1] -= 1
            elif action == MoveAction.RIGHT:
                new_pos[1] += 1
            elif action == MoveAction.UP:
                new_pos[0] -= 1
            elif action == MoveAction.DOWN:
                new_pos[0] += 1

            if self.is_valid_position(new_pos):
                self.cars_pos[car_index] = new_pos
                self.car_steps[car_index] -= 1  
                return

    
        for action in directions:
            new_pos = car_pos[:]
            if action == MoveAction.LEFT:
                new_pos[1] -= 1
            elif action == MoveAction.RIGHT:
                new_pos[1] += 1
            elif action == MoveAction.UP:
                new_pos[0] -= 1
            elif action == MoveAction.DOWN:
                new_pos[0] += 1

            
            if self.is_valid_position(new_pos):
                self.cars_pos[car_index] = new_pos
                self.car_steps[car_index] -= 1  
                return
    def is_valid_position(self, position):
        if position[0] < 0 or position[0] >= self.grid_rows or position[1] < 0 or position[1] >= self.grid_cols:
            return False
        if position in self.obstacles or position in self.cars_pos:
            return False
        return True

    def render(self):
        self._process_events()

        self.window_surface.fill((255, 255, 255))

        for r in range(self.grid_rows):
            for c in range(self.grid_cols):
                pos = (c * self.cell_width, r * self.cell_height)
                self.window_surface.blit(self.floor_img, pos)

                if [r, c] == self.target_pos:
                    self.window_surface.blit(self.goal_img, pos)

                if [r, c] == self.robot_pos:
                    self.window_surface.blit(self.robot_img, pos)

                for car_pos in self.cars_pos:
                    if [r, c] == car_pos:
                        self.window_surface.blit(self.car_img, pos)

                if [r, c] in self.obstacles:
                    self.window_surface.blit(self.obstacle_img, pos)

       

        pygame.display.update()
        self.clock.tick(self.fps)

    def _process_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()

    def check_collision(self):
        if self.robot_pos in self.cars_pos:
            print("Crash! Robot collided with a car.")
            pygame.quit()
            sys.exit()        
        elif self.robot_pos == self.target_pos:
            print("Win")
            pygame.quit()
            sys.exit()



obstacle_matrix = [
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
        [1, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]        
    ]   


new_game = DeliveryRobotAndCars(num_cars=1, obstacle_matrix=obstacle_matrix)
if __name__ == "__main__":
      
    while True:
        
        robot_action = random.choice(list(MoveAction))
        
        
        new_game.last_action_robot = robot_action

        new_game.perform_action(new_game.robot_pos, robot_action)
        for i in range(new_game.num_cars):
            new_game.perform_car_action(i)
        new_game.check_collision()

        new_game.render()
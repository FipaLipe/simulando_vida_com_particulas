# Importando bibliotecas
import pygame
import random
import math
import numpy as np
from matplotlib import pyplot as plt

class Game:
    def __init__(self, interactions, force_function, friction, width = 700, height = 700, max_fps = 60):
        self.running = True
        self.display = None
        self.clock = None
        self.width = width
        self.height = height
        self.size = (self.width, self.height)
        self.max_fps = max_fps
        self.particles = []

        self.interactions = interactions
        self.force_function = force_function
        self.friction = friction
    
    def on_init(self):
        pygame.init()
        self.display = pygame.display.set_mode(self.size)
        self.clock = pygame.time.Clock()
        return True

    def on_add_particle(self, particle):
        self.particles.append(particle)
    
    def on_event(self, event):
        if event.type == pygame.QUIT:
            self.running = False
    
    def on_loop(self):
        # Atualiza as partículas
        for particle in self.particles:            
            particle.on_loop(self.particles, self.force_function, self.interactions, self.friction)
        
        for particle in self.particles:    
            particle.update_position()

    def on_render(self):
        self.display.fill((20, 20, 20))

        for particle in self.particles:
            particle.on_render(self.display)

        pygame.display.flip()

    def on_cleanup(self):
        pygame.quit()

    def on_execute(self):
        self.running = self.on_init()

        while self.running:

            for event in pygame.event.get():
                self.on_event(event)

            self.on_loop()
            self.on_render()

            self.clock.tick(self.max_fps)

        self.on_cleanup()

class Species:
    def __init__(self, id, color, size = 1):
        self.id = id
        self.color = color
        self.size = size

class Particle:
    def __init__(self, species, position = None, velocity = None):
        self.species = species
        self.position = position
        if self.position == None:
            self.position = [0, 0]

        self.new_position = position.copy()
        self.velocity = velocity
        if self.velocity == None:
            self.velocity = [0, 0]
    
    def on_render(self, surface): 
        pygame.draw.circle(surface, self.species.color, self.position, self.species.size)
    
    def on_loop(self, particles, force_function, interactions, friction):
        force_x = 0
        force_y = 0

        for other_particle in particles:
            if other_particle.position == self.position:
                continue
        
            attraction, vision = interactions[self.species.id][other_particle.species.id]

            diff_x = other_particle.position[0] - self.position[0]
            diff_y = other_particle.position[1] - self.position[1]

            if abs(diff_x) >= vision or abs(diff_y) >= vision:
                continue

            distance = math.sqrt(diff_x ** 2 + diff_y ** 2)

            if distance > vision or distance <= 0:
                continue

            normal_distance = distance / vision

            force = force_function(normal_distance, attraction)

            force_x += force * (diff_x / distance)
            force_y += force * (diff_y / distance)

            # print(distance, diff_x, diff_y)
        
        self.velocity[0] += force_x
        self.velocity[1] += force_y

        self.new_position[0] += self.velocity[0]
        self.new_position[1] += self.velocity[1]

        self.velocity[0] *= 1 - friction
        if abs(self.velocity[0]) < 0.1:
            self.velocity[0] = 0
            
        self.velocity[1] *= 1 - friction
        if abs(self.velocity[1]) < 0.1:
            self.velocity[1] = 0

    def update_position(self):
        self.position = self.new_position

def instantiate_particles(number_of_particles, species, game):
    for i in range(number_of_particles):
        particle_species = random.choice(species)
        particle_x = random.randint(0, game.width)
        particle_y = random.randint(0, game.height)
        
        new_particle = Particle(particle_species, [particle_x, particle_y])
        game.on_add_particle(new_particle)

def force_function(dist, attraction):
    repulsion_intensity = -0.8
    repulsion_radius = 0.3

    if 0 <= dist < repulsion_radius:
        return dist * (-repulsion_intensity / repulsion_radius) + repulsion_intensity

    mid = repulsion_radius + ((1 - repulsion_radius) / 2)

    if repulsion_radius <= dist < mid:
        return (dist - repulsion_radius) * attraction / (mid - repulsion_radius)

    if mid <= dist <= 1:
        return -(1 - dist) * (-attraction / (1 - mid))

    return 0

# -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-

red_species = Species(0, (255,0,0), 4)
blue_species = Species(1, (0, 0, 255), 4)
yellow_species = Species(2, (255, 255, 0), 4)
species = [red_species, blue_species, yellow_species]

interactions = [
    [(0.3, 100), (-0.2, 100), (0.2, 100)],   # Vermelho com Vermelho | Vermelho com Azul | Vermelho com Amarelo
    [(0.3, 100), (0.3, 100), (-0.1, 100)],   # Azul com Vermelho     | Azul com Azul     | Azul com Amarelo
    [(-0.2, 100), (0.3, 100), (0.3, 100)],   # Amarelo com Vermelho  | Amarelo com Azul  | Amarelo com Amarelo
]

friction = 0.3

game = Game(interactions, force_function, friction)

instantiate_particles(300, species, game)

game.on_execute()
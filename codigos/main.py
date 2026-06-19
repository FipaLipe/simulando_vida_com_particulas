import pygame
import numpy as np

# =============================================
# CLASSES
# =============================================

class Species:
    def __init__(self, id, color, size=1):
        self.id = id
        self.color = color
        self.size = size


class Game:
    def __init__(self, interactions, force_function, friction, species, particle_number = 300, width = 700, height = 700, max_fps = 60, dt = 1):
        self.running = True
        self.display = None
        self.clock = None
        self.width = width
        self.height = height
        self.size = (self.width, self.height)
        self.max_fps = max_fps
        self.dt = dt

        self.interactions = interactions
        self.force_function = force_function
        self.friction = friction
        self.species = species
        self.particle_number = particle_number

        ### Informações das partículas
        self.particles = self.initiate_particles()
        

        self.interactions_matrix = self.interactions[
            self.particles["species"][:, None],
            self.particles["species"][None, :]
        ]

        self.interactions_strength = self.interactions_matrix[:, :, 0]
        self.interactions_radius = self.interactions_matrix[:, :, 1]

    def initiate_particles(self):
        particles = {}
        particles["positions"] = np.random.rand(self.particle_number, 2) * [self.width, self.height]
        particles["velocities"] = np.zeros((self.particle_number, 2))
        particles["species"] = np.random.randint(0, len(self.species), size=self.particle_number)

        return particles

    def on_init(self):
        pygame.init()
        self.display = pygame.display.set_mode(self.size)
        self.clock = pygame.time.Clock()
        return True

    def on_event(self, event):
        if event.type == pygame.QUIT:
            self.running = False

    def on_loop(self):
        #Atualiza as partículas
        diff = self.particles["positions"][None, :, :] - self.particles["positions"][:, None, :]
        dist = dist = np.linalg.norm(diff, axis=2) + 1e-5 # Soma um número muito pequeno pra não dividir por 0 depois

        np.fill_diagonal(dist, np.inf) # Evita forças com a própria partícula

        direction = diff / dist[:, :, None]

        dist /= self.interactions_radius # Normaliza a distância com base na visão

        force_strength = self.force_function(dist, self.interactions_strength)
        force_strength[dist > 1] = 0

        force = force_strength[:, :, None] * direction

        total_force = np.sum(force, axis=1)

        self.particles["velocities"] = (self.particles["velocities"] + total_force * self.dt) * (1 - self.friction)

        self.particles["positions"] += self.particles["velocities"] * self.dt
        # self.particles["positions"] %= [self.width, self.height]


    def on_render(self):
        self.display.fill((20, 20, 20))

        for i in range(len(self.particles["positions"])):
            pos = self.particles["positions"][i]
            species = self.species[self.particles["species"][i]]
            pygame.draw.circle(self.display, species.color, pos, species.size)

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


# =============================================
# FORÇA
# =============================================

def force_function(dist, attraction):

    repulsion_intensity = -0.8
    repulsion_radius = 0.3

    force = np.zeros_like(dist)

    mask1 = (dist >= 0) & (dist < repulsion_radius)
    force[mask1] = (
        dist[mask1] * (-repulsion_intensity / repulsion_radius) + repulsion_intensity
    )

    mid = repulsion_radius + ((1 - repulsion_radius) / 2)

    mask2 = (dist >= repulsion_radius) & (dist < mid)
    force[mask2] = (
        (dist[mask2] - repulsion_radius) * attraction[mask2] / (mid - repulsion_radius)
    )

    mask3 = (dist >= mid) & (dist <= 1)
    force[mask3] = (
        -(1 - dist[mask3]) * (-attraction[mask3] / (1 - mid))
    )

    return force


# =============================================
# SETUP
# =============================================
friction = 0.1

red_species = Species(0, (255, 0, 0), 4)
blue_species = Species(1, (0, 0, 255), 4)
yellow_species = Species(2, (255, 255, 0), 4)
green_species = Species(3, (0, 255, 0), 4)
purple_species = Species(4, (255, 0, 255), 4)
cyan_species = Species(5, (0, 255, 255), 4)
white_species = Species(6, (255, 255, 255), 4)

species = [
    red_species, blue_species, yellow_species,
    green_species, purple_species, cyan_species, white_species
]

interactions = np.array([

    # R         B           Y          G           P           C          W
    [(0.3,100), (-0.2,100), (0.2,100), (-0.1,100), (0.4,100), (0.0,100), (-0.3,100)],  # RED
    [(0.3,100), (0.3,100), (-0.1,100), (0.2,100), (-0.4,100), (0.1,100), (0.0,100)],   # BLUE
    [(-0.2,100), (0.3,100), (0.3,100), (-0.3,100), (0.0,100), (0.2,100), (0.1,100)],   # YELLOW
    [(0.1,100), (-0.2,100), (0.3,100), (0.3,100), (0.2,100), (-0.3,100), (0.0,100)],   # GREEN
    [(0.4,100), (0.1,100), (-0.2,100), (0.3,100), (0.3,100), (-0.1,100), (0.2,100)],   # PURPLE
    [(0.0,100), (-0.3,100), (0.2,100), (0.1,100), (0.3,100), (0.3,100), (-0.2,100)],   # CYAN
    [(-0.3,100), (0.0,100), (0.1,100), (-0.2,100), (0.2,100), (0.3,100), (0.3,100)]    # WHITE

])

game = Game(interactions, force_function, friction, species, particle_number=600, width=800, height=800)

game.on_execute()
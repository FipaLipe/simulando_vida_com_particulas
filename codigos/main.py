import pygame
import pygame_gui
import numpy as np
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONT_PATH = os.path.join(BASE_DIR, "fontes", "Monocraft.otf")
THEME_PATH = os.path.join(BASE_DIR, "codigos", "theme.json")

# =============================================
# CLASSES
# =============================================

class Species:
    def __init__(self, id, color, size=1):
        self.id = id
        self.color = color
        self.size = size


class Game:
    def __init__(self, interactions, force_function, friction, species, particle_number = 300, width = 700, height = 700, max_fps = 60): 
        self.running = True
        self.display = None
        self.clock = None
        self.delta_time = 0
        self.width = width
        self.height = height
        self.size = (self.width, self.height)
        self.center = np.array([self.width / 2, self.height / 2])
        self.max_fps = max_fps

        self.font = None
        self.font_sm = None
        self.manager = None

        self.offset = np.zeros(2)
        self.offset_controls = {pygame.K_UP: np.array([0, 1]), pygame.K_DOWN: np.array([0, -1]), pygame.K_LEFT: np.array([1, 0]), pygame.K_RIGHT: np.array([-1, 0])}
        self.zoom = 1.00

        self.interactions = interactions
        self.force_function = force_function
        self.friction = friction
        self.species = species
        self.particle_number = particle_number

        ### Informações das partículas
        self.particles = self.initiate_particles()

    def initiate_particles(self):
        particles = {}
        particles["positions"] = np.random.rand(self.particle_number, 2) * [self.width, self.height]
        particles["velocities"] = np.zeros((self.particle_number, 2))
        particles["species"] = np.random.randint(0, len(self.species), size=self.particle_number)
        

        particles["interactions_matrix"] = self.interactions[
            particles["species"][:, None],
            particles["species"][None, :]
        ]

        particles["interactions_strength"] = particles["interactions_matrix"][:, :, 0]
        particles["interactions_radius"] = particles["interactions_matrix"][:, :, 1]

        
        return particles

    def on_init(self):
        pygame.init()

        self.display = pygame.display.set_mode(self.size)
        pygame.display.set_caption("Simulando vida com partículas")

        self.clock = pygame.time.Clock()

        self.font = pygame.font.Font(FONT_PATH, size=20)
        self.font_sm = pygame.font.Font(FONT_PATH, size=14)

        self.manager = pygame_gui.UIManager(self.size, THEME_PATH)
        
        self.manager.add_font_paths("monocraft", FONT_PATH)

        restart_rect = pygame.Rect(0, 0, 80, 50)
        restart_rect.bottomright = (self.width-10, self.height -10)
        self.restart = pygame_gui.elements.UIButton(restart_rect, "Restart", self.manager)

        friction_slider_rect = pygame.Rect(0, 0, 200, 20)
        friction_slider_rect.bottomleft = (310, self.height -10)
        self.friction_slider = pygame_gui.elements.UIHorizontalSlider(friction_slider_rect, 0.1, (0, 1), self.manager)

        return True

    def on_event(self, event):
        if event.type == pygame.QUIT:
            self.running = False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r:
                self.particles = self.initiate_particles()

        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            if event.ui_element == self.restart:
                self.particles = self.initiate_particles()
        
        if event.type == pygame_gui.UI_HORIZONTAL_SLIDER_MOVED:
            if event.ui_element == self.friction_slider:
                self.friction = self.friction_slider.get_current_value()
        
        self.manager.process_events(event)
    
    def on_move_camera(self):
        keys = pygame.key.get_pressed()

        for k in self.offset_controls:
            if keys[k]:
                self.offset += self.offset_controls[k] * 30

        if keys[pygame.K_MINUS]:
            self.zoom = max(0, self.zoom - 0.05)

        if keys[pygame.K_EQUALS]:
            self.zoom = min(2, self.zoom + 0.05)
        

    def on_loop(self):
        #Atualiza as partículas
        diff = self.particles["positions"][None, :, :] - self.particles["positions"][:, None, :]
        dist = dist = np.linalg.norm(diff, axis=2) + 1e-5 # Soma um número muito pequeno pra não dividir por 0 depois

        np.fill_diagonal(dist, np.inf) # Evita forças com a própria partícula

        direction = diff / dist[:, :, None]

        dist /= self.particles["interactions_radius"] # Normaliza a distância com base na visão

        force_strength = self.force_function(dist, self.particles["interactions_strength"])
        force_strength[dist > 1] = 0

        force = force_strength[:, :, None] * direction

        total_force = np.sum(force, axis=1)

        self.particles["velocities"] = (self.particles["velocities"] + total_force) * (1 - self.friction)

        self.particles["positions"] += self.particles["velocities"]
        # self.particles["positions"] %= [self.width, self.height]


    def on_render(self):
        self.display.fill((20, 20, 20))

        for i in range(len(self.particles["positions"])):
            pos = ((self.particles["positions"][i] - self.center) * self.zoom) + self.center + self.offset * self.zoom
            species = self.species[self.particles["species"][i]]
            pygame.draw.circle(self.display, species.color, pos, max(1,species.size * self.zoom))

        controls_text = self.font.render("Move: ←↑→↓\nZoom in/out: +/-\nRestart Simulation: R", False, (240, 240, 240), (20, 20, 20))
        controls_text_rect = controls_text.get_rect()
        controls_text_rect.bottomleft = (10, self.height - 10)
        self.display.blit(controls_text, controls_text_rect)

        friction_text = self.font_sm.render(f"Friction: {self.friction:.2f}", False, (240, 240, 240), (20, 20, 20))
        friction_text_rect = friction_text.get_rect()
        friction_text_rect.bottomleft = (314, self.height - 34)
        self.display.blit(friction_text, friction_text_rect)

        self.manager.draw_ui(self.display)

        pygame.display.flip()

    def on_cleanup(self):
        pygame.quit()

    def on_execute(self):
        self.running = self.on_init()

        while self.running:
            for event in pygame.event.get():
                self.on_event(event)

            self.manager.update(self.delta_time)

            self.on_move_camera()

            self.on_loop()
            self.on_render()

            self.delta_time = self.clock.tick(self.max_fps)/1000.0

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
friction = 0.2

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
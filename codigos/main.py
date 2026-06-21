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
    """Classe base para o jogo
    
    Atributos:
        running (bool): Indica se o jogo está rodando
        display (pygame.Surface): A superfície de exibição do jogo
        clock (pygame.time.Clock): Relógio para controlar o FPS
        width (int): Largura da janela do jogo
        height (int): Altura da janela do jogo
        size (tuple): Tamanho da janela do jogo (width, height)
        max_fps (int): Taxa máxima de quadros por segundo
        interactions (numpy.ndarray): Matriz de interações entre as espécies de partículas
        force_function (callable): Função para calcular a força de atração ou repulsão entre as partículas
        friction (float): Coeficiente de fricção a ser aplicado à velocidade da partícula
        species (list): Lista de espécies de partículas no jogo
        particle_number (int): Número de partículas a ser instanciado no jogo
        particles (dict): Dicionário contendo as informações das partículas, incluindo posições, velocidades e espécies
        interactions_matrix (numpy.ndarray): Matriz de interações entre as partículas, calculada com base na matriz de interações e nas espécies das partículas
        interactions_strength (numpy.ndarray): Matriz contendo a força de atração ou repulsão entre as partículas, extraída da matriz de interações
        interactions_radius (numpy.ndarray): Matriz contendo o raio de visão para as interações entre as partículas, extraída da matriz de interações
    
    Métodos:
        __init__(self, width=700, height=700, max_fps=60): Inicializa os atributos do jogo
        on_init(self): Configura o ambiente do jogo
        on_add_particle(self, particle): Adiciona uma partícula à lista de partículas do jogo
        on_event(self, event): Lida com os eventos do jogo
        on_loop(self): Atualiza a lógica do jogo
        on_render(self): Renderiza os elementos do jogo na tela
        on_cleanup(self): Limpa os recursos do jogo
        on_execute(self): Executa o loop principal do jogo
    """

    def __init__(self, interactions, force_function, friction, species, particle_number = 300, width = 700, height = 700, max_fps = 60): 
        """Inicializa os atributos do jogo.

        Inicializa os atributos do jogo, incluindo as interações, a função de força, o coeficiente de fricção, a largura e altura da janela, a taxa máxima de quadros por segundo, e as variáveis para controlar o estado do jogo e a exibição.

        Args:
            interactions (numpy.ndarray): A matriz de interações entre as espécies de partículas.
            force_function (callable): A função para calcular a força de atração ou repulsão entre as partículas.
            friction (float): O coeficiente de fricção a ser aplicado à velocidade da partícula.
            species (list): A lista de espécies de partículas no jogo.
            particle_number (int, optional): O número de partículas a ser instanciado no jogo. Padrão é 300.
            width (int, optional): Largura da janela do jogo. Padrão é 700.
            height (int, optional): Altura da janela do jogo. Padrão é 700.
            max_fps (int, optional): Taxa máxima de quadros por segundo. Padrão é 60.
        """
        self.running = True
        self.display = None
        self.clock = None
        self.width = width
        self.height = height
        self.size = (self.width, self.height)
        self.max_fps = max_fps

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
        """Inicializa as partículas do jogo.
        
        Inicializa as partículas do jogo, gerando posições aleatórias dentro dos limites da janela, velocidades iniciais zeradas e atribuindo espécies aleatórias com base na lista de espécies disponível.
        
        Returns:
            dict: Um dicionário contendo as informações das partículas, incluindo posições, velocidades e espécies.
        """
        particles = {}
        particles["positions"] = np.random.rand(self.particle_number, 2) * [self.width, self.height]
        particles["velocities"] = np.zeros((self.particle_number, 2))
        particles["species"] = np.random.randint(0, len(self.species), size=self.particle_number)

        return particles

    def on_init(self):
        """Configura o ambiente do jogo.

        Configura o ambiente do jogo, inicializando o Pygame, criando a janela de exibição e configurando o relógio para controlar o FPS.

        Returns:
            bool: Retorna True se a inicialização for bem-sucedida, caso contrário, retorna False.
        """
        pygame.init()
        self.display = pygame.display.set_mode(self.size)
        self.clock = pygame.time.Clock()
        return True

    def on_event(self, event):
        """Lida com os eventos do jogo.
        
        Lida com os eventos do jogo, verificando se o evento é do tipo QUIT para encerrar o jogo.
        
        Args:
            event (pygame.event.Event): O evento a ser processado.
        """
        if event.type == pygame.QUIT:
            self.running = False

    def on_loop(self):
        """Atualiza a lógica do jogo.
        
        Atualiza os elementos do jogo, como a posição dos objetos, e cálculos de interações. Este método é chamado a cada iteração do loop principal do jogo.
        """

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

        self.particles["velocities"] = (self.particles["velocities"] + total_force) * (1 - self.friction)

        self.particles["positions"] += self.particles["velocities"]
        # self.particles["positions"] %= [self.width, self.height]


    def on_render(self):
        """Renderiza os elementos do jogo na tela.
        
        Renderiza os elementos do jogo na tela, desenhando os objetos e atualizando a exibição. Este método é chamado a cada iteração do loop principal do jogo.
        """
        self.display.fill((20, 20, 20))

        for i in range(len(self.particles["positions"])):
            pos = self.particles["positions"][i]
            species = self.species[self.particles["species"][i]]
            pygame.draw.circle(self.display, species.color, pos, species.size)

        pygame.display.flip()

    def on_cleanup(self):
        """Limpa os recursos do jogo.
        
        Limpa os recursos do jogo, encerrando o Pygame e liberando quaisquer recursos alocados. Este método é chamado quando o jogo é encerrado.
        """
        pygame.quit()

    def on_execute(self):
        """Executa o loop principal do jogo.
        
        Executa o loop principal do jogo, chamando os métodos de inicialização, eventos, lógica e renderização em cada iteração. O loop continua até que a variável 'running' seja definida como False.
        """
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
friction = 0.2

red_species = Species(0, (255, 0, 0), 2)
blue_species = Species(1, (0, 0, 255), 2)
yellow_species = Species(2, (255, 255, 0), 2)
green_species = Species(3, (0, 255, 0), 2)
purple_species = Species(4, (255, 0, 255), 2)
cyan_species = Species(5, (0, 255, 255), 2)
white_species = Species(6, (255, 255, 255), 2)

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

game = Game(interactions, force_function, friction, species, particle_number=800, width=800, height=800)

game.on_execute()
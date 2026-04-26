import pygame
import random
import math

pygame.init()

width = 1280
height = 720
screen = pygame.display.set_mode((width, height))
clock = pygame.time.Clock()

running = True

repulsao_borda = 1
atrito = 0.98
dt = 1

tipos = [
    {
        'cor': (255, 0, 0),
        'tamanho': 6,
        'interacoes': [
            {
                'f1': -0.1,
                'f2': 0.02,
                'r1': 40,
                'r2': 100
            }
        ]
    }
]

particulas = []


def cria_particulas(n):
    for i in range(n):
        nova_particula = {}

        nova_particula['id'] = len(particulas)

        nova_particula['tipo'] = 0

        nova_particula['x'] = random.randint(0, width)
        nova_particula['y'] = random.randint(0, height)

        nova_particula['vel_x'] = 0
        nova_particula['vel_y'] = 0

        particulas.append(nova_particula)


cria_particulas(100)


def calcula_forca(dist, r1, r2, f1, f2):

    if 0 < dist <= r1:
        return (dist * abs(f2 - f1) / r1) - abs(f1)

    if r1 < dist < r2:
        return f2 * abs(r2 - dist) / abs(r2 - r1)

    return 0


font = pygame.font.Font(pygame.font.get_default_font(), 24)

while running:
    primeiro = True

    events = pygame.event.get()

    for event in events:
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                particulas = []
                cria_particulas(300)

    screen.fill((20, 15, 15))

    for particula in particulas:
        tipo = tipos[particula['tipo']]

        cor = tipo['cor']
        tamanho = tipo['tamanho']

        x = particula['x']
        y = particula['y']

        pos = (x, y)

        delta_vel_x = 0
        delta_vel_y = 0

        forca = 0
        forca_x = 0
        forca_y = 0

        for particula_2 in particulas:
            if particula['id'] == particula_2['id']:
                continue

            tipo_2 = particula_2['tipo']
            interacoes = tipo['interacoes'][tipo_2]

            f1, f2, r1, r2 = [interacoes[x]
                              for x in ['f1', 'f2', 'r1', 'r2']]

            x_2 = particula_2['x']
            y_2 = particula_2['y']

            diff_x = x_2 - x
            diff_y = y_2 - y

            distancia = math.sqrt(diff_x ** 2 + diff_y ** 2)

            forca = calcula_forca(distancia, r1, r2, f1, f2)

            forca_x += forca * diff_x / distancia
            forca_y += forca * diff_y / distancia

        delta_vel_x = forca_x * dt
        delta_vel_y = forca_y * dt

        if x <= 0:
            delta_vel_x += repulsao_borda

        if x >= width:
            delta_vel_x -= repulsao_borda

        if y <= 0:
            delta_vel_y += repulsao_borda

        if y >= height:
            delta_vel_y -= repulsao_borda

        particula['vel_x'] += delta_vel_x
        particula['vel_y'] += delta_vel_y

        particula['x'] += particula['vel_x'] * dt
        particula['y'] += particula['vel_y'] * dt

        if primeiro:
            cor = (0, 255, 0)
            pygame.draw.circle(screen, (80, 30, 30), pos, r1, 1)
            pygame.draw.circle(screen, (80, 80, 80), pos, r2, 1)
            pygame.draw.line(screen, (0, 255, 0), (particula['x'], particula['y']), (
                particula['x'] + particula['vel_x'], particula['y'] + particula['vel_y']))
            # print(f"Vel X: {particula['vel_x']} | Vel Y: {particula['vel_y']}")

            primeiro = False

        # pygame.draw.circle(screen, (80, 30, 30), pos, r1, 1)
        # pygame.draw.circle(screen, (80, 80, 80), pos, r2, 1)
        pygame.draw.circle(screen, cor, pos, tamanho)

        particula['vel_x'] *= atrito
        if abs(particula['vel_x']) < 0.1:
            particula['vel_x'] = 0

        particula['vel_y'] *= atrito
        if abs(particula['vel_y']) < 0.1:
            particula['vel_y'] = 0

    fps = clock.get_fps()
    text_fps = font.render(
        f"FPS: {fps}", False, (255, 255, 255))
    text_fps_rect = text_fps.get_rect()
    text_fps_rect.topleft = (10, 10)
    screen.blit(text_fps, text_fps_rect)

    pygame.display.flip()

    clock.tick(60)

pygame.quit()

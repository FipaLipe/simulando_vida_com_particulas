import pygame
import random
import math

pygame.init()

width = 1280
height = 720
screen = pygame.display.set_mode((width, height))
clock = pygame.time.Clock()

running = True

tipos = [
    {
        'cor': (255, 0, 0),
        'tamanho': 6
    }
]

particulas = []

# Constantes

RADIUS = 60
ALFA = math.radians(180)
BETA = math.radians(17)
VELOCITY = 10

dt = 1

for i in range(300):
    nova_particula = {}

    nova_particula['tipo'] = 0

    nova_particula['x'] = random.randint(0, width)
    nova_particula['y'] = random.randint(0, height)

    nova_particula['direcao'] = math.radians(random.randint(0, 360))

    particulas.append(nova_particula)

while running:
    primeiro = True

    events = pygame.event.get()

    for event in events:
        if event.type == pygame.QUIT:
            running = False

    screen.fill((20, 15, 15))

    for particula in particulas:
        tipo = tipos[particula['tipo']]

        cor = tipo['cor']
        tamanho = tipo['tamanho']

        x = particula['x']
        y = particula['y']
        direcao = particula['direcao'] % (math.pi * 2)

        pos = (x, y)
        vel = (math.cos(direcao) * VELOCITY, math.sin(direcao) * VELOCITY)

        L = 0
        R = 0

        for particula_2 in particulas:
            x_2 = particula_2['x']
            y_2 = particula_2['y']
            pos_2 = (x_2, y_2)

            dx = x_2 - x
            dy = y_2 - y

            distancia = math.sqrt(dx ** 2 + dy ** 2)

            if distancia < RADIUS and distancia != 0:
                angulo = math.atan2(dy, dx) + math.pi

                if 0 < angulo - direcao < math.pi:
                    L += 1
                else:
                    R += 1

        N = L + R

        RL_Sign = (R-L) / abs(R - L) if abs(R - L) != 0 else 0

        delta_phi = ALFA + BETA * N * RL_Sign

        particula['direcao'] += delta_phi

        vel = (math.cos(direcao) * VELOCITY, math.sin(direcao) * VELOCITY)

        particula['x'] += vel[0]
        particula['y'] += vel[1]

        if primeiro:
            pygame.draw.circle(screen, (40, 40, 40), pos, RADIUS)
            pygame.draw.line(screen, (0, 255, 0), pos,
                             (pos[0] + vel[0] * 20, pos[1] + vel[1] * 20))

            L = 0
            R = 0

            for particula_2 in particulas:
                x_2 = particula_2['x']
                y_2 = particula_2['y']
                pos_2 = (x_2, y_2)

                dx = x_2 - x
                dy = y_2 - y

                distancia = math.sqrt(dx ** 2 + dy ** 2)

                if distancia < RADIUS:
                    angulo = math.atan2(dy, dx) + math.pi

                    # print(angulo, direcao)

                    if 0 < angulo - direcao < math.pi:
                        pygame.draw.circle(
                            screen, (0, 255, 255), pos_2, tamanho+2)
                    else:
                        pygame.draw.circle(
                            screen, (0, 0, 255), pos_2, tamanho+2)

            cor = (0, 255, 0)

            primeiro = False

        pygame.draw.circle(screen, cor, pos, tamanho)

    pygame.display.flip()

    dt = clock.tick(6000)

pygame.quit()

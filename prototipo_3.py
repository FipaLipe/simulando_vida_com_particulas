import pygame
import random
import math

pygame.init()

width = 500
height = 500
screen = pygame.display.set_mode((width, height))
clock = pygame.time.Clock()

running = True

repulsao_borda = 1
atrito = 0.5
dt = 1

# tipos = [
#     {
#         'cor': (210, 0, 0),
#         'tamanho': 1,
#         'interacoes': [
#             0.4, 0.1, 0.2
#         ]
#     },
#     {
#         'cor': (0, 0, 210),
#         'tamanho': 1,
#         'interacoes': [
#             -0.5, 0.2, 0.5
#         ]
#     },
#     {
#         'cor': (210, 210, 0),
#         'tamanho': 1,
#         'interacoes': [
#             0.2, 0.3, 0.5
#         ]
#     }
# ]

tipos = [
    {
        'cor': (210, 0, 0),
        'tamanho': 2,
        'interacoes': [
            0.4,
        ]
    }
]

fator_de_escala = 50
width_grade = math.floor(width / fator_de_escala)
height_grade = math.floor(height / fator_de_escala)

particulas = []


def grade_vazia():
    n_grade = []
    for i in range(height_grade + 1):
        linha = []
        for j in range(width_grade + 1):
            linha.append([])
        n_grade.append(linha)

    return n_grade


def cria_particulas(n):
    for i in range(n):
        nova_particula = {}

        nova_particula['id'] = i

        nova_particula['tipo'] = random.randint(0, len(tipos)-1)

        nova_particula['x'] = random.randint(0, width)
        nova_particula['y'] = random.randint(0, height)

        nova_particula['vel_x'] = 0
        nova_particula['vel_y'] = 0

        particulas.append(nova_particula)


def atualiza_grade():
    n_grade = grade_vazia()
    for particula in particulas:
        idx = max(
            0, min(width_grade-1, math.floor(particula['x']/fator_de_escala)))
        idy = max(
            0, min(height_grade-1, math.floor(particula['y']/fator_de_escala)))
        n_grade[idy][idx].append(particula['id'])
    return n_grade


n_particulas = 800

cria_particulas(n_particulas)

grade = atualiza_grade()


def calcula_forca(dist, atracao, raio):

    if 0 < dist <= raio:
        return (dist / raio) - 1

    if raio < dist < 1:
        return atracao * (1 - abs(2*dist - 1 - raio) / (1 - raio))

    return 0


beta = 0.3
visao = 40

passo = math.floor((visao / fator_de_escala) * 2)

font = pygame.font.Font(pygame.font.get_default_font(), 24)

mouse_down = False
last_pos = (None, None)
drag = (0, 0)

while running:
    primeiro = True

    events = pygame.event.get()

    for event in events:
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                particulas = []
                cria_particulas(n_particulas)
                grade = atualiza_grade()

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_down = True

        if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            mouse_down = False
            last_pos = (None, None)

        if event.type == pygame.MOUSEMOTION and mouse_down:
            if last_pos == (None, None):
                last_pos = event.pos

            drag = (event.pos[0] - last_pos[0], event.pos[1] - last_pos[1])

            last_pos = event.pos

            for p_id in grade[min(height_grade, max(0, math.floor(event.pos[1] / fator_de_escala)))][min(width_grade, max(0, math.floor(event.pos[0] / fator_de_escala)))]:
                particula = particulas[p_id]
                particula['vel_x'] += drag[0] * dt * 0.1
                particula['vel_y'] += drag[1] * dt * 0.1

    screen.fill((20, 15, 15))

    # for i in range(width_grade+1):
    #     pygame.draw.line(screen, (30, 30, 30),
    #                      (i * fator_de_escala, 0), (i * fator_de_escala, height))

    # for j in range(height_grade+1):
    #     pygame.draw.line(screen, (30, 30, 30), (0, j *
    #                      fator_de_escala), (width, j * fator_de_escala))

    for i, linha in enumerate(grade):
        for j, coluna in enumerate(linha):
            for particula_id in coluna:
                particula = particulas[particula_id]

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

                for linha_2 in range(max(0, i-passo), min(height_grade, i+passo)+1):
                    for coluna_2 in range(max(0, j-passo), min(width_grade, j+passo)+1):
                        for particula_id_2 in grade[linha_2][coluna_2]:
                            if particula_id == particula_id_2:
                                continue

                            particula_2 = particulas[particula_id_2]

                            tipo_2 = particula_2['tipo']
                            atracao = tipo['interacoes'][tipo_2]

                            x_2 = particula_2['x']
                            y_2 = particula_2['y']

                            diff_x = x_2 - x
                            diff_y = y_2 - y

                            if abs(diff_x) > visao or abs(diff_y) > visao:
                                continue

                            distancia = math.sqrt(diff_x ** 2 + diff_y ** 2)

                            if distancia <= 0:
                                continue

                            # pygame.draw.line(
                            #     screen, (20, 40, 20), (particula['x'], particula['y']), (particula_2['x'], particula_2['y']))

                            distancia /= visao

                            forca = calcula_forca(
                                distancia, atracao, beta) / 100

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

                # if primeiro:
                #     cor = (0, 255, 0)
                #     pygame.draw.circle(screen, (80, 30, 30), pos, visao * beta, 1)
                #     pygame.draw.circle(screen, (80, 80, 80), pos, visao, 1)
                #     pygame.draw.line(screen, (0, 255, 0), (particula['x'], particula['y']), (
                #         particula['x'] + particula['vel_x'], particula['y'] + particula['vel_y']))
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

    grade = atualiza_grade()

    fps = clock.get_fps()
    text_fps = font.render(
        f"FPS: {round(fps, 2)}", False, (255, 255, 255))
    text_fps_rect = text_fps.get_rect()
    text_fps_rect.topleft = (10, 10)
    screen.blit(text_fps, text_fps_rect)

    pygame.display.flip()

    clock.tick(60)

pygame.quit()

import pygame
import sys
from enemigo import EnemigoCaminante, EnemigoConAtaque 
from jugador import Jugador

# juegoKodland.py

# Inicialización de PyGame
pygame.init()

# Dimensiones de la pantalla
ANCHO_PANTALLA = 800
ALTO_PANTALLA = 600

pantalla = pygame.display.set_mode((ANCHO_PANTALLA, ALTO_PANTALLA))
pygame.display.set_caption("Escuadrón de proyectiles")

reloj = pygame.time.Clock()
FPS = 60

# Creamos superficies para los sprites
def crear_sprite(color, ancho=50, alto=50):
    surf = pygame.Surface((ancho, alto))
    surf.fill(color)
    return surf

# Diccionario de sprites para el jugador
sprites_jugador = {
    "idle": [crear_sprite((0, 255, 0))],
    "corre": [crear_sprite((0, 200, 0))],
    "salto": [crear_sprite((100, 255, 100))],
    "muerte": [crear_sprite((0, 100, 0))]
}

# Diccionario de sprites para enemigos
sprites_enemigo1 = {
    "idle": [crear_sprite((255, 0, 0))],
    "caminar": [crear_sprite((200, 0, 0))],
    "atacar": [crear_sprite((255, 100, 100))],
    "muerto": [crear_sprite((100, 0, 0))]
}

sprites_enemigo2 = {
    "idle": [crear_sprite((0, 0, 255))],
    "caminar": [crear_sprite((0, 0, 200))],
    "atacar": [crear_sprite((100, 100, 255))],
    "muerto": [crear_sprite((0, 0, 100))]
}

# Crear instancias
jugador = Jugador(0,0,sprites_jugador, ANCHO_PANTALLA, ALTO_PANTALLA, vida=10)
# Crear enemigos con sus respectivos sprites
enemigo1 = EnemigoCaminante(100, ALTO_PANTALLA - 100, sprites_enemigo1, ANCHO_PANTALLA, ALTO_PANTALLA, danoBase=1, vida=5)
enemigo2 = EnemigoConAtaque(600, ALTO_PANTALLA - 100, sprites_enemigo2, ANCHO_PANTALLA, ALTO_PANTALLA, danoBase=2, vida=8)

# Asignar suelo para enemigos (en este caso suelo fijo a una altura)
enemigo1.sueloActual = ALTO_PANTALLA - enemigo1.dimAlto
enemigo2.sueloActual = ALTO_PANTALLA - enemigo2.dimAlto

# Bucle principal
while True:
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    # Actualizar estado de enemigos
    enemigo1.mover()
    enemigo1.avanzarAnimacion()
    enemigo1.actualizarProyectiles(jugador, ANCHO_PANTALLA)

    enemigo2.mover()
    enemigo2.avanzarAnimacion()
    enemigo2.actualizarProyectiles(jugador, ANCHO_PANTALLA)


    # Limpiar pantalla
    pantalla.fill((30, 30, 30))

    # Dibujar enemigos y sus proyectiles
    enemigo1.visualizarAnimacion(pantalla)
    enemigo1.dibujarProyectiles(pantalla)

    enemigo2.visualizarAnimacion(pantalla)
    enemigo2.dibujarProyectiles(pantalla)

    # Dibujar jugador
    jugador.mover()
    jugador.visualizarAnimacion(pantalla)
    jugador.avanzarAnimacion()
    jugador.dibujarProyectiles(pantalla)

    pygame.display.flip()
    reloj.tick(FPS)

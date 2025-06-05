import pygame

class Jugador:
    """Representa el avatar del jugador"""
    
    def __init__(
            self, 
            posX, 
            posY,
            spritesDict,
            anchoPantalla,
            altoPantalla,
            vida = 7,
            ):
        """
        Constructor de la clase jugador.
        
        :param posX: Posición inicial en el eje X (en píxeles).
        :param posY: Posición inicial en el eje Y (en píxeles).
        :param spritesDict: Diccionario con listas de Surfaces para cada animación.
            Ejemplo:
            {
                "idle": [img_idle1, img_idle2, ...],
                "corre": [img_c1, img_c2, ...],
                "salto": [img_s1, img_s2, ...],
                "muerte": [img_m1, img_m2, ...]
            }
        :param anchoPantalla: Ancho de la pantalla del juego (en píxeles).
        :param altoPantalla: Alto de la pantalla del juego (en píxeles).
        :param vida: Entero de puntos de vida inicial (por defecto 7).
        """
        # Inicialización de la posición y velocidad del jugador
        self.posX = float(posX)
        self.posY = float(posY)
        self.velX = 0.0
        self.velY = 0.0

        # Parámetros para definir el movimiento y actualización de la posición del jugador
        self.velBaseX = 2.0 # Velocidad base de movimiento horizontal
        self.impulsoY = 2.0 # Impulso vertical al saltar
        self.gravedad = 0.2 # Gravedad aplicada al jugador

        # Sprites y dimensiones (se asume que todos los frames tienen el mismo tamaño)
        self.sprites = spritesDict
        primerSprite = self.sprites["idle"][0]
        self.dimAncho = primerSprite.get_width()
        self.dimAlto  = primerSprite.get_height()


        # Rectángulo de colisión, basado en posición y dimensiones
        self.rect = pygame.Rect(int(self.posX), int(self.posY), self.dimAncho, self.dimAlto)

        # Estado de animación y frame actual
        self.estadoAnimacion = "idle"     # Por defecto el jugador esta quieto
        self.frameActual     = 0

        # Vida
        self.vida = vida
        self.jugadorVivo = True

        # Salto/colisiones
        self.enSuelo = True  # Indica si el jugador está en el suelo
        self.sueloActual = self.posY + self.dimAlto # Posición del suelo actual (para colisiones)


        # Control de animación
        self.contadorFrames = 0          # Para saber cuándo avanzar frameActual
        self.delayAnimacion = 5          # Avanza cada 5 ticks de reloj

        # Inicialización de parámetros para el ataque del jugador
        self.proyectiles = [] # Lista de proyectiles disparados por el jugador
        self.cooldownDisparo = 0 # Tiempo de espera entre disparos
        self.direccion = "derecha" # Dirección del último movimiento del jugador

        # Dimensiones de la pantalla
        self.anchoPantalla = anchoPantalla
        self.altoPantalla = altoPantalla

    def posicionJugadorMuerto(self):
        """
        Método auxiliar: si el jugador está muerto, lo
        coloca en el centro de la pantalla y ajusta su rect.
        """
        # Detener cualquier velocidad
        self.velX = 0.0
        self.velY = 0.0
        # Calcular posición central
        self.posX = (self.anchoPantalla  // 2) - (self.dimAncho // 2)
        self.posY = (self.altoPantalla   // 2) - (self.dimAlto  // 2)
        # Actualizar rect para colisiones y dibujo
        self.rect.topleft = (int(self.posX), int(self.posY))

    def procesarTeclado(self):
        teclaSeleccionada = pygame.key.get_pressed()

        # Movimiento horizontal
        if teclaSeleccionada[pygame.K_LEFT]:
            self.estadoAnimacion = "corre"
            self.velX = -self.velBaseX
            self.direccion = "izquierda"
        elif teclaSeleccionada[pygame.K_RIGHT]:
            self.estadoAnimacion = "corre"
            self.velX = self.velBaseX
            self.direccion = "derecha"
        else:
            self.velX = 0
            self.estadoAnimacion = "idle"

        # Ataque con disparo
        # Si se presiona la tecla Z y el cooldown de disparo es 0, dispara
        if teclaSeleccionada[pygame.K_z] and self.cooldownDisparo <= 0:
            self.disparar()

        # Movimiento vertical (salto)
        if teclaSeleccionada[pygame.K_UP] and self.enSuelo:
            self.estadoAnimacion = "salto"
            self.velY = -self.impulsoY
            self.enSuelo = False
            self.sueloActual = self.posY + self.dimAlto
        



    def disparar(self):
        """
        Crea un nuevo proyectil y lo agrega a self.proyectiles.
        Solo dispara si self.cooldownDisparo <= 0.
        """
        # Verificar enfriamiento
        if self.cooldownDisparo <= 0 and self.jugadorVivo:
            # Posición inicial del proyectil:
            # Si el jugador mira a la derecha, sale justo al borde derecho del sprite.
            # Si mira a la izquierda, sale al borde izquierdo.
            if self.direccion == "derecha":
                px = self.posX + self.dimAncho
                vel = 10      # velocidad positiva (derecha)
            else:  # "izquierda"
                px = self.posX - 10  # sale ligeramente a la izquierda del sprite
                vel = -10     # velocidad negativa (izquierda)

            # Altura media del jugador para centrar el disparo verticalmente
            py = self.posY + (self.dimAlto // 2)

            # Crear diccionario que represente el proyectil
            nuevoProyectil = {
                "x": float(px),
                "y": float(py),
                "vel": float(vel),
                "ancho": 2,    # ancho del proyectil en píxeles
                "alto": 2,      # alto del proyectil en píxeles
                "activo": True
            }

            # Agregar a la lista de proyectiles del jugador
            self.proyectiles.append(nuevoProyectil)

            # Reiniciar enfriamiento
            self.cooldownDisparo = 20
    
    def actualizarProyectiles(self, listaEnemigos, anchoPantalla):
        """
        Mueve cada proyectil, comprueba colisiones con enemigos,
        y elimina los proyectiles que ya no estén activos.
        
        :param listaEnemigos: lista de instancias Enemigo (deben tener atributo .rect y método recibirDano).
        :param anchoPantalla: ancho de la ventana, para descartar proyectiles que salgan de pantalla.
        """
        proyectiles_activos = []
        for p in self.proyectiles:
            # Mover el proyectil
            p["x"] += p["vel"]
            
            # Crear rect de colisión para el proyectil
            rect_p = pygame.Rect(int(p["x"]), int(p["y"]), p["ancho"], p["alto"])
            
            # Comprobar colisión con enemigos
            for enemigo in listaEnemigos:
                if enemigo.vivo and rect_p.colliderect(enemigo.rect):
                    enemigo.recibirDano(1)
                    p["activo"] = False
                    break
            
            if not p["activo"]:
                continue
            
            # Comprobar si salió de pantalla
            if p["x"] < 0 or p["x"] > anchoPantalla:
                p["activo"] = False
                continue
            
            # Si sigue activo, lo conservamos para la siguiente iteración
            proyectiles_activos.append(p)
        
        # Reemplazar self.proyectiles con los que siguen activos
        self.proyectiles = proyectiles_activos
        
        # Reducir el cooldown de disparo si está en curso
        if self.cooldownDisparo > 0:
            self.cooldownDisparo -= 1

    def dibujarProyectiles(self, pantalla):
        """
        Dibuja cada proyectil activo en pantalla.
        
        :param pantalla: superficie de PyGame donde se dibuja el escenario del juego.
        """
        for p in self.proyectiles:
            rect_dibujo = pygame.Rect(int(p["x"]), int(p["y"]), p["ancho"], p["alto"])
            pygame.draw.rect(pantalla, (255, 255, 0), rect_dibujo)


    def aplicarFisicaAlMovimiento(self):
        # Gravedad
        self.velY += self.gravedad

        # Actualizar posición
        self.posX += self.velX
        self.posY += self.velY

        # Colisión con suelo
        if self.posY + self.dimAlto >= self.sueloActual:
            self.posY = self.sueloActual - self.dimAlto
            self.velY = 0
            self.enSuelo = True

        # Bordes de pantalla
        if self.posX < 0:
            self.posX = 0
        elif self.posX + self.dimAncho > self.anchoPantalla:
            self.posX = self.anchoPantalla - self.dimAncho

        # Sincronizar rect
        self.rect.topleft = (self.posX, self.posY)

    def mover(self):
        if self.jugadorVivo:
            self.procesarTeclado()
            self.aplicarFisicaAlMovimiento()
    
    def recibirDano(self, danoRecibido):
        """
        Método para recibir daño. Reduce la vida del jugador.
        Si la vida llega a 0, el jugador muere.
        """
        self.vida -= danoRecibido
        # Verificar si el jugador ha muerto
        if self.vida <= 0:
            self.morir()

    def morir(self):
        """
        Método para manejar la muerte del jugador.
        Coloca al jugador en el centro de la pantalla y detiene su movimiento.
        """
        self.jugadorVivo = False
        self.estadoAnimacion = "muerto"
        self.posicionJugadorMuerto()
    
    def avanzarAnimacion(self):
        """
        Actualiza el frame actual de la animación según el estado del jugador.
        """
        if self.jugadorVivo:
            # Avanzar frame si corresponde
            self.contadorFrames += 1
            if self.contadorFrames >= self.delayAnimacion:
                self.contadorFrames = 0
                # Cambiar al siguiente frame de la animación actual
                self.frameActual += 1
                # Si se ha llegado al final de los frames, reiniciar
                if self.frameActual >= len(self.sprites[self.estadoAnimacion]):
                    self.frameActual = 0

    def visualizarAnimacion(self, pantalla):
        """
        Dibuja el frame actual de la animación en pantalla, en la posición del jugador.
        """
        sprite = self.sprites[self.estadoAnimacion][self.frameActual]
        pantalla.blit(sprite, (int(self.posX), int(self.posY)))
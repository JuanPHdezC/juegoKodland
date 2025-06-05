import pygame

class Enemigo:
    """Representa el avatar del enemigo en el juego."""
    
    def __init__(
            self, 
            posX, 
            posY,
            spritesDict,
            anchoPantalla,
            altoPantalla,
            danoBase,
            vida = 3,
            ):
        """
        Constructor de la clase Enemigo.
        
        :param posX: Posición inicial en el eje X (en píxeles).
        :param posY: Posición inicial en el eje Y (en píxeles).
        :param spritesDict: Diccionario con listas de Surfaces para cada animación.
            Ejemplo:
            {
                "idle": [img_idle1, img_idle2, ...],
                "caminar": [img_c1, img_c2, ...],
                "atacar": [img_a1, img_a2, ...],
                "muerto": [img_m1, img_m2, ...]
            }
        :param anchoPantalla: Ancho de la pantalla del juego (en píxeles).
        :param altoPantalla: Alto de la pantalla del juego (en píxeles).
        :param danoBase: Entero de daño base que el enemigo puede infligir.
        :param vida: Entero de puntos de vida inicial (por defecto 3).
        """
        # Inicialización de la posición y velocidad del enemigo
        self.posX = float(posX)
        self.posY = float(posY)
        self.velX = 0.0
        self.velY = 0.0

        # Inicialización parámetros físicos del enemigo        
        self.velBaseX    = 2.0   # Velocidad horizontal base
        self.impulsoY     = 1.0   # Impulso vertical al saltar
        self.gravedad     = 0.5   # Aceleración hacia abajo        

        

        # Sprites y dimensiones (se asume que todos los frames tienen el mismo tamaño)
        self.sprites = spritesDict
        primerSprite = self.sprites["idle"][0]
        self.dimAncho = primerSprite.get_width()
        self.dimAlto  = primerSprite.get_height()


        # Rectángulo de colisión, basado en posición y dimensiones
        self.rect = pygame.Rect(int(self.posX), int(self.posY), self.dimAncho, self.dimAlto)

        # Estado de animación y frame actual
        self.frameActual = 0
        self.estadoAnimacion = "idle"


        # Vida y daño
        self.vida = vida
        self.enemigoVivo = True
        self.danoBase = danoBase

        # Salto/colisiones
        self.enSuelo = True  # Indica si el enemigo está en el suelo
        self.sueloActual = self.posY + self.dimAlto # Posición del suelo actual (para colisiones)


        # Control de animación
        self.contadorFrames = 0          # Para saber cuándo avanzar frameActual
        self.delayAnimacion = 5          # Avanza cada 5 ticks de reloj

        # Inicialización de parámetros para el ataque del enemigo
        self.proyectiles = [] # Lista de proyectiles disparados por el enemigo
        self.cooldownDisparo = 0 # Tiempo de espera entre disparos
        self.direccion = "derecha" # Dirección del último movimiento del enemigo

        # Dimensiones de la pantalla
        self.anchoPantalla = anchoPantalla
        self.altoPantalla = altoPantalla

    def enemigoMuerto(self):
        """
        Método auxiliar: si el enemigo está muerto actualiza su estadoAnimación, 
        modifica su valor booleano en enemigoVivo, ajusta su rect y coloca en 0 sus parámetros de velocidad.
        """
        # Detener cualquier velocidad
        self.enemigoVivo = False
        self.estadoAnimacion = "muerto"
        self.reinicioAnimacion()
        self.velX = 0.0
        self.velY = 0.0
        # Actualizar rect para colisiones y dibujo
        self.rect.topleft = (int(self.posX), int(self.posY))

    def decidir_movimiento(self):
        """
        Este método se sobrescribe en cada subclase para 
        asignar self.velX y self.velY.
        """
        pass

    def mover(self):
        """Aplica gravedad, actualiza posX/Y según velX/velY y colisión con suelo dinámico."""
        if self.enemigoVivo:

            self.decidir_movimiento()

            # Aplicar gravedad en Y
            self.velY += self.gravedad

            # Actualizar posiciones
            self.posX += self.velX
            self.posY += self.velY

            if self.velX > 0:
                self.direccion = "derecha"
            elif self.velX < 0:
                self.direccion = "izquierda"


            # Colisión con suelo dinámico
            if self.posY + self.dimAlto >= self.sueloActual:
                
                self.posY = self.sueloActual - self.dimAlto
                self.velY = 0.0
                self.enSuelo = True

            # Limitar dentro de la pantalla horizontalmente
            if self.posX < 0:
                self.posX = 0
            elif self.posX + self.dimAncho > self.anchoPantalla:
                self.posX = self.anchoPantalla - self.dimAncho

            # Actualizar rect
            self.rect.x = int(self.posX)
            self.rect.y = int(self.posY)
    
    def atacar(self, jugador):
        """
        Método para atacar al jugador. Reduce la vida del jugador.
        :param jugador: Instancia del jugador al que se le inflige daño.
        """
        if self.enemigoVivo:
            danoRecibido = self.danoBase
            jugador.recibirDano(danoRecibido)
    
    def disparar(self):
        """
        Crea un nuevo proyectil y lo agrega a self.proyectiles.
        Solo dispara si self.cooldownDisparo <= 0.
        """
        # Verificar enfriamiento
        if self.cooldownDisparo <= 0 and self.enemigoVivo:
            # Posición inicial del proyectil:
            # Si el enemigo mira a la derecha, sale justo al borde derecho del sprite.
            # Si mira a la izquierda, sale al borde izquierdo.
            if self.direccion == "derecha":
                px = self.posX + self.dimAncho
                vel = 10      # velocidad positiva (derecha)
            else:  # "izquierda"
                px = self.posX - 10  # sale ligeramente a la izquierda del sprite
                vel = -10     # velocidad negativa (izquierda)

            # Altura media del enemigo para centrar el disparo verticalmente
            py = self.posY + (self.dimAlto // 2)

            # Crear diccionario que represente el proyectil
            nuevoProyectil = {
                "x": float(px),
                "y": float(py),
                "vel": float(vel),
                "ancho": 2,    # ancho del proyectil (px)
                "alto": 2,      # alto del proyectil (px)
                "activo": True
            }

            # Agregar a la lista de proyectiles del enemigo
            self.proyectiles.append(nuevoProyectil)

            # Reiniciar enfriamiento
            self.cooldownDisparo = 20
    
    def actualizarProyectiles(self, jugador, anchoPantalla):
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
            
            # Comprobar colisión con jugador
            if jugador.jugadorVivo and rect_p.colliderect(jugador.rect):
                jugador.recibirDano(1)
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
        
        :param pantalla: superficie de PyGame donde se dibuja el ambiente del juego.
        """
        for p in self.proyectiles:
            rect_dibujo = pygame.Rect(int(p["x"]), int(p["y"]), p["ancho"], p["alto"])
            pygame.draw.rect(pantalla, (255, 255, 0), rect_dibujo)

    def recibirDano(self, danoRecibido):
        """
        Método para recibir daño. Reduce la vida del enemigo.
        Si la vida llega a 0, el enemigo muere.
        """
        self.vida -= danoRecibido
        # Verificar si el enemigo ha muerto
        if self.vida <= 0:
            self.enemigoMuerto()

    def avanzarAnimacion(self):
        """
        Actualiza el frame actual de la animación según el estado del enemigo.
        """
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
        Dibuja el frame actual de la animación en pantalla, en la posición del enemigo.
        """
        if self.estadoAnimacion in self.sprites:
            frames = self.sprites[self.estadoAnimacion]
            if frames:  # Verifica que haya al menos un frame
                sprite = frames[self.frameActual]
                pantalla.blit(sprite, (int(self.posX), int(self.posY)))
    
    def reinicioAnimacion(self):
        """
        Reinicia la animación al primer frame del estado actual.
        """
        self.frameActual = 0
        self.contadorFrames = 0

class EnemigoCaminante(Enemigo):
    def __init__(self, posX, posY, spritesDict, anchoPantalla, altoPantalla, danoBase, vida):
        super().__init__(posX, posY, spritesDict, anchoPantalla, altoPantalla, danoBase, vida)
        # Este enemigo se mueve con velX = 1.0 cuando está en estadoAnimacion “caminar”
        self.velBaseX = 1.0
        self.gravedad = 0.3
        self.estadoAnimacion = "caminar"  # Por defecto camina

    def decidir_movimiento(self):
        if self.enSuelo:
            self.velX = -self.velBaseX
            self.estadoAnimacion = "caminar"
        else:
            self.estadoAnimacion = "idle"


class EnemigoConAtaque(Enemigo):
    def __init__(self, posX, posY, spritesDict, anchoPantalla, altoPantalla, danoBase, vida):
        super().__init__(posX, posY, spritesDict, anchoPantalla, altoPantalla, danoBase, vida)
        # Este enemigo corre,salta y ataca
        self.contadorMovimiento = 0
        self.velBaseX = 3.0
        self.impulsoY  = 12.0
        self.estadoAnimacion = "idle"  # Por defecto está inactivo

    def decidir_movimiento(self):
        # Enemigo que camina, y de vez en cuando salta y ataca.
        self.contadorMovimiento += 1
        if self.enSuelo:
            # Cuando el contadorMovimiento es un múltiplo de 120, salta
            if self.contadorMovimiento % 120 == 0:
                self.velY = -self.impulsoY
                self.enSuelo = False
                self.estadoAnimacion = "idle"  # Mientras está en el aire, idle
            # Cuando el contadorMovimiento es un múltiplo de 60, dispara
            elif self.contadorMovimiento % 60 == 0:
                self.estadoAnimacion = "atacar"
                self.disparar()
            else:
                self.estadoAnimacion = "caminar"
        else:
            # En el aire no camina ni dispara
            self.estadoAnimacion = "idle"

    

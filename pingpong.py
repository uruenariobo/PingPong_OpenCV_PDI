# --------------------------------------------------------------------------
# ------- PLANTILLA DE CÓDIGO ----------------------------------------------
# ------- Conceptos básicos de PDI - PING PONG ------------------------------
# ------- Por: Miguel Urueña    miguel.uruena@udea.edu.co ------------------
# -------      Estudiante Facultad de Ingeniería ---------------------------
# -------      CC 1006121797, Wpp 3166704467 -------------------------------
# ------- Curso Básico de Procesamiento Digital de Imágenes ----------------
# ------- Febrero 2022 - SEM2021-2 -----------------------------------------
# --------------------------------------------------------------------------
# --------------------------------------------------------------------------

# --1. Inicializo el sistema -----------------------------------------------
# --------------------------------------------------------------------------

# Se importa las librerías necesarias para el desarrollo del sistema
import pygame
import cv2 as cv
import numpy as np
import os
import sys

# -----------
# Constantes
# -----------
from builtins import print, input, len, str, int

AnchoPantalla = 1280  # Ancho de la ventana de juego
AlturaPantalla = 720  # Alto de la ventana de juego
DireccionImagen = "imagenes"  # Nombre de la carpeta que aloja las imagenes
DireccionSonido = "sonidos"  # Nombre de la carpeta que aloja los sonidos

# Se establece los arreglos que contienen los colores que serán usados posteriormente para el texto
Rojo = [255, 0, 0]
Azul = [0, 0, 255]

TipoDeFuente = pygame.font.match_font('Agency FB')  # Tipo de fuente para el texto

# ------------------------------
# Clases y Funciones utilizadas
# ------------------------------
y = 200
y2 = 200

score1 = 0
score2 = 0


# Función encargar de reubicar los sprites
def scale(i, in_min, in_max, out_min, out_max):  # 50 - 700  : 50 - 430
    return (i - in_min) * (out_max - out_min) / (in_max - in_min) + out_min


# Función encargada de escribir texto en una interfaz recibiendo como parámetros, el nombre de la interfaz, el texto,
# el tamaño la ubicación y el color.
def draw_Text(surf, text, size, x, y, color):
    font = pygame.font.Font(TipoDeFuente, size)
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect()
    text_rect.midtop = (x, y)
    surf.blit(text_surface, text_rect)


# Función encargada de cargar una imagen recibiendo como parámetros el nombre del archivo, la ubicación y si tiene o no
# canal alpha. Después convierte las imágenes al mismo formato de pixel usado por la pantalla.
def CargarImagen(nombre, dir_imagen, alpha=False):
    # Encontramos la ruta completa de la imagen
    ruta = os.path.join(dir_imagen, nombre)
    try:
        image = pygame.image.load(ruta)
    except:
        print("Error, no se puede cargar la imagen: " + ruta)
        sys.exit(1)
    # Comprobar si la imagen tiene "canal alpha" (como los png)
    if alpha is True:
        image = image.convert_alpha()
    else:
        image = image.convert()
    return image


# Función encargada de cargar un sonido recibiendo como parámetros el nombre del archivo y la ubicación.
def CargarSonido(nombre, dir_sonido):
    ruta = os.path.join(dir_sonido, nombre)
    # Intentar cargar el sonido
    try:
        sonido = pygame.mixer.Sound(ruta)
    except pygame.error:
        print("No se pudo cargar el sonido:" + ruta)
        sonido = None
    return sonido


# -----------------------------------------------
# -- 2. Se definen los objetos: Creamos los sprites (clases) de los objetos del juego:

class Pelota(pygame.sprite.Sprite):
    """La bola y su comportamiento en la pantalla"""

    def __init__(self, sonido_golpe):
        pygame.sprite.Sprite.__init__(self)
        self.image = CargarImagen("bola2.png", DireccionImagen, alpha=True)  # Se carga la imagen que representará la
        # pelota.
        self.rect = self.image.get_rect()
        # Se ubica la pelota en el centro de la pantalla (su posición inicial).
        self.rect.centerx = AnchoPantalla / 2
        self.rect.centery = AlturaPantalla / 2
        # Se define la velocidad de la pelota.
        self.speed = [12, 12]
        # Se define el sonido que será usado cuando la pelota golpee otros objetos.
        self.sonido_golpe = sonido_golpe

    # Se define la nueva posición de la pelota dependiendo de la ubicación.
    def update(self):
        global score1
        global score2
        # En caso de que la pelota choque con algún borde lateral borde, se ubica de nuevo en centro y se actualizan
        # los puntajes, adicionalmente se le cambia la dirección de movimiento.
        if self.rect.left < 0:
            score1 += 1
            self.speed[0] = -self.speed[0]
            self.rect.centerx = AnchoPantalla / 2
            self.rect.centery = AlturaPantalla / 2
        elif self.rect.right > AnchoPantalla:
            score2 += 1
            self.speed[0] = -self.speed[0]
            self.rect.centerx = AnchoPantalla / 2
            self.rect.centery = AlturaPantalla / 2
        # En caso de que la pelota choque con los bordes superior o inferior se invierte la dirección de movimiento.
        elif self.rect.top < 0 or self.rect.bottom > AlturaPantalla:
            self.speed[1] = -self.speed[1]
        self.rect.move_ip((self.speed[0], self.speed[1]))

    # En caso de que colisione con alguna de las raquetas entonces se invierte la dirección y se reproduce el sonido de
    # rebote.
    def colision(self, objetivo):
        if self.rect.colliderect(objetivo.rect):
            self.speed[0] = -self.speed[0]
            self.sonido_golpe.play()  # Reproducir sonido de rebote


class Paleta(pygame.sprite.Sprite):
    """Define el comportamiento de las paletas de ambos jugadores"""

    def __init__(self, x, rutaImagen):
        pygame.sprite.Sprite.__init__(self)
        self.speed = None
        self.image = CargarImagen(rutaImagen, DireccionImagen, alpha=True)  # Se carga la imagen que representará la
        # pelota.
        self.rect = self.image.get_rect()
        # Se ubican las raquetas en el centro de la pantalla (su posición inicial).
        self.rect.centerx = x
        self.rect.centery = AlturaPantalla / 2

    def humano(self):
        # Se controla que las raquetas no salgan de la pantalla y lleguen máximo hasta las esquinas.
        if self.rect.bottom >= AlturaPantalla:
            self.rect.bottom = AlturaPantalla
        elif self.rect.top <= 0:
            self.rect.top = 0

    def cpu(self, pelota):
        self.speed = [0, 2.5]
        if pelota.speed[0] >= 0 and pelota.rect.centerx >= AnchoPantalla / 2:
            if self.rect.centery > pelota.rect.centery:
                self.rect.centery -= self.speed[1]
            if self.rect.centery < pelota.rect.centery:
                self.rect.centery += self.speed[1]


# ------------------------------
# Función principal del juego
# ------------------------------


def main():
    global y
    global y2
    global score1
    global score2

    # -- 3. Se captura el video de la cámara.
    cap = cv.VideoCapture(0)
    j1 = input("INGRESE EL NOMBRE DEL JUGADOR 1 (Azul):")  # Se recibe el nombre del jugador azul y se almacena.
    j2 = input("INGRESE EL NOMBRE DEL JUGADOR 2 (Rojo):")  # Se recibe el nombre del jugador Rojo y se almacena.
    # Se inicia el juego.
    pygame.init()
    pygame.mixer.init()
    # creamos la ventana y le indicamos un título:
    screen = pygame.display.set_mode((AnchoPantalla, AlturaPantalla))  # Se define el tamaño de la ventana de juego.
    pygame.display.set_caption("PingPong PDI 2021-2")  # Se establece el Nombre de la ventana de juego.
    icono = CargarImagen("icono.png", DireccionImagen, alpha=True)  # Se carga la imagen que usaremos como icono.
    pygame.display.set_icon(icono)  # Se define el icono de la ventana.
    # cargamos los objetos
    fondo = CargarImagen("fondo.jpg", DireccionImagen, alpha=False)  # Cargamos la imagen del tablero de fondo.
    sonido_golpe = CargarSonido("tennis.ogg", DireccionSonido)  # Cargamos el sonido de rebote.

    bola = Pelota(sonido_golpe)  # Creamos un elemento de la clase pelota
    jugador1 = Paleta(40, "paletaAzul1.png")  # Creamos un elemento de la clase paleta que será el jugador azul.
    jugador2 = Paleta(AnchoPantalla - 40, "paletaRoja1.png")  # Creamos un elemento de la clase paleta que será el
    # jugador rojo.

    clock = pygame.time.Clock()  # Inicializamos el reloj, el cual ira actualizando la posición de los elementos.
    pygame.key.set_repeat(1, 25)  # Activa repetición de teclas
    pygame.mouse.set_visible(True)  # Dejamos el mouse visible en la ventana de juego

    screen.blit(fondo, (0, 0))  # Fijamos la imagen de fondo en la interfaz.
    #  Se crea el texto de los nombres, puntajes y la instrucción para empezar.
    draw_Text(screen, "Azul:" + j1, 48, ((AnchoPantalla / 2) - (len(j1)) - 200), 0, Azul)
    draw_Text(screen, str(score2), 48, (AnchoPantalla / 2) - 40, 0, Azul)
    draw_Text(screen, str(score1), 48, (AnchoPantalla / 2) + 40, 0, Rojo)
    draw_Text(screen, "Rojo:" + j2, 48, ((AnchoPantalla / 2) + (len(j2)) + 200), 0, Rojo)
    draw_Text(screen, "PRESIONA LA BARRA ESPACIADORA PARA COMENZAR", 60, AnchoPantalla / 2, AlturaPantalla / 2 + 250,
              Rojo)
    # Creamos un grupo con la pelota y las raquetas de los dos jugadores.
    todos = pygame.sprite.RenderPlain(bola, jugador1, jugador2)
    # Dibujamos el grupo creado.
    todos.draw(screen)
    # Se actualiza la superficie de visualización.
    pygame.display.flip()

    # Definimos la variable que indicará el momento en que el usuario está listo para empezar a jugar.
    wait = False
    # Bucle que detecta el momento en que el usuario desea empezar.
    while not wait:
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                wait = True
            elif event.type == pygame.QUIT:
                sys.exit(0)
                # el bucle principal del juego
    # Bucle que se corre cuando el usuario decide empezar (Oprime tecla "espacio")
    while True:
        # Comienza el conteo del reloj.
        clock.tick(60)

        # Actualizamos los objetos en pantalla (raquetas y pelota)
        jugador1.humano()
        jugador2.humano()
        bola.update()

        # Comprobamos si colisionan los objetos
        bola.colision(jugador1)
        bola.colision(jugador2)

        ny = scale(y, 100, 350, 60, 500)
        ny2 = scale(y2, 100, 350, 60, 500)

        # Se crea un frame con el video de la camara.
        _, frame = cap.read()
        # 4. Convert BGR to HSV
        hsv = cv.cvtColor(frame, cv.COLOR_BGR2HSV)

        # 5. Umbralización: Se definen los rangos de color (Azul y rojo).
        # Define range of Blue color in HSV
        lower_blue = np.array([100, 82, 42])
        upper_blue = np.array([255, 248, 110])
        # Define range of Red color in HSV
        lower_red = np.array([169, 100, 100])
        upper_red = np.array([189, 255, 255])
        # Threshold the HSV image to get only blue colors
        mask = cv.inRange(hsv, lower_blue, upper_blue)
        # Threshold the HSV image to get only red colors
        mask2 = cv.inRange(hsv, lower_red, upper_red)

        # 6. Erosión: Aplicamos la erosión a la máscara resultante del rango Azul
        filtro1 = cv.erode(mask, cv.getStructuringElement(cv.MORPH_RECT, (3, 3)), iterations=1)
        filtro2 = cv.erode(filtro1, cv.getStructuringElement(cv.MORPH_RECT, (5, 5)), iterations=1)

        # Aplicamos la erosión a la máscara resultante del rango Rojo
        filtro3 = cv.erode(mask2, cv.getStructuringElement(cv.MORPH_RECT, (3, 3)), iterations=1)
        filtro4 = cv.erode(filtro3, cv.getStructuringElement(cv.MORPH_RECT, (5, 5)), iterations=1)

        # 7. Calculo de centros. -------------------------------------------------------------------------
        try:
            # Calculamos los centros de los contornos de las figuras resultantes posteriores a las erosiones.
            objct = cv.moments(filtro2)
            if objct['m00'] > 50000:
                cx = int(objct['m10'] / objct['m00'] + 1)
                cy = int(objct['m01'] / objct['m00'] + 1)
                cv.circle(frame, (cx, cy), 10, (0, 0, 255), 4)  # Se dibujan los círculos rojos en el centro de los
                # contornos.
                y = cy

            objct2 = cv.moments(filtro4)
            if objct2['m00'] > 50000:
                cx2 = int(objct2['m10'] / objct2['m00'] + 1)
                cy2 = int(objct2['m01'] / objct2['m00'] + 1)
                cv.circle(frame, (cx2, cy2), 10, (0, 0, 255), 4)  # Se dibujan los círculos rojos en el centro de
                # los contornos.
                y2 = cy2
        except:
            print("error")

        # 8. Reflexión de video. -------------------------------------------------------------------------

        anchomitad = frame.shape[1] // 2  # Ubicamos el centro del ancho para usarlo como eje de reflexión.
        frameEspejo = cv.flip(frame, anchomitad)  # Aplicamos la reflexion usando como eje la mitad del ancho.
        cv.imshow('VideoOriginal', frameEspejo)  # Se muestra el video de la camara posterior a la reflexión con los

        # círculos en el centro de los contornos.

        # 9. Actualización posición de sprites y puntajes. ---------------------------------------------------------

        # Se mueven los objetos raquetas de acuerdo a la detección del movimiento de los contornos.
        jugador1.rect.centery = ny
        jugador2.rect.centery = ny2
        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                sys.exit(0)

        # Actualizamos los puntajes en pantalla y los elementos.
        screen.blit(fondo, (0, 0))
        draw_Text(screen, "Azul:" + j1, 48, ((AnchoPantalla / 2) - (len(j1)) - 200), 0, Azul)
        draw_Text(screen, str(score2), 48, (AnchoPantalla / 2) - 40, 0, Azul)
        draw_Text(screen, str(score1), 48, (AnchoPantalla / 2) + 40, 0, Rojo)
        draw_Text(screen, "Rojo:" + j2, 48, ((AnchoPantalla / 2) + (len(j2)) + 200), 0, Rojo)
        todos = pygame.sprite.RenderPlain(bola, jugador1, jugador2)
        todos.draw(screen)
        pygame.display.flip()


if __name__ == "__main__":
    main()

# --------------------------------------------------------------------------
# ---------------------------  FIN DEL PROGRAMA ----------------------------
# --------------------------------------------------------------------------

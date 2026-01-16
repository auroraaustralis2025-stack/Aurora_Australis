import math
import pygame
import os
import sys
from PIL import Image, ImageSequence
import logging
import datetime
import csv

# ===============================================================================
# CONFIGURACIÓN DE LOGGING CSV
# ===============================================================================
# Crear directorio de logs si no existe
if not os.path.exists('logs'):
    os.makedirs('logs')

# Crear archivo CSV para eventos de botones
csv_filename = f"logs/botones_events_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"

# Escribir encabezados en el CSV
with open(csv_filename, 'w', newline='', encoding='utf-8') as csvfile:
    csv_writer = csv.writer(csvfile)
    csv_writer.writerow(['timestamp', 'jugador', 'boton', 'accion', 'nombre_capa'])

# Función para registrar eventos en CSV
def log_evento_csv(jugador, boton, accion, nombre_capa):
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
    with open(csv_filename, 'a', newline='', encoding='utf-8') as csvfile:
        csv_writer = csv.writer(csvfile)
        csv_writer.writerow([timestamp, jugador, boton, accion, nombre_capa])

# Configurar logger minimalista
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(message)s',
    handlers=[
        logging.FileHandler(f"logs/aurora_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger('AuroraLogger')

# ===============================================================================
# CONFIGURACIÓN INICIAL DE POSICIÓN DE VENTANA
# ===============================================================================
# Establecer posición de la ventana antes de inicializar Pygame
os.environ['SDL_VIDEO_WINDOW_POS'] = "0,0"
os.environ['SDL_VIDEODRIVER'] = 'windib'

# Inicializar Pygame
pygame.init()

# ===============================================================================
# CONFIGURACIÓN DE JOYSTICKS
# ===============================================================================
# Inicializar subsistema de joysticks
pygame.joystick.init()

# Obtener lista de joysticks conectados
joysticks = []
for i in range(pygame.joystick.get_count()):
    joystick = pygame.joystick.Joystick(i)
    joystick.init()
    joysticks.append(joystick)
    logger.info(f"Joystick {i}: {joystick.get_name()}")

# ===============================================================================
# CONFIGURACIÓN DE VENTANA CON TRES MONITORES (5760x1080)
# ===============================================================================
screen_width = 5760
screen_height = 1080

# Registrar configuración de pantalla
logger.info(f"Iniciando aplicación Aurora Australis")
logger.info(f"Configuración de pantalla: {screen_width}x{screen_height} px")
logger.info(f"Joysticks detectados: {pygame.joystick.get_count()}")

# Crear ventana sin bordes del tamaño de los tres monitores
screen = pygame.display.set_mode((screen_width, screen_height), pygame.NOFRAME)
pygame.display.set_caption("Proyecto Aurora Australis")

# ===============================================================================
# PANTALLA DE CARGA (SPLASH SCREEN)
# ===============================================================================
def mostrar_splash():
    try:
        splash = pygame.image.load(r"C:\IMAGENES\SPLASH.png")
        splash = pygame.transform.scale(splash, (screen_width, screen_height))
        screen.blit(splash, (0, 0))
        pygame.display.flip()
        return True
    except Exception as e:
        logger.error(f"Error al cargar pantalla de carga: {e}")
        return False

# Mostrar splash screen al inicio
splash_visible = mostrar_splash()

# ===============================================================================
# CONFIGURACIÓN DE SONIDOS
# ===============================================================================
ruta_sonidos = r"C:\SONIDOS"
ruta_voz_off = r"C:\VOZ EN OFF AURORA"

mapeo_sonidos = {
    "INCENDIOS.png": "1INCENDIOS.mp3",
    "NATIVO.png": "2NATIVO.mp3",
    "TERMALES.gif": "3TERMALES.mp3",  # Cambiado a .gif
    "PATRIMONIO.png": "4PATRIMONIO.mp3",
    "VOLC.gif": "5VOLCANES.mp3",
    "REDVIAL.png": "6REDVIAL.mp3",
    "PRODUCTIVO.png": "7PRODUCTIVO.mp3",
    "PRECIPITACION.gif": "8PRECIP.mp3",
    "HIDRO.png": "9CUERPOSDEAGUA.mp3",
    "SNASPE.png": "10SNASPE.mp3",
    "COMUNIDADES.png": "11COMUNIDADES.mp3",
    "SALUD.png": "12EDUCACION.mp3",
    "TIEMPO.gif": "13DINAMICA.mp3",      # Nuevo
    "FALLAS.gif": "14FALLAS.mp3",        # Nuevo
    "COMUNAS.png": "15LIMITES.mp3",      # Nuevo
    "SATELITAL.png": "16SATELITAL.mp3",  # Nuevo
    "PELIGRO.png": "17PELIGRO.mp3",      # Nuevo
    "ARALERCE.png": "18ARALERCE.mp3"     # Nuevo
}
# Sonidos para teclas
teclas_sonidos = {
    pygame.K_q: "BIENVENIDA.mp3",
    pygame.K_w: "Instrucciones.mp3",
    pygame.K_e: "Volcanes.mp3",
    pygame.K_r: "Bosque.mp3",
    pygame.K_t: "Agua.mp3",
    pygame.K_y: "Productivo.mp3"
}

# Inicializar mixer de pygame
pygame.mixer.init()
sonidos_cargados = {}

# Cargar todos los sonidos de capas al inicio
for archivo_capa, archivo_sonido in mapeo_sonidos.items():
    ruta_sonido = os.path.join(ruta_sonidos, archivo_sonido)
    try:
        sonido = pygame.mixer.Sound(ruta_sonido)
        sonidos_cargados[archivo_capa] = sonido
        logger.info(f"Sonido cargado: {archivo_sonido}")
    except Exception as e:
        logger.error(f"Error al cargar sonido {archivo_sonido}: {e}")
        sonidos_cargados[archivo_capa] = None

# Cargar sonidos de teclas
sonidos_teclas = {}
for tecla, archivo_sonido in teclas_sonidos.items():
    ruta_sonido = os.path.join(ruta_voz_off, archivo_sonido)
    try:
        sonido = pygame.mixer.Sound(ruta_sonido)
        sonidos_teclas[tecla] = sonido
        logger.info(f"Sonido de tecla cargado: {archivo_sonido}")
    except Exception as e:
        logger.error(f"Error al cargar sonido de tecla {archivo_sonido}: {e}")
        sonidos_teclas[tecla] = None

# ===============================================================================
# FUNCIONES DE SÍMBOLOS PERSONALIZADOS
# ===============================================================================
def dibujar_simbolo_diagonal(surface, color, rect):
    x, y, w, h = rect
    pygame.draw.line(surface, color, (x, y), (x + w, y + h), 2)
    pygame.draw.line(surface, color, (x + w, y), (x, y + h), 2)

def dibujar_simbolo_diamante(surface, color, rect):
    x, y, w, h = rect
    puntos = [
        (x + w//2, y),
        (x + w, y + h//2),
        (x + w//2, y + h),
        (x, y + h//2)
    ]
    pygame.draw.polygon(surface, color, puntos, 2)
    pygame.draw.circle(surface, "#ff0000", (x + w//2, y + h//2), 2)

def dibujar_circulo_seia(surface, color, rect, radio):
    x, y, w, h = rect
    centro = (x + w//2, y + h//2)
    pygame.draw.circle(surface, color, centro, radio, 1)

def dibujar_linea_solida(surface, color, rect):
    x, y, w, h = rect
    pygame.draw.line(surface, color, (x, y + h//2), (x + w, y + h//2), 2)

def dibujar_linea_punteada(surface, color, rect):
    x, y, w, h = rect
    dash_length = 4
    gap = 3
    current_x = x
    while current_x < x + w:
        pygame.draw.line(surface, color, 
                        (current_x, y + h//2), 
                        (min(current_x + dash_length, x + w), y + h//2), 
                        1)
        current_x += dash_length + gap

def dibujar_punto_circulo(surface, color, rect):
    x, y, w, h = rect
    centro = (x + w//2, y + h//2)
    pygame.draw.circle(surface, color, centro, 2)

def dibujar_limite_predial(surface, color, rect):
    x, y, w, h = rect
    pygame.draw.rect(surface, color, (x, y, w, h), 1)

def dibujar_simbolo_incendios(surface, color, rect):
    x, y, w, h = rect
    puntos = [
        (x + w//2, y),
        (x, y + h),
        (x + w, y + h)
    ]
    pygame.draw.polygon(surface, color, puntos)

def dibujar_circulo_relleno(surface, color, rect, radio):
    x, y, w, h = rect
    centro = (x + w//2, y + h//2)
    pygame.draw.circle(surface, color, centro, radio)

def dibujar_linea_2px(surface, color, rect):
    x, y, w, h = rect
    pygame.draw.line(surface, color, (x, y + h//2), (x + w, y + h//2), 2)

def dibujar_triangulo(surface, color, rect):
    x, y, w, h = rect
    puntos = [
        (x + w//2, y),
        (x, y + h),
        (x + w, y + h)
    ]
    pygame.draw.polygon(surface, color, puntos)

def dibujar_circulo_punteado(surface, color, centro, radio, grosor, dash_length=4):
    circunferencia = 2 * 3.1416 * radio
    num_dashes = int(circunferencia / (dash_length * 2))
    angle_step = 360 / num_dashes
    for i in range(num_dashes):
        start_angle = math.radians(i * angle_step)
        end_angle = math.radians(i * angle_step + angle_step/2)
        pygame.draw.arc(surface, color, (centro[0]-radio, centro[1]-radio, 2*radio, 2*radio),
                        start_angle, end_angle, grosor)

def dibujar_circulo_doble_punteado(surface, color, rect):
    x, y, w, h = rect
    centro = (x + w//2, y + h//2)
    dibujar_circulo_punteado(surface, color, centro, 12, 2)
    pygame.draw.circle(surface, color, centro, 5)

def dibujar_cruz(surface, color, rect):
    x, y, w, h = rect
    centro = (x + w//2, y + h//2)
    largo = int(min(w, h) * 0.25)
    
    pygame.draw.line(surface, color, 
                    (centro[0] - largo, centro[1]), 
                    (centro[0] + largo, centro[1]), 2)
    
    pygame.draw.line(surface, color, 
                    (centro[0], centro[1] - largo), 
                    (centro[0], centro[1] + largo), 2)
    
    pygame.draw.line(surface, color,
                    (centro[0] - int(w * 0.35), centro[1]),
                    (centro[0] + int(w * 0.35), centro[1]),
                    2)
    
    pygame.draw.line(surface, color,
                    (centro[0], centro[1] - int(h * 0.35)),
                    (centro[0], centro[1] + int(h * 0.35)),
                    2)

def dibujar_circulo_doble(surface, color, rect):
    x, y, w, h = rect
    centro = (x + w//2, y + h//2)
    pygame.draw.circle(surface, color, centro, 12, 2)
    pygame.draw.circle(surface, color, centro, 6)

# Nuevas funciones para los símbolos modificados
def dibujar_circulo_doble_relleno(surface, color, rect):
    x, y, w, h = rect
    centro = (x + w//2, y + h//2)
    # Círculo exterior blanco
    pygame.draw.circle(surface, (255, 255, 255), centro, w//2)
    # Círculo interior del color
    pygame.draw.circle(surface, color, centro, w//2 - 2)
    # Punto blanco en el centro
    pygame.draw.circle(surface, (255, 255, 255), centro, 2)

def dibujar_cruz_con_circulo(surface, color, rect):
    x, y, w, h = rect
    centro = (x + w//2, y + h//2)
    # Círculo blanco de fondo
    pygame.draw.circle(surface, (255, 255, 255), centro, 10)
    # Cruz roja
    largo = int(min(w, h) * 0.25)
    pygame.draw.line(surface, color, 
                    (centro[0] - largo, centro[1]), 
                    (centro[0] + largo, centro[1]), 2)
    pygame.draw.line(surface, color, 
                    (centro[0], centro[1] - largo), 
                    (centro[0], centro[1] + largo), 2)

# Nuevo símbolo para patrimonio geológico
def dibujar_circulo_doble_borde(surface, color, rect):
    x, y, w, h = rect
    centro = (x + w//2, y + h//2)
    # Círculo exterior más grande (10px)
    pygame.draw.circle(surface, color, centro, 10, 1)
    # Círculo interior más pequeño (5px) con grosor 3px
    pygame.draw.circle(surface, color, centro, 5, 3)

# ===============================================================================
# FUNCIONES DE CARGA DE IMÁGENES
# ===============================================================================
def cargar_gif(ruta, ancho, alto):
    try:
        gif = Image.open(ruta)
        frames = []
        for frame in ImageSequence.Iterator(gif):
            frame = frame.convert("RGBA")
            pygame_frame = pygame.image.fromstring(
                frame.tobytes(), frame.size, frame.mode
            ).convert_alpha()
            frames.append(pygame.transform.scale(pygame_frame, (ancho, alto)))
        logger.info(f"GIF cargado: {ruta} ({len(frames)} frames)")
        return frames
    except Exception as e:
        logger.error(f"Error al cargar GIF {ruta}: {e}")
        return [pygame.Surface((ancho, alto))]

def cargar_imagen_escalada(ruta, ancho, alto):
    try:
        if ruta.lower().endswith('.gif'):
            return cargar_gif(ruta, ancho, alto)
        else:
            imagen = pygame.image.load(ruta).convert_alpha()
            logger.info(f"Imagen cargada: {ruta}")
            return [pygame.transform.scale(imagen, (ancho, alto))]
    except Exception as e:
        logger.error(f"Error al cargar {ruta}: {e}")
        return [pygame.Surface((ancho, alto))]

# ===============================================================================
# CLASE DE IMAGEN CON FADE Y SONIDO
# ===============================================================================
class ImagenConFade:
    def __init__(self, config):
        self.nombre = config['nombre']
        self.archivo = config.get('archivo', '')
        self.es_reinicio = config.get('es_reinicio', False)
        self.color = pygame.Color(config.get('color', '#ffffff'))
        self.leyenda = config.get('leyenda', [])
        self.titulo_leyenda = config.get('titulo_leyenda', None)
        self.leyenda_compartida = config.get('leyenda_compartida', None)
        self.max_alpha = config.get('max_alpha', 255)

        # Atributos de animación
        self.frames = []
        self.frame_actual = 0
        self.alpha = 0
        self.velocidad_fade = 15
        self.activa = False
        self.orden = 0
        self.ultimo_update = pygame.time.get_ticks()
        self.intervalo_animacion = 100
        
        # Atributos de sonido
        self.sonido = None
        self.sonido_reproduciendose = False
        
        # Cargar sonido si corresponde
        if self.archivo in sonidos_cargados:
            self.sonido = sonidos_cargados[self.archivo]
            logger.info(f"Sonido asignado a capa '{self.nombre}'")
        
        if self.archivo:
            ruta_completa = os.path.join(ruta_imagenes, self.archivo)
            self.frames = cargar_imagen_escalada(ruta_completa, 3840, 1080)

    def actualizar_animacion(self):
        if self.frames:
            ahora = pygame.time.get_ticks()
            if ahora - self.ultimo_update > self.intervalo_animacion:
                self.frame_actual = (self.frame_actual + 1) % len(self.frames)
                self.ultimo_update = ahora

    def reproducir_sonido(self):
        if self.sonido and not self.sonido_reproduciendose:
            self.sonido.play()
            self.sonido_reproduciendose = True
            logger.info(f"Reproduciendo sonido para capa '{self.nombre}'")

    def detener_sonido(self):
        if self.sonido and self.sonido_reproduciendose:
            self.sonido.stop()
            self.sonido_reproduciendose = False
            logger.info(f"Deteniendo sonido para capa '{self.nombre}'")

    def fade_in(self):
        if self.alpha < self.max_alpha:
            self.alpha = min(self.alpha + self.velocidad_fade, self.max_alpha)
            if self.alpha == self.max_alpha:
                logger.info(f"Capa '{self.nombre}' completamente visible")
                self.reproducir_sonido()

    def fade_out(self):
        if self.alpha > 0:
            self.alpha = max(self.alpha - self.velocidad_fade, 0)
            if self.alpha == 0:
                logger.info(f"Capa '{self.nombre}' completamente oculta")
                self.detener_sonido()

    def dibujar(self, pantalla):
        if self.frames:
            self.actualizar_animacion()
            frame = self.frames[self.frame_actual]
            frame.set_alpha(self.alpha)
            pantalla.blit(frame, (0, 0))

# ===============================================================================
# CONFIGURACIÓN DE CAPAS CON ASIGNACIÓN PERSONALIZADA
# ===============================================================================
ruta_imagenes = r"C:\IMAGENES"

# Lista de acciones con asignación específica de jugador y botón
acciones_y_rutas = [
    # JUGADOR 1
    {"nombre": "Fuentes termales", "jugador": 1, "boton": 0, "color": "#00edff", "archivo": "TERMALES.gif", "titulo_leyenda": "Fuentes termales", "leyenda": [{"nombre": "Fuentes termales", "color": "#00edff", "simbolo": "circulo_doble_punteado"}]},
    {"nombre": "Volcanes activos", "jugador": 1, "boton": 1, "color": "#ffffff", "archivo": "VOLC.gif", "titulo_leyenda": "Volcanes activos", "leyenda": [{"nombre": "Volcanes activos", "color": "#ff7f00", "simbolo": "circulo_20_relleno"}]},
    {"nombre": "Peligro volcánico", "jugador": 1, "boton": 3, "color": "#ff7f00", "archivo": "PELIGRO.png", "titulo_leyenda": "Peligro volcánico", "leyenda": [{"nombre": "Peligro Alto", "color": "#e31a1c", "simbolo": "cuadrado_relleno"}, {"nombre": "Peligro Medio", "color": "#ff7f00", "simbolo": "cuadrado_relleno"}, {"nombre": "Peligro Bajo", "color": "#ffff00", "simbolo": "cuadrado_relleno"}]},
    {"nombre": "Distribución araucaria-alerce", "jugador": 1, "boton": 4, "color": "#ffffff", "archivo": "ARALERCE.png", "titulo_leyenda": "Distribución Araucaria y Alerce", "leyenda": [{"nombre": "Araucaria", "color": "#b8ff70", "simbolo": "cuadrado_relleno"}, {"nombre": "Alerce", "color": "#fca3a3", "simbolo": "cuadrado_relleno"}]},
    {"nombre": "Cuencas/subcuencas/subsubcuencas", "jugador": 1, "boton": 5, "color": "#ffffff", "archivo": "CUENCAS.png", "titulo_leyenda": "Cuencas", "leyenda": [{"nombre": "Subcuencas", "color": "#ffffff", "simbolo": "linea_solida"}, {"nombre": "Sub-subcuencas", "color": "#ffffff", "simbolo": "linea_punteada"}]},
    {"nombre": "Patrimonio geológico", "jugador": 1, "boton": 6, "color": "#ffd97a", "archivo": "PATRIMONIO.png", "titulo_leyenda": "Patrimonio geológico", "leyenda": [{"nombre": "patrimonio geológico", "color": "#ffd97a", "simbolo": "circulo_doble_borde"}]},
    {"nombre": "Sistema falla liquiñe ofqui", "jugador": 1, "boton": 7, "color": "#ffffff", "archivo": "FALLAS.gif", "titulo_leyenda": "Dinámica Geológica", "leyenda": [{"nombre": "Sistema de fallas tectónicas", "color": "#ffffff", "simbolo": "linea_punteada"}]},
    {"nombre": "Bosque nativo", "jugador": 1, "boton": 8, "color": "#668a63", "archivo": "NATIVO.png", "titulo_leyenda": "Bosque nativo", "leyenda": [{"nombre": "Bosque nativo", "color": "#668a63"}]},
    {"nombre": "Red hidrográfica y masas lacustres", "jugador": 1, "boton": 9, "color": "#a6cee3", "archivo": "HIDRO.png", "titulo_leyenda": "Red hidrográfica y masas lacustres", "leyenda": [{"nombre": "Cuerpos de Agua", "color": "#a6cee3", "simbolo": "cuadrado_relleno"}, {"nombre": "Red hidrográfica", "color": "#a6cee3", "simbolo": "linea_solida"}]},
    {"nombre": "Tipos forestales", "jugador": 1, "boton": 10, "archivo": "TIPOS_FORES.png", "titulo_leyenda": "Tipos Forestales", "leyenda": [
        {"nombre": "Alerce", "color": "#7daa46"},
        {"nombre": "Ciprés de la Cordillera", "color": "#b68d4c"},
        {"nombre": "Ciprés de las Guaitécas", "color": "#8d6e4e"},
        {"nombre": "Coihue de Magallanes", "color": "#2e5a3d"},
        {"nombre": "Coihue/Raulí/tepa", "color": "#3d6b3d"},
        {"nombre": "Esclerófilo", "color": "#d4b04b"},
        {"nombre": "Lenga", "color": "#e67e35"},
        {"nombre": "Roble/Raulí/Coihue", "color": "#85b66f"},
        {"nombre": "Siempreverde", "color": "#3c793c"},
        {"nombre": "Araucaria", "color": "#8c9d5b"}
    ]},
    {"nombre": "Zonas geológicas", "jugador": 1, "boton": 11, "color": "#ffffff", "archivo": "GEOLOGIA.png", "titulo_leyenda": "Composición Geológica", "leyenda": [{"nombre": "Rocas intrusivas", "color": "#e86363"}, {"nombre": "Rocas metamórficas", "color": "#9c9c9c"}, {"nombre": "Rocas estratificadas", "color": "#a47158"}, {"nombre": "Rocas volcánicas", "color": "#8142d3"}, {"nombre": "Sedimentos no consolidados", "color": "#fffe5d"}]},
    
    # JUGADOR 2
    {"nombre": "Dinámica Atmosférica", "jugador": 2, "boton": 2, "archivo": "PRECIPITACION.gif", "color": "#ffffff", "max_alpha": 153, "titulo_leyenda": "Promedio precipitación anual (1980-2020)", "leyenda": [{"nombre": "Baja", "color": "#edfac2", "simbolo": "cuadrado_relleno"}, {"nombre": "Media", "color": "#0570b0", "simbolo": "cuadrado_relleno"}, {"nombre": "Alta", "color": "#6a2c5a", "simbolo": "cuadrado_relleno"}]},
    # REINICIO AHORA EN BOTÓN 3 DEL JUGADOR 2
    {"nombre": "Pantalla de reinicio", "jugador": 2, "boton": 3, "archivo": "INICIO.png", "es_reinicio": True},
    {"nombre": "Espacios productivos", "jugador": 2, "boton": 4, "color": "#ffffff", "archivo": "PRODUCTIVO.png", "titulo_leyenda": "Usos productivos", "leyenda": [{"nombre": "Agrícola", "color": "#f7ebbf"}, {"nombre": "Forestal", "color": "#7a5900"}, {"nombre": "Acuícola", "color": "#ff2323"}]},
    {"nombre": "Topografía", "jugador": 2, "boton": 5, "color": "#ffffff", "archivo": "DEM.png", "max_alpha": 153, "titulo_leyenda": "Elevación", "leyenda": [{"nombre": "Baja (0-750 m.s.n.m)", "color": "#180f3e", "simbolo": "cuadrado_relleno"}, {"nombre": "Media (751-1500 m.s.n.m)", "color": "#cd3f71", "simbolo": "cuadrado_relleno"}, {"nombre": "Alta (>1500 m.s.n.m)", "color": "#fec98d", "simbolo": "cuadrado_relleno"}]},
    {"nombre": "Red vial", "jugador": 2, "boton": 6, "archivo": "REDVIAL.png", "titulo_leyenda": "Red vial", "leyenda": [{"nombre": "Carreteras", "color": "#ffff00", "simbolo": "linea_solida"}, {"nombre": "Calles y Caminos", "color": "#ffff00", "simbolo": "linea_solida"}]},
    {"nombre": "Límites comunales, regionales, comunas ANDES", "jugador": 2, "boton": 7, "color": "#ffffff", "archivo": "COMUNAS.png", "titulo_leyenda": "Límites administrativos", "leyenda": [{"nombre": "Límites comunales", "color": "#ffffff", "simbolo": "linea_solida"}, {"nombre": "Comunas Andes del Sur", "color": "#b7484b", "simbolo": "cuadrado_relleno"}]},
    {"nombre": "Satelital", "jugador": 2, "boton": 8, "color": "#ffffff", "archivo": "SATELITAL.png", "titulo_leyenda": "Imagen Satelital", "leyenda": [{"nombre": "Imagen Satelital", "color": "#ffffff"}]},
    {"nombre": "Usos de suelo 2022", "jugador": 2, "boton": 11, "archivo": "USOS_2020.png", "leyenda_compartida": "usos_suelo", "titulo_leyenda": "Usos de suelo 2022"},
    {"nombre": "Usos de suelo 2002", "jugador": 2, "boton": 10, "archivo": "USOS_2000.png", "leyenda_compartida": "usos_suelo", "titulo_leyenda": "Usos de suelo 2002"},
    
    # JUGADOR 3
    {"nombre": "Comunidades indígenas", "jugador": 3, "boton": 0, "color": "#1f78b4", "archivo": "COMUNIDADES.png", "titulo_leyenda": "Comunidades indígenas", "leyenda": [{"nombre": "Comunidades indígenas", "color": "#1f78b4", "simbolo": "circulo_doble_relleno"}]},
    # SOLO ÁREAS POBLADAS EN BOTÓN 3 DEL JUGADOR 3
    {"nombre": "Áreas pobladas y viviendas rurales", "jugador": 3, "boton": 3, "color": "#ffffff", "archivo": "VIVIENDAS_2.png", "titulo_leyenda": "Áreas pobladas", "leyenda": [{"nombre": "Áreas pobladas", "color": "#ffffff"}]},
    {"nombre": "SEIA 1994-2004", "jugador": 3, "boton": 4, "color": "#ffffff", "archivo": "SEA94.png", "leyenda_compartida": "seia", "titulo_leyenda": "Tamaño de inversión (SEIA)"},
    {"nombre": "Establecimientos educacionales y salud", "jugador": 3, "boton": 5, "color": "#ffffff", "archivo": "SALUD.png", "titulo_leyenda": "Establecimientos", "leyenda": [{"nombre": "Educacionales", "color": "#ff0000", "simbolo": "triangulo_8"}, {"nombre": "Salud", "color": "#ff0000", "simbolo": "cruz_con_circulo"}]},
    {"nombre": "SEIA 2015-2024", "jugador": 3, "boton": 6, "color": "#ffffff", "archivo": "SEA14.png", "leyenda_compartida": "seia", "titulo_leyenda": "Tamaño de inversión (SEIA)"},
    {"nombre": "SEIA 2005-2014", "jugador": 3, "boton": 7, "color": "#ffffff", "archivo": "SEA24.png", "leyenda_compartida": "seia", "titulo_leyenda": "Tamaño de inversión (SEIA)"},
    {"nombre": "Incendios forestales", "jugador": 3, "boton": 8, "archivo": "INCENDIOS.png", "titulo_leyenda": "Incendios forestales 2014-2024", "leyenda": [{"nombre": "Incendios 2014-2024", "color": "#ff7f00", "simbolo": "incendio"}]},
    {"nombre": "Dinámica Atmosférica", "jugador": 3, "boton": 10, "archivo": "TIEMPO.gif", "titulo_leyenda": "Dinámica Atmosférica", "leyenda": [{"nombre": "Dinámica atmosférica", "color": "#ffffff", "simbolo": "cuadrado_relleno"}]},
    {"nombre": "Conservación privada y SNASPE", "jugador": 3, "boton": 11, "archivo": "SNASPE.png", "titulo_leyenda": "Conservación y SNASPE", "leyenda": [{"nombre": "Conservación privada", "color": "#ffff3c", "simbolo": "diagonal_x"}, {"nombre": "Áreas protegidas del Estado", "color": "#e18ee6", "simbolo": "diagonal_x"}, {"nombre": "Áreas marino-costeras protegidas (EMCPO)", "color": "#19e1ff", "simbolo": "diagonal_x"}]}
]

# Crear objetos de imagen
imagenes_con_fade = [ImagenConFade(config) for config in acciones_y_rutas]

# Crear mapeo (jugador, boton) -> lista de capas
mapeo_capas = {}
for config in acciones_y_rutas:
    clave = (config['jugador'], config['boton'])
    # Buscar el objeto ImagenConFade correspondiente a esta config
    capa_obj = next((c for c in imagenes_con_fade if c.nombre == config['nombre'] and c.archivo == config.get('archivo', '')), None)
    if capa_obj:
        if clave not in mapeo_capas:
            mapeo_capas[clave] = []
        mapeo_capas[clave].append(capa_obj)

# Asignar imagen de reinicio
imagen_reinicio = None
for capa in imagenes_con_fade:
    if capa.es_reinicio:
        imagen_reinicio = capa
        break

# Cargar imagen base solo para los primeros dos monitores (3840x1080)
imagen_base = cargar_imagen_escalada(os.path.join(ruta_imagenes, "BASE.png"), 3840, 1080)[0]

# ===============================================================================
# FINALIZAR CARGA - OCULTAR SPLASH SCREEN
# ===============================================================================
# Después de cargar todos los recursos, quitamos el splash screen
if splash_visible:
    screen.fill((0, 0, 0))
    screen.blit(imagen_base, (0, 0))
    pygame.display.flip()
    logger.info("Recursos cargados - Pantalla de carga ocultada")

# Leyendas comunes
leyenda_comun = [
    {"nombre": "Bosque", "color": "#334632"},
    {"nombre": "Plantación forestal", "color": "#7a5900"},
    {"nombre": "Formación natural no boscosa", "color": "#d5ccad"},
    {"nombre": "Humedales", "color": "#519799"},
    {"nombre": "Pradera", "color": "#d5ccad"},
    {"nombre": "Mosaico de agricultura", "color": "#f7ebbf"},
    {"nombre": "Infraestructura", "color": "#d4271e"},
    {"nombre": "Hielo y nieves", "color": "#ffffff"},
    {"nombre": "Matorral", "color": "#a89358"}
]

leyenda_comun_seia = [
    {"nombre": "Inversión pequeña", "color": "#d7b4b3", "simbolo": "circulo_5"},
    {"nombre": "Inversión media", "color": "#d7b4b3", "simbolo": "circulo_15"},
    {"nombre": "Inversión grande", "color": "#d7b4b3", "simbolo": "circulo_20"}
]

# ===============================================================================
# CONFIGURACIÓN DE LEYENDA PARA TERCER MONITOR (1920x1080)
# ===============================================================================
leyenda_ancho_px = 1920
leyenda_alto_px = 1080
leyenda_x = 3840
leyenda_y = 0

# ===============================================================================
# FUNCIÓN DE DIBUJO DE LEYENDA MEJORADA (ESTÁTICA, SIN PAGINACIÓN)
# ===============================================================================
def dibujar_leyenda_tercer_monitor(pantalla, imagenes_activas):
    if not imagenes_activas:
        return

    # Crear superficie para la leyenda
    leyenda_surface = pygame.Surface((leyenda_ancho_px, leyenda_alto_px), pygame.SRCALPHA)
    
    # Márgenes con espacio inferior significativo (1/3 de la pantalla)
    margen_lateral_px = 25
    margen_vertical_px = 25
    margen_inferior_px = 360  # 1/3 de 1080px
    
    # Área de contenido con márgenes
    contenido_ancho = leyenda_ancho_px - 2 * margen_lateral_px
    contenido_alto = leyenda_alto_px - 2 * margen_vertical_px - margen_inferior_px
    
    # Fondo semitransparente con bordes redondeados
    pygame.draw.rect(leyenda_surface, (0, 0, 0, 200), 
                    (margen_lateral_px, margen_vertical_px, 
                     contenido_ancho, contenido_alto), 0, 10)

    # Generar elementos de la leyenda
    elementos = []
    leyendas_ya_agregadas = set()

    # Procesar usos de suelo
    usos_activos = [capa for capa in imagenes_activas 
                   if hasattr(capa, 'leyenda_compartida') 
                   and capa.leyenda_compartida == "usos_suelo"]
    if usos_activos:
        titulo = " & ".join(capa.titulo_leyenda for capa in usos_activos)
        elementos.append({'tipo': 'titulo', 'texto': titulo})
        elementos.extend([{
            'tipo': 'item',
            'texto': elem['nombre'],
            'color': elem['color'],
            'simbolo': None
        } for elem in leyenda_comun])
        leyendas_ya_agregadas.add("usos_suelo")

    # Procesar SEIA
    seia_activos = [capa for capa in imagenes_activas 
                   if hasattr(capa, 'leyenda_compartida') 
                   and capa.leyenda_compartida == "seia"]
    if seia_activos:
        elementos.append({'tipo': 'titulo', 'texto': "Tamaño de inversión (SEIA)"})
        elementos.extend([{
            'tipo': 'item',
            'texto': elem['nombre'],
            'color': elem['color'],
            'simbolo': elem['simbolo']
        } for elem in leyenda_comun_seia])
        leyendas_ya_agregadas.add("seia")

    # Otras capas
    for capa in imagenes_activas:
        if hasattr(capa, 'leyenda_compartida') and capa.leyenda_compartida in leyendas_ya_agregadas:
            continue
        if getattr(capa, 'leyenda', None):
            if capa.titulo_leyenda:
                elementos.append({'tipo': 'titulo', 'texto': capa.titulo_leyenda})
            for elem in capa.leyenda:
                elementos.append({
                    'tipo': 'item',
                    'texto': elem['nombre'],
                    'color': elem['color'],
                    'simbolo': elem.get('simbolo', None)
                })
        elif not hasattr(capa, 'leyenda_compartida'):
            elementos.append({
                'tipo': 'item',
                'texto': capa.nombre,
                'color': capa.color,
                'simbolo': None
            })

    # Determinar el mejor tamaño de fuente y número de columnas
    tam_fuentes = [16, 14, 12]  # Tamaños de fuente a probar
    separacion_entre_columnas = 30
    tam_fuente = 16
    num_columnas = 1
    esp_linea = 20
    tam_simbolo = 16
    
    # Calcular altura máxima permitida
    altura_maxima_permitida = contenido_alto
    
    # Intentar con diferentes tamaños de fuente
    for tam_fuente_intento in tam_fuentes:
        # Configurar fuentes con este tamaño
        fuente = pygame.font.SysFont("Arial", tam_fuente_intento)
        fuente_titulo = pygame.font.SysFont("Arial", tam_fuente_intento, bold=True)
        
        # Calcular espacio por línea y tamaño de símbolo proporcional
        esp_linea_intento = int(tam_fuente_intento * 1.25)
        tam_simbolo_intento = tam_fuente_intento
        
        # Función para dividir elementos en columnas según la altura disponible
        def dividir_en_columnas(elementos, max_altura, max_cols=3):
            columnas = [[]]
            altura_actual = 0
            max_lineas = max_altura // esp_linea_intento
            
            for elemento in elementos:
                # Calcular altura requerida para este elemento
                lineas_requeridas = 1.4 if elemento['tipo'] == 'titulo' else 1.0
                
                # Si excede la altura, intentar crear nueva columna
                if altura_actual + lineas_requeridas > max_lineas:
                    if len(columnas) < max_cols:
                        columnas.append([])
                        altura_actual = 0
                    else:
                        # Si ya tenemos el máximo de columnas, salir
                        return None
                        
                columnas[-1].append(elemento)
                altura_actual += lineas_requeridas
                
            return columnas

        # Intentar con diferentes números de columnas
        for cols in range(3, 0, -1):
            columnas = dividir_en_columnas(elementos, contenido_alto, max_cols=cols)
            if columnas is not None:
                # Verificar si todas las columnas caben en altura
                altura_maxima_columna = 0
                for col in columnas:
                    altura_col = 0
                    for elemento in col:
                        altura_col += esp_linea_intento * (1.4 if elemento['tipo'] == 'titulo' else 1.0)
                    if altura_col > altura_maxima_columna:
                        altura_maxima_columna = altura_col
                
                if altura_maxima_columna <= altura_maxima_permitida:
                    tam_fuente = tam_fuente_intento
                    esp_linea = esp_linea_intento
                    tam_simbolo = tam_simbolo_intento
                    num_columnas = len(columnas)
                    break
            if num_columnas > 1:
                break
        else:
            continue
        break
    
    # Configurar fuentes con el tamaño seleccionado
    fuente = pygame.font.SysFont("Arial", tam_fuente)
    fuente_titulo = pygame.font.SysFont("Arial", tam_fuente, bold=True)
    
    # Volver a dividir elementos con los parámetros seleccionados
    def dividir_en_columnas_final(elementos, max_altura, max_cols=3):
        columnas = [[]]
        altura_actual = 0
        max_lineas = max_altura // esp_linea
        
        for elemento in elementos:
            # Calcular altura requerida para este elemento
            lineas_requeridas = 1.4 if elemento['tipo'] == 'titulo' else 1.0
            
            # Si excede la altura, crear nueva columna
            if altura_actual + lineas_requeridas > max_lineas and len(columnas) < max_cols:
                columnas.append([])
                altura_actual = 0
                
            columnas[-1].append(elemento)
            altura_actual += lineas_requeridas
            
        return columnas

    columnas = dividir_en_columnas_final(elementos, contenido_alto, max_cols=num_columnas)
    num_columnas = len(columnas)
    
    # Calcular ancho de columna
    ancho_col = (contenido_ancho - separacion_entre_columnas * (num_columnas - 1)) // num_columnas if num_columnas > 0 else contenido_ancho
    
    # Dibujar cada columna
    y_inicial = margen_vertical_px + 15
    for idx_col, columna in enumerate(columnas):
        x_col = margen_lateral_px + idx_col * (ancho_col + separacion_entre_columnas)
        y_actual = y_inicial
        
        for elemento in columna:
            if elemento['tipo'] == 'titulo':
                texto = fuente_titulo.render(elemento['texto'], True, (255, 255, 255))
                leyenda_surface.blit(texto, (x_col, y_actual))
                y_actual += int(esp_linea * 1.4)
            else:
                rect_simbolo = (x_col, y_actual, tam_simbolo, tam_simbolo)
                color = pygame.Color(elemento['color'])
                simbolo = elemento.get('simbolo', None)
                centro = (x_col + tam_simbolo//2, y_actual + tam_simbolo//2)
                
                # Dibujar símbolo según el tipo
                if simbolo == "circulo_5":
                    pygame.draw.circle(leyenda_surface, color, centro, 5, 1)
                elif simbolo == "circulo_15":
                    pygame.draw.circle(leyenda_surface, color, centro, 15, 1)
                elif simbolo == "circulo_20":
                    pygame.draw.circle(leyenda_surface, color, centro, 20, 1)
                elif simbolo == "circulo_20_relleno":
                    pygame.draw.circle(leyenda_surface, color, centro, 20)
                elif simbolo == "circulo_fijo_15_borde":
                    pygame.draw.circle(leyenda_surface, color, centro, 15, 2)
                elif simbolo == "circulo_doble_punteado":
                    dibujar_circulo_punteado(leyenda_surface, color, centro, 15, 2)
                    pygame.draw.circle(leyenda_surface, color, centro, 6)
                elif simbolo == "diagonal_x":
                    dibujar_simbolo_diagonal(leyenda_surface, color, rect_simbolo)
                elif simbolo == "diamond_red_dot":
                    dibujar_simbolo_diamante(leyenda_surface, color, rect_simbolo)
                elif simbolo == "linea_solida":
                    dibujar_linea_solida(leyenda_surface, color, rect_simbolo)
                elif simbolo == "linea_punteada":
                    dibujar_linea_punteada(leyenda_surface, color, rect_simbolo)
                elif simbolo == "punto_circulo":
                    dibujar_punto_circulo(leyenda_surface, color, rect_simbolo)
                elif simbolo == "limite_predial":
                    dibujar_limite_predial(leyenda_surface, color, rect_simbolo)
                elif simbolo == "incendio":
                    dibujar_simbolo_incendios(leyenda_surface, color, rect_simbolo)
                elif simbolo == "cuadrado_relleno":
                    pygame.draw.rect(leyenda_surface, color, rect_simbolo)
                elif simbolo == "triangulo_8":
                    dibujar_triangulo(leyenda_surface, color, rect_simbolo)
                elif simbolo == "cruz":
                    dibujar_cruz(leyenda_surface, color, rect_simbolo)
                elif simbolo == "cruz_con_circulo":
                    dibujar_cruz_con_circulo(leyenda_surface, color, rect_simbolo)
                elif simbolo == "circulo_doble":
                    dibujar_circulo_doble(leyenda_surface, color, rect_simbolo)
                elif simbolo == "linea_2px":
                    dibujar_linea_2px(leyenda_surface, color, rect_simbolo)
                elif simbolo == "circulo_doble_relleno":
                    dibujar_circulo_doble_relleno(leyenda_surface, color, rect_simbolo)
                # Nuevo símbolo para patrimonio geológico
                elif simbolo == "circulo_doble_borde":
                    dibujar_circulo_doble_borde(leyenda_surface, color, rect_simbolo)
                elif simbolo and simbolo.startswith("circulo_"):
                    if "_relleno" in simbolo:
                        partes = simbolo.split("_")
                        radio = int(partes[1])
                        pygame.draw.circle(leyenda_surface, color, centro, radio)
                    else:
                        try:
                            radio = int(simbolo.split("_")[1])
                            pygame.draw.circle(leyenda_surface, color, centro, radio, 1)
                        except ValueError:
                            pygame.draw.rect(leyenda_surface, color, rect_simbolo)
                else:
                    pygame.draw.rect(leyenda_surface, color, rect_simbolo)

                # Dibujar texto
                texto = fuente.render(elemento['texto'], True, (255, 255, 255))
                texto_y = y_actual + (tam_simbolo - texto.get_height()) // 2
                leyenda_surface.blit(texto, (x_col + tam_simbolo + 5, texto_y))
                y_actual += esp_linea

    # Dibujar la superficie de la leyenda
    pantalla.blit(leyenda_surface, (leyenda_x, leyenda_y))

# ===============================================================================
# BUCLE PRINCIPAL
# ===============================================================================
orden_activacion = 0
running = True

# Crear un diccionario para rastrear el estado de los sonidos de teclas
estado_sonidos_teclas = {tecla: False for tecla in teclas_sonidos.keys()}

logger.info("Inicio de sesión")

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            logger.info("Fin de sesión")
            running = False
            
        # Manejo de joysticks
        elif event.type == pygame.JOYBUTTONDOWN:
            joystick_id = event.instance_id
            button = event.button
            
            # Buscar el joystick que generó el evento
            for i, joy in enumerate(joysticks):
                if joy.get_instance_id() == joystick_id:
                    jugador = i + 1  # Jugadores 1,2,3
                    break
            else:
                continue
                
            # Calcular clave
            clave = (jugador, button)
            if clave in mapeo_capas:
                capas = mapeo_capas[clave]
                for capa in capas:
                    estado_anterior = capa.activa
                    
                    # Manejo especial para reinicio
                    if capa.es_reinicio:
                        logger.info(f"Jugador {jugador} botón {button}: REINICIO")
                        log_evento_csv(jugador, button, "reinicio", capa.nombre)
                        
                        # Desactivar todas las capas excepto reinicio
                        for c in imagenes_con_fade:
                            if not c.es_reinicio and c.activa:
                                log_evento_csv(jugador, button, "desactivar", c.nombre)
                                c.activa = False
                        # Activar capa de reinicio
                        if not capa.activa:
                            log_evento_csv(jugador, button, "activar", capa.nombre)
                        capa.activa = True
                        capa.orden = orden_activacion + 1
                    else:
                        # Desactivar pantalla de reinicio si se activa otra capa
                        if imagen_reinicio and imagen_reinicio.activa:
                            logger.info("Desactivando pantalla de reinicio")
                            log_evento_csv(jugador, button, "desactivar", imagen_reinicio.nombre)
                            imagen_reinicio.activa = False
                            
                        # Toggle de la capa normal
                        if not capa.activa:
                            orden_activacion += 1
                            capa.orden = orden_activacion
                            logger.info(f"Jugador {jugador} botón {button}: ACTIVAR {capa.nombre}")
                            log_evento_csv(jugador, button, "activar", capa.nombre)
                        else:
                            logger.info(f"Jugador {jugador} botón {button}: DESACTIVAR {capa.nombre}")
                            log_evento_csv(jugador, button, "desactivar", capa.nombre)
                        capa.activa = not capa.activa
            else:
                logger.warning(f"Botón no asignado: Jugador {jugador}, Botón {button}")

        # Manejo de teclado para sonidos
        elif event.type == pygame.KEYDOWN:
            # Salir con Shift+ESC
            if event.key == pygame.K_ESCAPE and pygame.key.get_mods() & pygame.KMOD_SHIFT:
                logger.info("Fin de sesión (Shift+ESC)")
                running = False
            
            # Reproducir/detener sonidos de teclas
            elif event.key in sonidos_teclas and sonidos_teclas[event.key]:
                if estado_sonidos_teclas[event.key]:
                    # Si el sonido está activo, detenerlo
                    sonidos_teclas[event.key].stop()
                    estado_sonidos_teclas[event.key] = False
                    logger.info(f"Deteniendo sonido de tecla: {event.key}")
                else:
                    # Si el sonido no está activo, reproducirlo
                    sonidos_teclas[event.key].play()
                    estado_sonidos_teclas[event.key] = True
                    logger.info(f"Reproduciendo sonido de tecla: {event.key}")

    # Limpiar pantalla
    screen.fill((0, 0, 0))
    
    # Dibujar imagen base
    screen.blit(imagen_base, (0, 0))

    # Obtener capas activas
    imagenes_activas = sorted(
        [capa for capa in imagenes_con_fade if (capa.activa or capa.alpha > 0)],
        key=lambda x: x.orden
    )

    # Actualizar y dibujar capas
    for capa in imagenes_activas:
        if capa.activa:
            capa.fade_in()
        else:
            capa.fade_out()
        capa.dibujar(screen)

    # Dibujar leyenda en el tercer monitor
    if not (imagen_reinicio and imagen_reinicio.activa):
        dibujar_leyenda_tercer_monitor(screen, [c for c in imagenes_activas if not c.es_reinicio])

    pygame.display.flip()
    pygame.time.delay(30)

# Finalización
logger.info("Sesión finalizada")
pygame.quit()
sys.exit()
import pygame
import sys
import random
import json
import os
from pygame.locals import *

# Inicializar Pygame
pygame.init()

# Configuración de la pantalla
ANCHO, ALTO = 800, 600
pantalla = pygame.display.set_mode((ANCHO, ALTO))
pygame.display.set_caption("El Ahorcado")

# Colores
BLANCO = (255, 255, 255)
NEGRO = (0, 0, 0)
AZUL = (0, 0, 255)
ROJO = (255, 0, 0)
VERDE = (0, 255, 0)
GRIS = (200, 200, 200)

# Fuentes
fuente_grande = pygame.font.SysFont('Arial', 48)
fuente_mediana = pygame.font.SysFont('Arial', 32)
fuente_pequena = pygame.font.SysFont('Arial', 24)

# Lista de palabras para el juego
palabras = [
    "PYTHON", "PROGRAMACION", "JUEGO", "AHORCADO", "COMPUTADORA",
    "ALGORITMO", "VARIABLE", "FUNCION", "LISTA", "DICCIONARIO",
    "PYGAME", "INTERFAZ", "DESARROLLO", "CODIGO", "DEBUGGING"
]

# Datos del juego
class JuegoAhorcado:
    def __init__(self):
        self.palabra = ""
        self.palabra_oculta = []
        self.letras_adivinadas = []
        self.letras_incorrectas = []
        self.intentos_maximos = 6
        self.intentos = 0
        self.puntaje = 0
        self.jugador = ""
        self.estado = "menu"  # menu, jugando, game_over, victoria

    def nuevo_juego(self, jugador=""):
        self.palabra = random.choice(palabras).upper()
        self.palabra_oculta = ["_" if letra.isalpha() else letra for letra in self.palabra]
        self.letras_adivinadas = []
        self.letras_incorrectas = []
        self.intentos = 0
        self.puntaje = 0
        self.jugador = jugador if jugador else "Jugador"
        self.estado = "jugando"

    def adivinar_letra(self, letra):
        letra = letra.upper()
        if letra in self.letras_adivinadas or letra in self.letras_incorrectas:
            return False
        
        if letra in self.palabra:
            self.letras_adivinadas.append(letra)
            # Actualizar palabra oculta
            for i, char in enumerate(self.palabra):
                if char == letra:
                    self.palabra_oculta[i] = letra
            # Calcular puntaje
            self.puntaje += 10
            return True
        else:
            self.letras_incorrectas.append(letra)
            self.intentos += 1
            return False

    def verificar_victoria(self):
        return "_" not in self.palabra_oculta

    def verificar_derrota(self):
        return self.intentos >= self.intentos_maximos

    def guardar_partida(self):
        datos = {
            "palabra": self.palabra,
            "palabra_oculta": self.palabra_oculta,
            "letras_adivinadas": self.letras_adivinadas,
            "letras_incorrectas": self.letras_incorrectas,
            "intentos": self.intentos,
            "puntaje": self.puntaje,
            "jugador": self.jugador
        }
        with open("partida_guardada.json", "w") as archivo:
            json.dump(datos, archivo)

    def cargar_partida(self):
        try:
            with open("partida_guardada.json", "r") as archivo:
                datos = json.load(archivo)
            self.palabra = datos["palabra"]
            self.palabra_oculta = datos["palabra_oculta"]
            self.letras_adivinadas = datos["letras_adivinadas"]
            self.letras_incorrectas = datos["letras_incorrectas"]
            self.intentos = datos["intentos"]
            self.puntaje = datos["puntaje"]
            self.jugador = datos["jugador"]
            self.estado = "jugando"
            return True
        except:
            return False

    def guardar_puntaje(self):
        try:
            with open("clasificaciones.json", "r") as archivo:
                clasificaciones = json.load(archivo)
        except:
            clasificaciones = []
        
        clasificaciones.append({
            "jugador": self.jugador,
            "puntaje": self.puntaje,
            "palabra": self.palabra
        })
        
        # Ordenar por puntaje (mayor a menor)
        clasificaciones.sort(key=lambda x: x["puntaje"], reverse=True)
        
        with open("clasificaciones.json", "w") as archivo:
            json.dump(clasificaciones[:10], archivo)  # Guardar solo top 10

# Funciones de dibujo
def dibujar_menu(juego):
    pantalla.fill(BLANCO)
    
    # Título
    titulo = fuente_grande.render("EL AHORCADO", True, AZUL)
    pantalla.blit(titulo, (ANCHO//2 - titulo.get_width()//2, 100))
    
    # Botones del menú
    botones = [
        ("NUEVO JUEGO", 200),
        ("CARGAR JUEGO", 270),
        ("TABLA DE CLASIFICACIONES", 340),
        ("SALIR", 410)
    ]
    
    for texto, y in botones:
        pygame.draw.rect(pantalla, GRIS, (ANCHO//2 - 150, y, 300, 50))
        texto_boton = fuente_mediana.render(texto, True, NEGRO)
        pantalla.blit(texto_boton, (ANCHO//2 - texto_boton.get_width()//2, y + 10))
    
    pygame.display.flip()

def dibujar_juego(juego):
    pantalla.fill(BLANCO)
    
    # Información del jugador
    info_jugador = fuente_pequena.render(f"Jugador: {juego.jugador} | Puntaje: {juego.puntaje}", True, NEGRO)
    pantalla.blit(info_jugador, (20, 20))
    
    # Dibujar el ahorcado
    dibujar_ahorcado(juego.intentos)
    
    # Palabra oculta
    palabra_texto = " ".join(juego.palabra_oculta)
    texto_palabra = fuente_mediana.render(palabra_texto, True, NEGRO)
    pantalla.blit(texto_palabra, (ANCHO//2 - texto_palabra.get_width()//2, 400))
    
    # Letras incorrectas
    if juego.letras_incorrectas:
        letras_texto = fuente_pequena.render(f"Letras incorrectas: {', '.join(juego.letras_incorrectas)}", True, ROJO)
        pantalla.blit(letras_texto, (ANCHO//2 - letras_texto.get_width()//2, 450))
    
    # Intentos restantes
    intentos_texto = fuente_pequena.render(f"Intentos restantes: {juego.intentos_maximos - juego.intentos}", True, NEGRO)
    pantalla.blit(intentos_texto, (ANCHO//2 - intentos_texto.get_width()//2, 480))
    
    # Botón de guardar
    pygame.draw.rect(pantalla, VERDE, (ANCHO - 120, 20, 100, 40))
    guardar_texto = fuente_pequena.render("GUARDAR", True, BLANCO)
    pantalla.blit(guardar_texto, (ANCHO - 120 + 50 - guardar_texto.get_width()//2, 30))
    
    pygame.display.flip()

def dibujar_ahorcado(intentos):
    # Base
    pygame.draw.line(pantalla, NEGRO, (100, 500), (300, 500), 5)
    # Poste vertical
    pygame.draw.line(pantalla, NEGRO, (200, 500), (200, 100), 5)
    # Poste horizontal
    pygame.draw.line(pantalla, NEGRO, (200, 100), (350, 100), 5)
    # Cuerda
    pygame.draw.line(pantalla, NEGRO, (350, 100), (350, 150), 5)
    
    if intentos >= 1:  # Cabeza
        pygame.draw.circle(pantalla, NEGRO, (350, 180), 30, 2)
    if intentos >= 2:  # Cuerpo
        pygame.draw.line(pantalla, NEGRO, (350, 210), (350, 320), 2)
    if intentos >= 3:  # Brazo izquierdo
        pygame.draw.line(pantalla, NEGRO, (350, 230), (320, 280), 2)
    if intentos >= 4:  # Brazo derecho
        pygame.draw.line(pantalla, NEGRO, (350, 230), (380, 280), 2)
    if intentos >= 5:  # Pierna izquierda
        pygame.draw.line(pantalla, NEGRO, (350, 320), (320, 380), 2)
    if intentos >= 6:  # Pierna derecha
        pygame.draw.line(pantalla, NEGRO, (350, 320), (380, 380), 2)

def dibujar_game_over(juego, victoria=False):
    pantalla.fill(BLANCO)
    
    if victoria:
        mensaje = "¡VICTORIA!"
        color = VERDE
        mensaje_puntaje = f"Puntaje final: {juego.puntaje + 50}"  # Bonus por victoria
    else:
        mensaje = "GAME OVER"
        color = ROJO
        mensaje_puntaje = f"La palabra era: {juego.palabra}"
    
    texto_mensaje = fuente_grande.render(mensaje, True, color)
    pantalla.blit(texto_mensaje, (ANCHO//2 - texto_mensaje.get_width()//2, 200))
    
    texto_puntaje = fuente_mediana.render(mensaje_puntaje, True, NEGRO)
    pantalla.blit(texto_puntaje, (ANCHO//2 - texto_puntaje.get_width()//2, 280))
    
    # Botones
    pygame.draw.rect(pantalla, AZUL, (ANCHO//2 - 150, 350, 300, 50))
    texto_reiniciar = fuente_mediana.render("VOLVER AL MENÚ", True, BLANCO)
    pantalla.blit(texto_reiniciar, (ANCHO//2 - texto_reiniciar.get_width()//2, 360))
    
    pygame.display.flip()

def dibujar_clasificaciones():
    pantalla.fill(BLANCO)
    
    titulo = fuente_grande.render("TABLA DE CLASIFICACIONES", True, AZUL)
    pantalla.blit(titulo, (ANCHO//2 - titulo.get_width()//2, 50))
    
    try:
        with open("clasificaciones.json", "r") as archivo:
            clasificaciones = json.load(archivo)
    except:
        clasificaciones = []
    
    if not clasificaciones:
        texto_vacio = fuente_mediana.render("No hay puntuaciones guardadas", True, NEGRO)
        pantalla.blit(texto_vacio, (ANCHO//2 - texto_vacio.get_width()//2, 200))
    else:
        for i, registro in enumerate(clasificaciones[:10]):  # Mostrar top 10
            texto = f"{i+1}. {registro['jugador']} - {registro['puntaje']} pts - {registro['palabra']}"
            texto_render = fuente_pequena.render(texto, True, NEGRO)
            pantalla.blit(texto_render, (ANCHO//2 - 250, 120 + i * 40))
    
    # Botón volver
    pygame.draw.rect(pantalla, ROJO, (ANCHO//2 - 100, 500, 200, 50))
    texto_volver = fuente_mediana.render("VOLVER", True, BLANCO)
    pantalla.blit(texto_volver, (ANCHO//2 - texto_volver.get_width()//2, 510))
    
    pygame.display.flip()

def obtener_nombre_jugador():
    nombre = ""
    activo = True
    
    while activo:
        pantalla.fill(BLANCO)
        
        texto = fuente_mediana.render("Ingresa tu nombre:", True, NEGRO)
        pantalla.blit(texto, (ANCHO//2 - texto.get_width()//2, 200))
        
        nombre_texto = fuente_mediana.render(nombre + "|", True, AZUL)
        pantalla.blit(nombre_texto, (ANCHO//2 - nombre_texto.get_width()//2, 250))
        
        pygame.draw.rect(pantalla, VERDE, (ANCHO//2 - 100, 320, 200, 50))
        texto_empezar = fuente_mediana.render("EMPEZAR", True, BLANCO)
        pantalla.blit(texto_empezar, (ANCHO//2 - texto_empezar.get_width()//2, 330))
        
        for evento in pygame.event.get():
            if evento.type == QUIT:
                pygame.quit()
                sys.exit()
            elif evento.type == KEYDOWN:
                if evento.key == K_RETURN and nombre:
                    activo = False
                elif evento.key == K_BACKSPACE:
                    nombre = nombre[:-1]
                elif evento.key == K_ESCAPE:
                    return None
                elif len(nombre) < 15 and evento.unicode.isalnum():
                    nombre += evento.unicode
            elif evento.type == MOUSEBUTTONDOWN:
                if ANCHO//2 - 100 <= evento.pos[0] <= ANCHO//2 + 100 and 320 <= evento.pos[1] <= 370:
                    if nombre:
                        activo = False
        
        pygame.display.flip()
    
    return nombre

# Función principal
def main():
    juego = JuegoAhorcado()
    reloj = pygame.time.Clock()
    
    while True:
        for evento in pygame.event.get():
            if evento.type == QUIT:
                pygame.quit()
                sys.exit()
            
            if juego.estado == "menu":
                if evento.type == MOUSEBUTTONDOWN:
                    x, y = evento.pos
                    
                    # Nuevo juego
                    if ANCHO//2 - 150 <= x <= ANCHO//2 + 150 and 200 <= y <= 250:
                        nombre = obtener_nombre_jugador()
                        if nombre:
                            juego.nuevo_juego(nombre)
                    
                    # Cargar juego
                    elif ANCHO//2 - 150 <= x <= ANCHO//2 + 150 and 270 <= y <= 320:
                        if juego.cargar_partida():
                            juego.estado = "jugando"
                    
                    # Clasificaciones
                    elif ANCHO//2 - 150 <= x <= ANCHO//2 + 150 and 340 <= y <= 390:
                        juego.estado = "clasificaciones"
                    
                    # Salir
                    elif ANCHO//2 - 150 <= x <= ANCHO//2 + 150 and 410 <= y <= 460:
                        pygame.quit()
                        sys.exit()
            
            elif juego.estado == "jugando":
                if evento.type == KEYDOWN:
                    if evento.key == K_ESCAPE:
                        juego.estado = "menu"
                    elif evento.unicode.isalpha() and len(evento.unicode) == 1:
                        juego.adivinar_letra(evento.unicode)
                        
                        # Verificar estado del juego
                        if juego.verificar_victoria():
                            juego.puntaje += 50  # Bonus por victoria
                            juego.guardar_puntaje()
                            juego.estado = "victoria"
                        elif juego.verificar_derrota():
                            juego.estado = "game_over"
                
                elif evento.type == MOUSEBUTTONDOWN:
                    x, y = evento.pos
                    # Botón guardar
                    if ANCHO - 120 <= x <= ANCHO - 20 and 20 <= y <= 60:
                        juego.guardar_partida()
            
            elif juego.estado in ["victoria", "game_over"]:
                if evento.type == MOUSEBUTTONDOWN:
                    x, y = evento.pos
                    if ANCHO//2 - 150 <= x <= ANCHO//2 + 150 and 350 <= y <= 400:
                        juego.estado = "menu"
            
            elif juego.estado == "clasificaciones":
                if evento.type == MOUSEBUTTONDOWN:
                    x, y = evento.pos
                    if ANCHO//2 - 100 <= x <= ANCHO//2 + 100 and 500 <= y <= 550:
                        juego.estado = "menu"
        
        # Dibujar según el estado actual
        if juego.estado == "menu":
            dibujar_menu(juego)
        elif juego.estado == "jugando":
            dibujar_juego(juego)
        elif juego.estado in ["victoria", "game_over"]:
            dibujar_game_over(juego, juego.estado == "victoria")
        elif juego.estado == "clasificaciones":
            dibujar_clasificaciones()
        
        reloj.tick(60)

if __name__ == "__main__":
    main()
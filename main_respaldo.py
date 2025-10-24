import pygame
import sys
import random 
from pygame.locals import *
from variables_constantes import *
from PIL import Image
from conexion.cliente import usuarios_collection, db
from pymongo.errors import ConnectionFailure
from componentes.boton_clase import Boton
from componentes.input_box import InputBox

pygame.init()

pantalla = pygame.display.set_mode((ANCHO_PANTALLA, ALTO_PANTALLA))
pygame.display.set_caption('Ahorcado')

try:
    preguntas_palabras_collection = db["preguntas_palabras"]
except Exception as e:
    print(f"Error al conectar con la colección 'preguntas_palabras': {e}")
    preguntas_palabras_collection = None

try:
    fondo = pygame.image.load('imagenes/BACKGROUND.png')
    fondo = pygame.transform.scale(fondo, (ANCHO_PANTALLA, ALTO_PANTALLA))
except pygame.error as e:
    print(f"Error: No se pudo cargar la imagen de fondo. Detalle: {e}")
    fondo = None

BTN_MENU_ANCHO = 220
BTN_MENU_ALTO = 65
GRID_MARGEN_H = 40 
GRID_MARGEN_V = 30 
grid_total_ancho = (BTN_MENU_ANCHO * 2) + GRID_MARGEN_H
grid_start_x = (ANCHO_PANTALLA - grid_total_ancho) // 2
grid_start_y = 220 

BTN_FORM_ANCHO = 150
BTN_FORM_ALTO = 50

BTN_NAV_ANCHO = 140
BTN_NAV_ALTO = 50

BTN_GAME_ANCHO = 200
BTN_GAME_ALTO = 50

SCROLL_SPEED = 30

PANEL_COLOR = (240, 240, 240, 220) 
PANEL_BORDER_RADIUS = 15

PANEL_REGISTRO_RECT = pygame.Rect(ANCHO_PANTALLA // 2 - 200, 80, 400, 450)
PANEL_LOAD_RECT = pygame.Rect(ANCHO_PANTALLA // 2 - 200, 80, 400, 450)
PANEL_BOARD_RECT = pygame.Rect(ANCHO_PANTALLA // 2 - 275, 80, 550, 450)

VIEWPORT_LOAD_RECT = pygame.Rect(PANEL_LOAD_RECT.x + 20, PANEL_LOAD_RECT.y + 90, PANEL_LOAD_RECT.width - 40, PANEL_LOAD_RECT.height - 100)
VIEWPORT_BOARD_RECT = pygame.Rect(PANEL_BOARD_RECT.x + 20, PANEL_BOARD_RECT.y + 90, PANEL_BOARD_RECT.width - 40, PANEL_BOARD_RECT.height - 100)

try:
    img_btn_create_orig = pygame.image.load('imagenes/CREATE.png').convert_alpha()
    img_btn_load_orig = pygame.image.load('imagenes/LOAD.png').convert_alpha()
    img_btn_board_orig = pygame.image.load('imagenes/BOARD.png').convert_alpha()
    img_btn_exit_orig = pygame.image.load('imagenes/EXIT.png').convert_alpha()
    
    img_btn_regresar_orig = pygame.image.load('imagenes/BACK.png').convert_alpha()
    img_btn_guardar_orig = pygame.image.load('imagenes/SAVE.png').convert_alpha()
    img_btn_siguiente_orig = pygame.image.load('imagenes/NEXT.png').convert_alpha()
    img_btn_salir_menu_orig = pygame.image.load('imagenes/BACK.png').convert_alpha()

    img_btn_create = pygame.transform.scale(img_btn_create_orig, (BTN_MENU_ANCHO, BTN_MENU_ALTO))
    img_btn_load = pygame.transform.scale(img_btn_load_orig, (BTN_MENU_ANCHO, BTN_MENU_ALTO))
    img_btn_board = pygame.transform.scale(img_btn_board_orig, (BTN_MENU_ANCHO, BTN_MENU_ALTO))
    img_btn_exit = pygame.transform.scale(img_btn_exit_orig, (BTN_MENU_ANCHO, BTN_MENU_ALTO))

    img_btn_guardar = pygame.transform.scale(img_btn_guardar_orig, (BTN_FORM_ANCHO, BTN_FORM_ALTO))
    img_btn_siguiente = pygame.transform.scale(img_btn_siguiente_orig, (BTN_GAME_ANCHO, BTN_GAME_ALTO))
    img_btn_salir_menu = pygame.transform.scale(img_btn_salir_menu_orig, (BTN_GAME_ANCHO, BTN_GAME_ALTO))

    img_btn_regresar_nav = pygame.transform.scale(img_btn_regresar_orig, (BTN_NAV_ANCHO, BTN_NAV_ALTO))
    img_btn_regresar_form = pygame.transform.scale(img_btn_regresar_orig, (BTN_FORM_ANCHO, BTN_FORM_ALTO))


except pygame.error as e:
    print(f"¡ERROR! No se pudo cargar o escalar una imagen de botón: {e}")
    img_btn_create = img_btn_load = img_btn_board = img_btn_exit = None
    img_btn_regresar_nav = img_btn_regresar_form = img_btn_guardar = None
    img_btn_siguiente = img_btn_salir_menu = None

if img_btn_create: 
    rect_btn_create = img_btn_create.get_rect(topleft=(grid_start_x, grid_start_y))
    rect_btn_load = img_btn_load.get_rect(topleft=(grid_start_x + BTN_MENU_ANCHO + GRID_MARGEN_H, grid_start_y))
    y_fila_2 = grid_start_y + BTN_MENU_ALTO + GRID_MARGEN_V
    rect_btn_board = img_btn_board.get_rect(topleft=(grid_start_x, y_fila_2))
    rect_btn_exit = img_btn_exit.get_rect(topleft=(grid_start_x + BTN_MENU_ANCHO + GRID_MARGEN_H, y_fila_2))
else:
    rect_btn_create = rect_btn_load = rect_btn_board = rect_btn_exit = pygame.Rect(0,0,0,0)

if img_btn_regresar_nav and img_btn_regresar_form:
    x_nav = (ANCHO_PANTALLA - BTN_NAV_ANCHO) // 2
    y_nav = ALTO_PANTALLA - BTN_NAV_ALTO - MARGEN
    rect_btn_regresar_puntuaciones = img_btn_regresar_nav.get_rect(topleft=(x_nav, y_nav))
    
    rect_btn_regresar_cargar = img_btn_regresar_nav.get_rect(topleft=(x_nav, y_nav))

    x_form_reg = (ANCHO_PANTALLA - BTN_FORM_ANCHO) // 2
    rect_btn_regresar_registro = img_btn_regresar_form.get_rect(topleft=(x_form_reg, 470))
else:
    rect_btn_regresar_puntuaciones = rect_btn_regresar_cargar = rect_btn_regresar_registro = pygame.Rect(0,0,0,0)

if img_btn_guardar:
    x_form_guardar = (ANCHO_PANTALLA - BTN_FORM_ANCHO) // 2
    rect_btn_guardar_usuario = img_btn_guardar.get_rect(topleft=(x_form_guardar, 400))
else:
    rect_btn_guardar_usuario = pygame.Rect(0,0,0,0)

if img_btn_siguiente:
    x_game = (ANCHO_PANTALLA - BTN_GAME_ANCHO) // 2
    rect_btn_siguiente_palabra = img_btn_siguiente.get_rect(topleft=(x_game, ALTO_PANTALLA - 150))
else:
    rect_btn_siguiente_palabra = pygame.Rect(0,0,0,0)
    
if img_btn_salir_menu:
    x_game = (ANCHO_PANTALLA - BTN_GAME_ANCHO) // 2
    rect_btn_terminar_juego = img_btn_salir_menu.get_rect(topleft=(x_game, ALTO_PANTALLA - 80))
else:
    rect_btn_terminar_juego = pygame.Rect(0,0,0,0)


botones_usuarios = [] 
usuario_actual = None
imagen_inicio = pygame.image.load('imagenes/boton_NU.png').convert_alpha() 

input_username = InputBox(
    x=ANCHO_PANTALLA // 2 - 160,
    y=300,
    w=300,
    h=40,
    texto=''
)

estado_actual = ESTADO_MENU
lista_palabras_juego = []
indice_palabra_actual = 0
palabra_actual = ""
pista_actual = ""
letras_adivinadas = []
letras_incorrectas = []
intentos_globales_restantes = MAX_INTENTOS_TOTALES
puntuacion_sesion = 0
estado_partida = "JUGANDO"

scroll_y_load_user = 0
scroll_y_leaderboard = 0
max_scroll_load = 0
max_scroll_board = 0
content_surface_load_user = None
content_surface_leaderboard = None
lista_puntuaciones_cache = [] 


def cargar_palabras():
    if preguntas_palabras_collection is None:
        print("No se puede conectar a la colección de palabras.")
        return [{"palabra": "PYTHON", "pista": "Lenguaje de programación"}]
    
    palabras_validas = []
    try:
        documentos_db = list(preguntas_palabras_collection.find({}))
        
        if not documentos_db:
            print("ADVERTENCIA: La colección 'preguntas_palabras' está vacía.")
            return [{"palabra": "ERROR", "pista": "Base de datos vacía"}]

        for doc in documentos_db:
            if "respuesta" in doc and "pregunta" in doc:
                palabras_validas.append({
                    "palabra": doc["respuesta"], 
                    "pista": doc["pregunta"]      
                })
            else:
                print(f"ADVERTENCIA: Documento omitido por formato incorrecto (ID: {doc.get('_id', 'N/A')}). Faltan 'respuesta' o 'pregunta'.")      
        if not palabras_validas:
            print("Error: No se encontraron palabras válidas (con 'respuesta' y 'pregunta') en la base de datos.")
            return [{"palabra": "PYTHON", "pista": "Lenguaje de programación"}] 
            
        random.shuffle(palabras_validas)
        return palabras_validas
        
    except Exception as e:
        print(f"Error al cargar palabras: {e}")
        return [{"palabra": "PYTHON", "pista": "Lenguaje de programación"}]

def guardar_puntuacion(username, nueva_puntuacion):
    if usuarios_collection is None:
        print("Error: No hay conexión a la DB de usuarios.")
        return
    if nueva_puntuacion == 0:
        print("Puntuación 0, no se guarda.")
        return 

    try:
        usuario_doc = usuarios_collection.find_one({"nombre": username})
        if usuario_doc:
            puntuacion_actual_max = usuario_doc.get("puntuacion_maxima", 0)
            
            if nueva_puntuacion > puntuacion_actual_max:
                usuarios_collection.update_one(
                    {"nombre": username},
                    {"$set": {"puntuacion_maxima": nueva_puntuacion}}
                )
                print(f"¡Nuevo récord para {username}: {nueva_puntuacion}!")
            else:
                print(f"Puntuación de la sesión: {nueva_puntuacion}. Récord actual: {puntuacion_actual_max}.")
        else:
            print(f"Error: No se encontró al usuario {username} para guardar puntuación.")
    except Exception as e:
        print(f"Error al guardar puntuación: {e}")

def iniciar_nueva_ronda():
    global palabra_actual, pista_actual, letras_adivinadas, estado_partida, indice_palabra_actual
    
    if indice_palabra_actual < len(lista_palabras_juego):
        palabra_info = lista_palabras_juego[indice_palabra_actual]
        palabra_actual = palabra_info["palabra"].upper().strip() 
        pista_actual = palabra_info["pista"]
        letras_adivinadas = []
        estado_partida = "JUGANDO"
        indice_palabra_actual += 1
        return True 
    else:
        print("¡Has completado todas las palabras!")
        return False 

def iniciar_juego_completo():
    global lista_palabras_juego, indice_palabra_actual, puntuacion_sesion, estado_partida, intentos_globales_restantes, letras_incorrectas
    print(f"Iniciando juego para {usuario_actual}")
    lista_palabras_juego = cargar_palabras()
    indice_palabra_actual = 0
    puntuacion_sesion = 0
    intentos_globales_restantes = MAX_INTENTOS_TOTALES 
    letras_incorrectas = []
    estado_partida = "JUGANDO"
    iniciar_nueva_ronda() 

def wrap_text(text, font, color, max_width):
    palabras = text.split(' ')
    lineas_superficies = []
    linea_actual = ""
    
    for palabra in palabras:
        linea_prueba = linea_actual + palabra + " "
        
        if font.size(linea_prueba)[0] < max_width:
            linea_actual = linea_prueba
        else:
            superficie_linea = font.render(linea_actual.strip(), True, color)
            lineas_superficies.append(superficie_linea)
            linea_actual = palabra + " "
    
    superficie_linea = font.render(linea_actual.strip(), True, color)
    lineas_superficies.append(superficie_linea)
    
    return lineas_superficies

def dibujar_juego(pantalla):
    global estado_partida
    
    fuente_pista = pygame.font.Font(None, 34)
    fuente_palabra = pygame.font.Font(None, 60)
    fuente_letras = pygame.font.Font(None, 40)
    fuente_info = pygame.font.Font(None, 36)
    fuente_resultado = pygame.font.Font(None, 70)

    max_width_texto = ANCHO_PANTALLA - MARGEN * 4 

    texto_puntuacion = fuente_info.render(f"Puntuación: {puntuacion_sesion}", True, VERDE)
    pantalla.blit(texto_puntuacion, (MARGEN * 2, MARGEN * 2))

    texto_intentos = fuente_info.render(f"Intentos restantes: {intentos_globales_restantes}", True, NEGRO) 
    rect_intentos = texto_intentos.get_rect(topright=(ANCHO_PANTALLA - (MARGEN * 2), MARGEN * 2))
    pantalla.blit(texto_intentos, rect_intentos)

    y_actual = 110 

    texto_pista_titulo = fuente_info.render("PISTA:", True, NEGRO)
    rect_pista_titulo = texto_pista_titulo.get_rect(center=(ANCHO_PANTALLA // 2, y_actual))
    pantalla.blit(texto_pista_titulo, rect_pista_titulo)
    y_actual += 40 

    lineas_pista = wrap_text(pista_actual, fuente_pista, NEGRO, max_width_texto)
    for i, linea_surface in enumerate(lineas_pista):
        rect_linea = linea_surface.get_rect(center=(ANCHO_PANTALLA // 2, y_actual))
        pantalla.blit(linea_surface, rect_linea)
        y_actual += linea_surface.get_height() + 5
    
    y_actual += 40 

    palabra_mostrada = ""
    for letra in palabra_actual:
        if letra in letras_adivinadas:
            palabra_mostrada += letra + " "
        elif letra == " ": 
            palabra_mostrada += "  "
            if " " not in letras_adivinadas: 
                letras_adivinadas.append(" ")
        else:
            palabra_mostrada += "_ "
    
    texto_palabra = fuente_palabra.render(palabra_mostrada.strip(), True, NEGRO)
    rect_palabra = texto_palabra.get_rect(center=(ANCHO_PANTALLA // 2, y_actual))
    pantalla.blit(texto_palabra, rect_palabra)
    
    y_actual += 80 

    texto_incorrectas_titulo = fuente_info.render("Incorrectas:", True, ROJO)
    rect_incorrectas_titulo = texto_incorrectas_titulo.get_rect(center=(ANCHO_PANTALLA // 2, y_actual))
    pantalla.blit(texto_incorrectas_titulo, rect_incorrectas_titulo)
    y_actual += 40

    if letras_incorrectas:
        texto_incorrectas_str = " ".join(letras_incorrectas)
        lineas_incorrectas = wrap_text(texto_incorrectas_str, fuente_letras, ROJO, max_width_texto)
        
        for i, linea_surface in enumerate(lineas_incorrectas):
            rect_linea = linea_surface.get_rect(center=(ANCHO_PANTALLA // 2, y_actual))
            pantalla.blit(linea_surface, rect_linea)
            y_actual += linea_surface.get_height() + 5
    else:
        y_actual += 30 

    if img_btn_salir_menu:
        pantalla.blit(img_btn_salir_menu, rect_btn_terminar_juego)

    if estado_partida == "GANADA":
        texto_resultado = fuente_resultado.render("¡CORRECTO!", True, VERDE)
        rect_resultado = texto_resultado.get_rect(center=(ANCHO_PANTALLA // 2, rect_btn_siguiente_palabra.top - 50))
        pantalla.blit(texto_resultado, rect_resultado)
        
        if img_btn_siguiente:
            pantalla.blit(img_btn_siguiente, rect_btn_siguiente_palabra)
    
    elif estado_partida == "PERDIDA_GLOBAL": 
        texto_resultado = fuente_resultado.render("¡FIN DEL JUEGO!", True, ROJO)
        rect_resultado = texto_resultado.get_rect(center=(ANCHO_PANTALLA // 2, rect_btn_terminar_juego.top - 100))
        pantalla.blit(texto_resultado, rect_resultado)
        
        texto_score_final = fuente_letras.render(f"Palabras adivinadas: {puntuacion_sesion}", True, NEGRO)
        rect_score_final = texto_score_final.get_rect(center=(ANCHO_PANTALLA // 2, rect_btn_terminar_juego.top - 50))
        pantalla.blit(texto_score_final, rect_score_final)

running = True
while running:

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            if estado_actual == ESTADO_JUEGO and usuario_actual:
                guardar_puntuacion(usuario_actual, puntuacion_sesion)

        if event.type == pygame.MOUSEWHEEL:
            if estado_actual == ESTADO_CARGAR_USUARIO:
                scroll_y_load_user -= event.y * SCROLL_SPEED
                scroll_y_load_user = max(0, min(scroll_y_load_user, max_scroll_load))

            elif estado_actual == ESTADO_PUNTUACIONES:
                scroll_y_leaderboard -= event.y * SCROLL_SPEED
                scroll_y_leaderboard = max(0, min(scroll_y_leaderboard, max_scroll_board))

        if estado_actual == ESTADO_REGISTRO_USUARIO:
            input_username.handle_event(event)
        
        elif estado_actual == ESTADO_JUEGO and estado_partida == "JUGANDO":
            if event.type == pygame.KEYDOWN:
                if event.unicode.isalpha() and len(event.unicode) == 1: 
                    letra = event.unicode.upper()
                    if letra not in letras_adivinadas and letra not in letras_incorrectas:
                        if letra in palabra_actual:
                            letras_adivinadas.append(letra)
                            ganado = True
                            for l in palabra_actual:
                                if l != " " and l not in letras_adivinadas:
                                    ganado = False
                                    break
                            if ganado:
                                estado_partida = "GANADA"
                                puntuacion_sesion += 1
                                print("Palabra ganada!")
                        else:
                            letras_incorrectas.append(letra)
                            intentos_globales_restantes -= 1 
                            if intentos_globales_restantes <= 0:
                                estado_partida = "PERDIDA_GLOBAL" 
                                print(f"Juego terminado. Sin intentos. Puntuación: {puntuacion_sesion}")
                                guardar_puntuacion(usuario_actual, puntuacion_sesion)

        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                posicion_clic = event.pos

                if estado_actual == ESTADO_MENU:
                    
                    if rect_btn_create.collidepoint(posicion_clic):
                        estado_actual = ESTADO_REGISTRO_USUARIO
                        
                    elif rect_btn_load.collidepoint(posicion_clic):
                        estado_actual = ESTADO_CARGAR_USUARIO
                        botones_usuarios.clear()
                        scroll_y_load_user = 0 
                        
                        if usuarios_collection is None:
                            print("La conexión a la base de datos no está disponible.")
                            content_surface_load_user = None 
                        else:
                            try:
                                lista_usuarios_db = list(usuarios_collection.find({}, {"nombre": 1, "_id": 0}))
                                
                                if not lista_usuarios_db:
                                    print("No hay usuarios registrados.")
                                    content_surface_load_user = None
                                
                                alto_btn_usuario = 50
                                margen_btn_usuario = 15
                                ancho_btn_usuario = 300 
                                
                                total_height_load = max(
                                    len(lista_usuarios_db) * (alto_btn_usuario + margen_btn_usuario), 
                                    VIEWPORT_LOAD_RECT.height
                                )
                                content_surface_load_user = pygame.Surface((VIEWPORT_LOAD_RECT.width, total_height_load)).convert_alpha()
                                content_surface_load_user.fill((0,0,0,0)) 

                                max_scroll_load = content_surface_load_user.get_height() - VIEWPORT_LOAD_RECT.height
                                if max_scroll_load < 0: max_scroll_load = 0

                                for i, doc_usuario in enumerate(lista_usuarios_db):
                                    nombre_usuario = doc_usuario['nombre']
                                    
                                    x_pos = (VIEWPORT_LOAD_RECT.width - ancho_btn_usuario) // 2
                                    y_pos = (i * (alto_btn_usuario + margen_btn_usuario)) + (margen_btn_usuario // 2)
                                    
                                    nuevo_boton_usuario = Boton(
                                        x=x_pos,
                                        y=y_pos,
                                        ancho=ancho_btn_usuario,
                                        alto=alto_btn_usuario,
                                        color=AZUL,
                                        texto_str=nombre_usuario,
                                        color_texto=BLANCO
                                    )
                                    botones_usuarios.append(nuevo_boton_usuario)
                                    nuevo_boton_usuario.dibujar(content_surface_load_user) 
                                    
                            except ConnectionFailure as e:
                                print(f"ERROR DE CONEXIÓN: No se pudo cargar usuarios. Detalle: {e}")
                                content_surface_load_user = None
                            except Exception as e:
                                print(f"Error inesperado al cargar usuarios: {e}")
                                content_surface_load_user = None
                            
                    elif rect_btn_board.collidepoint(posicion_clic):
                        estado_actual = ESTADO_PUNTUACIONES
                        scroll_y_leaderboard = 0 
                        
                        try:
                            if usuarios_collection is None:
                                raise Exception("No hay conexión a la base de datos.")

                            lista_puntuaciones_cache = list(usuarios_collection.find(
                                {},  
                                {"nombre": 1, "puntuacion_maxima": 1, "_id": 0} 
                            ).sort(
                                "puntuacion_maxima", -1 
                            ).limit(20)) 

                            fuente_score = pygame.font.Font(None, 36)
                            altura_linea = 40
                            total_height_board = max(
                                len(lista_puntuaciones_cache) * altura_linea + 20, 
                                VIEWPORT_BOARD_RECT.height
                            )
                            content_surface_leaderboard = pygame.Surface((VIEWPORT_BOARD_RECT.width, total_height_board)).convert_alpha()
                            content_surface_leaderboard.fill((0,0,0,0)) 

                            max_scroll_board = content_surface_leaderboard.get_height() - VIEWPORT_BOARD_RECT.height
                            if max_scroll_board < 0: max_scroll_board = 0

                            if not lista_puntuaciones_cache:
                                fuente_msg = pygame.font.Font(None, 30)
                                texto_msg = fuente_msg.render("Aún no hay puntuaciones.", True, NEGRO)
                                msg_rect = texto_msg.get_rect(center=(VIEWPORT_BOARD_RECT.width // 2, 100))
                                content_surface_leaderboard.blit(texto_msg, msg_rect)
                            else:
                                y_inicio_scores = 20 
                                for i, doc in enumerate(lista_puntuaciones_cache):
                                    nombre_usuario = doc.get("nombre", "N/A")
                                    score = doc.get("puntuacion_maxima", 0)
                                    texto_linea = f"{i + 1}. {nombre_usuario} - {score} pts"
                                    texto_renderizado = fuente_score.render(texto_linea, True, NEGRO)
                                    linea_rect = texto_renderizado.get_rect(center=(VIEWPORT_BOARD_RECT.width // 2, y_inicio_scores + (i * altura_linea)))
                                    content_surface_leaderboard.blit(texto_renderizado, linea_rect)

                        except Exception as e:
                            print(f"Error al cargar puntuaciones: {e}")
                            content_surface_leaderboard = pygame.Surface((VIEWPORT_BOARD_RECT.width, VIEWPORT_BOARD_RECT.height)).convert_alpha()
                            content_surface_leaderboard.fill((0,0,0,0))
                            fuente_msg = pygame.font.Font(None, 30)
                            texto_error = fuente_msg.render("Error al cargar puntuaciones.", True, ROJO)
                            error_rect = texto_error.get_rect(center=(VIEWPORT_BOARD_RECT.width // 2, 100))
                            content_surface_leaderboard.blit(texto_error, error_rect)

                    elif rect_btn_exit.collidepoint(posicion_clic):
                        running = False

                elif estado_actual == ESTADO_REGISTRO_USUARIO:
                    if rect_btn_regresar_registro.collidepoint(posicion_clic):
                        estado_actual = ESTADO_MENU
                        input_username.texto = ""
                    elif rect_btn_guardar_usuario.collidepoint(posicion_clic):
                        nombre_a_guardar = input_username.texto.strip()
                        if not nombre_a_guardar:
                            print("El campo de nombre no puede estar vacío.")
                        elif usuarios_collection is None:
                            print("La conexión a la base de datos no está disponible.")
                        else:
                            try:
                                usuario_existente = usuarios_collection.find_one({"nombre": nombre_a_guardar})
                                if usuario_existente:
                                    print(f"Error: El usuario '{nombre_a_guardar}' ya existe.")
                                else:
                                    usuario_data = {"nombre": nombre_a_guardar, "puntuacion_maxima": 0}
                                    usuarios_collection.insert_one(usuario_data)
                                    print(f"¡Usuario '{nombre_a_guardar}' registrado con éxito!")
                                    usuario_actual = nombre_a_guardar
                                    estado_actual = ESTADO_JUEGO
                                    iniciar_juego_completo() 
                                    input_username.texto = ""
                            except ConnectionFailure as e:
                                print(f"ERROR DE CONEXIÓN: No se pudo guardar el usuario. Revisa que MongoDB esté activo. Detalle: {e}")
                            except Exception as e:
                                print(f"Ha ocurrido un error inesperado al guardar: {e}")
                
                
                elif estado_actual == ESTADO_CARGAR_USUARIO:
                    
                    if rect_btn_regresar_cargar.collidepoint(posicion_clic):
                        estado_actual = ESTADO_MENU
                        botones_usuarios.clear()
                        content_surface_load_user = None 
                    
                    if VIEWPORT_LOAD_RECT.collidepoint(posicion_clic):
                        pos_clic_relativo = (
                            posicion_clic[0] - VIEWPORT_LOAD_RECT.x,
                            posicion_clic[1] - VIEWPORT_LOAD_RECT.y + scroll_y_load_user
                        )
                        
                        for boton_usuario in botones_usuarios:
                            if boton_usuario.es_clicado(pos_clic_relativo):
                                usuario_actual = boton_usuario.texto_str
                                print(f"Usuario seleccionado: {usuario_actual}")
                                
                                estado_actual = ESTADO_JUEGO
                                iniciar_juego_completo() 
                                
                                botones_usuarios.clear()
                                content_surface_load_user = None 
                                break
                
                elif estado_actual == ESTADO_PUNTUACIONES:
                    if rect_btn_regresar_puntuaciones.collidepoint(posicion_clic):
                        estado_actual = ESTADO_MENU
                        content_surface_leaderboard = None 
                        lista_puntuaciones_cache.clear()
                            
                elif estado_actual == ESTADO_JUEGO:
                    if estado_partida == "GANADA":
                        if rect_btn_siguiente_palabra.collidepoint(posicion_clic):
                            if not iniciar_nueva_ronda(): 
                                print("Juego terminado (todas las palabras). Regresando al menú.")
                                guardar_puntuacion(usuario_actual, puntuacion_sesion) 
                                estado_actual = ESTADO_MENU
                                usuario_actual = None
                    
                    if rect_btn_terminar_juego.collidepoint(posicion_clic):
                        print("Saliendo del juego. Guardando puntuación.")
                        if estado_partida != "PERDIDA_GLOBAL":
                            guardar_puntuacion(usuario_actual, puntuacion_sesion)
                        estado_actual = ESTADO_MENU
                        usuario_actual = None

    if fondo:
        pantalla.blit(fondo, (0, 0))
    else:
        pantalla.fill(NEGRO)


    if estado_actual == ESTADO_MENU:
        
        if img_btn_create: pantalla.blit(img_btn_create, rect_btn_create)
        if img_btn_load: pantalla.blit(img_btn_load, rect_btn_load)
        if img_btn_board: pantalla.blit(img_btn_board, rect_btn_board)
        if img_btn_exit: pantalla.blit(img_btn_exit, rect_btn_exit)
            
    elif estado_actual == ESTADO_REGISTRO_USUARIO:
        
        pygame.draw.rect(pantalla, PANEL_COLOR, PANEL_REGISTRO_RECT, border_radius=PANEL_BORDER_RADIUS)
        
        fuente_titulo = pygame.font.Font(None, 40)
        texto_titulo = fuente_titulo.render("REGISTRAR NUEVO USUARIO", True, NEGRO)
        titulo_rect = texto_titulo.get_rect(center=(PANEL_REGISTRO_RECT.centerx, PANEL_REGISTRO_RECT.y + 40))
        pantalla.blit(texto_titulo, titulo_rect)

        fuente_instruccion = pygame.font.Font(None, 30)
        texto_instruccion = fuente_instruccion.render("Nombre de usuario:", True, NEGRO)
        instruccion_rect = texto_instruccion.get_rect(midleft=(input_username.rect.left, input_username.rect.top - 25))
        pantalla.blit(texto_instruccion, instruccion_rect)

        input_username.dibujar(pantalla)
        if img_btn_guardar: pantalla.blit(img_btn_guardar, rect_btn_guardar_usuario)
        if img_btn_regresar_form: pantalla.blit(img_btn_regresar_form, rect_btn_regresar_registro)
            
    elif estado_actual == ESTADO_CARGAR_USUARIO:
        
        pygame.draw.rect(pantalla, PANEL_COLOR, PANEL_LOAD_RECT, border_radius=PANEL_BORDER_RADIUS)

        fuente_titulo = pygame.font.Font(None, 40)
        texto_titulo = fuente_titulo.render("SELECCIONA TU USUARIO", True, NEGRO)
        titulo_rect = texto_titulo.get_rect(center=(PANEL_LOAD_RECT.centerx, PANEL_LOAD_RECT.y + 40))
        pantalla.blit(texto_titulo, titulo_rect)
        
        fuente_scroll = pygame.font.Font(None, 24)
        texto_scroll = fuente_scroll.render("(Usa la rueda del ratón para desplazarte)", True, (50, 50, 50)) 
        scroll_rect = texto_scroll.get_rect(center=(PANEL_LOAD_RECT.centerx, PANEL_LOAD_RECT.y + 70))
        pantalla.blit(texto_scroll, scroll_rect)

        if content_surface_load_user:
            pantalla.blit(
                content_surface_load_user,
                VIEWPORT_LOAD_RECT.topleft, 
                (0, scroll_y_load_user, VIEWPORT_LOAD_RECT.width, VIEWPORT_LOAD_RECT.height) 
            )
        else:
            fuente_msg = pygame.font.Font(None, 30)
            texto_msg = fuente_msg.render("No hay usuarios registrados.", True, NEGRO)
            msg_rect = texto_msg.get_rect(center=VIEWPORT_LOAD_RECT.center)
            pantalla.blit(texto_msg, msg_rect)
            
        if img_btn_regresar_nav: pantalla.blit(img_btn_regresar_nav, rect_btn_regresar_cargar)
            
    elif estado_actual == ESTADO_PUNTUACIONES:
        
        pygame.draw.rect(pantalla, PANEL_COLOR, PANEL_BOARD_RECT, border_radius=PANEL_BORDER_RADIUS)

        fuente_titulo = pygame.font.Font(None, 50)
        texto_titulo = fuente_titulo.render("MEJORES PUNTUACIONES", True, NEGRO)
        titulo_rect = texto_titulo.get_rect(center=(PANEL_BOARD_RECT.centerx, PANEL_BOARD_RECT.y + 40))
        pantalla.blit(texto_titulo, titulo_rect)
        
        fuente_scroll = pygame.font.Font(None, 24)
        texto_scroll = fuente_scroll.render("(Usa la rueda del ratón para desplazarte)", True, (50, 50, 50)) 
        scroll_rect = texto_scroll.get_rect(center=(PANEL_BOARD_RECT.centerx, PANEL_BOARD_RECT.y + 75))
        pantalla.blit(texto_scroll, scroll_rect)

        if content_surface_leaderboard:
            pantalla.blit(
                content_surface_leaderboard,    
                VIEWPORT_BOARD_RECT.topleft,    
                (0, scroll_y_leaderboard, VIEWPORT_BOARD_RECT.width, VIEWPORT_BOARD_RECT.height) 
            )

        if img_btn_regresar_nav: pantalla.blit(img_btn_regresar_nav, rect_btn_regresar_puntuaciones)

    elif estado_actual == ESTADO_JUEGO:
        dibujar_juego(pantalla) 
        
    pygame.display.flip()

pygame.quit()
sys.exit()
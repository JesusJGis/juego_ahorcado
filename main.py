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
    fondo = pygame.image.load('imagenes/fondo_pixel.jpg')
    fondo = pygame.transform.scale(fondo, (ANCHO_PANTALLA, ALTO_PANTALLA))
except pygame.error as e:
    print(f"Error: No se pudo cargar la imagen de fondo. Detalle: {e}")
    fondo = None

botones = []
botones_usuarios = []
usuario_actual = None
nombres_botones = ["Nuevo Usuario", "Cargar Usuario", "Puntuaciones", "Salir"]

imagen_inicio = pygame.image.load('imagenes/boton_NU.png').convert_alpha()

for i, nombre in enumerate(nombres_botones):
    y_pos = Y_INICIO + (i * (ALTO_BOTON + MARGEN_VERTICAL))
    
    nuevo_boton = Boton(
        x=X_FIJA,
        y=y_pos,
        ancho=ANCHO_BOTON,
        alto=ALTO_BOTON,
        color=AZUL,
        texto_str=nombre,
        color_texto=BLANCO
    )
    botones.append(nuevo_boton)

btn_regresar_puntuaciones = Boton(
    x=(ANCHO_PANTALLA // 2)-70,
    y=ALTO_PANTALLA - ALTO_BOTON - MARGEN,
    ancho=ANCHO_BOTON,
    alto=ALTO_BOTON,
    color=ROJO,
    texto_str="Regresar",
    color_texto=BLANCO
)

btn_guardar_usuario = Boton(
    x=ANCHO_PANTALLA // 2 - 75,
    y=400,
    ancho=150,
    alto=50,
    color=(0, 150, 0),
    texto_str="Guardar",
    color_texto=BLANCO
)

btn_regresar_registro = Boton(
    x=ANCHO_PANTALLA // 2 - 75,
    y=470,
    ancho=150,
    alto=50,
    color=(150, 0, 0),
    texto_str="Regresar",
    color_texto=BLANCO
)

btn_regresar_cargar = Boton(
    x=(ANCHO_PANTALLA // 2) - (ANCHO_BOTON // 2),
    y=ALTO_PANTALLA - ALTO_BOTON - MARGEN,
    ancho=ANCHO_BOTON,
    alto=ALTO_BOTON,
    color=ROJO,
    texto_str="Regresar",
    color_texto=BLANCO
)

btn_siguiente_palabra = Boton(
    x=(ANCHO_PANTALLA // 2) - 100,
    y=ALTO_PANTALLA - 150,
    ancho=200,
    alto=50,
    color=VERDE,
    texto_str="Siguiente Palabra",
    color_texto=BLANCO
)

btn_terminar_juego = Boton(
    x=(ANCHO_PANTALLA // 2) - 100,
    y=ALTO_PANTALLA - 80,
    ancho=200,
    alto=50,
    color=ROJO,
    texto_str="Salir al Menú",
    color_texto=BLANCO
)

input_username = InputBox(
    x=ANCHO_PANTALLA // 2 - 160,
    y=300,
    w=300,
    h=40,
    texto=''
)

btn_salir = botones[3]
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

def cargar_palabras():
    """Carga las palabras desde MongoDB, las baraja y filtra documentos incorrectos."""
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
            return [{"palabra": "PYTHON", "pista": "Lenguaje de programación"}] # Fallback
            
        random.shuffle(palabras_validas)
        return palabras_validas
        
    except Exception as e:
        print(f"Error al cargar palabras: {e}")
        return [{"palabra": "PYTHON", "pista": "Lenguaje de programación"}]

def guardar_puntuacion(username, nueva_puntuacion):
    """Guarda la puntuación si es un nuevo récord."""
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
    """Configura las variables para la siguiente palabra."""
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
    """Inicia toda la sesión de juego."""
    global lista_palabras_juego, indice_palabra_actual, puntuacion_sesion, estado_partida, intentos_globales_restantes, letras_incorrectas
    print(f"Iniciando juego para {usuario_actual}")
    lista_palabras_juego = cargar_palabras()
    indice_palabra_actual = 0
    puntuacion_sesion = 0
    intentos_globales_restantes = MAX_INTENTOS_TOTALES 
    letras_incorrectas = []
    estado_partida = "JUGANDO"
    iniciar_nueva_ronda() 

def dibujar_juego(pantalla):
    """Dibuja todos los elementos de la pantalla de juego."""
    global estado_partida
    
    fuente_pista = pygame.font.Font(None, 32)
    fuente_palabra = pygame.font.Font(None, 60)
    fuente_letras = pygame.font.Font(None, 40)
    fuente_info = pygame.font.Font(None, 30)
    fuente_resultado = pygame.font.Font(None, 70)

    texto_pista_titulo = fuente_info.render("PISTA:", True, NEGRO)
    pantalla.blit(texto_pista_titulo, (MARGEN, 100))
    texto_pista = fuente_pista.render(pista_actual, True, NEGRO)
    pantalla.blit(texto_pista, (MARGEN, 140))

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
    
    texto_palabra = fuente_palabra.render(palabra_mostrada, True, NEGRO)
    rect_palabra = texto_palabra.get_rect(center=(ANCHO_PANTALLA // 2, 300))
    pantalla.blit(texto_palabra, rect_palabra)

    texto_incorrectas_titulo = fuente_info.render("Incorrectas:", True, ROJO)
    pantalla.blit(texto_incorrectas_titulo, (MARGEN, 400))
    texto_incorrectas = fuente_letras.render(" ".join(letras_incorrectas), True, ROJO)
    pantalla.blit(texto_incorrectas, (MARGEN, 440))

    texto_intentos = fuente_info.render(f"Intentos restantes: {intentos_globales_restantes}", True, NEGRO) 
    pantalla.blit(texto_intentos, (ANCHO_PANTALLA - texto_intentos.get_width() - MARGEN, 100))
    
    texto_puntuacion = fuente_info.render(f"Puntuación: {puntuacion_sesion}", True, VERDE)
    pantalla.blit(texto_puntuacion, (ANCHO_PANTALLA - texto_puntuacion.get_width() - MARGEN, 140))


    if estado_partida == "GANADA":
        texto_resultado = fuente_resultado.render("¡CORRECTO!", True, VERDE)
        pantalla.blit(texto_resultado, (ANCHO_PANTALLA // 2 - texto_resultado.get_width() // 2, 400))
        btn_siguiente_palabra.dibujar(pantalla)
    
    elif estado_partida == "PERDIDA_GLOBAL": 
        texto_resultado = fuente_resultado.render("¡FIN DEL JUEGO!", True, ROJO)
        pantalla.blit(texto_resultado, (ANCHO_PANTALLA // 2 - texto_resultado.get_width() // 2, 400))
        
        texto_score_final = fuente_letras.render(f"Palabras adivinadas: {puntuacion_sesion}", True, NEGRO)
        pantalla.blit(texto_score_final, (ANCHO_PANTALLA // 2 - texto_score_final.get_width() // 2, 480))
        
    btn_terminar_juego.dibujar(pantalla)

running = True
while running:

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            if estado_actual == ESTADO_JUEGO and usuario_actual:
                guardar_puntuacion(usuario_actual, puntuacion_sesion)


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
                    
                    if botones[0].es_clicado(posicion_clic):
                        estado_actual = ESTADO_REGISTRO_USUARIO
                        
                    elif botones[1].es_clicado(posicion_clic):
                        estado_actual = ESTADO_CARGAR_USUARIO
                        botones_usuarios.clear()
                        
                        if usuarios_collection is None:
                            print("La conexión a la base de datos no está disponible.")
                        else:
                            try:
                                lista_usuarios_db = list(usuarios_collection.find({}, {"nombre": 1, "_id": 0}))
                                
                                if not lista_usuarios_db:
                                    print("No hay usuarios registrados.")
                                
                                y_inicio_lista = 150
                                alto_btn_usuario = 50
                                margen_btn_usuario = 15
                                ancho_btn_usuario = 300
                                
                                for i, doc_usuario in enumerate(lista_usuarios_db):
                                    nombre_usuario = doc_usuario['nombre']
                                    
                                    y_pos = y_inicio_lista + (i * (alto_btn_usuario + margen_btn_usuario))
                                    
                                    nuevo_boton_usuario = Boton(
                                        x=(ANCHO_PANTALLA // 2) - (ancho_btn_usuario // 2),
                                        y=y_pos,
                                        ancho=ancho_btn_usuario,
                                        alto=alto_btn_usuario,
                                        color=AZUL,
                                        texto_str=nombre_usuario,
                                        color_texto=BLANCO
                                    )
                                    botones_usuarios.append(nuevo_boton_usuario)
                                    
                            except ConnectionFailure as e:
                                print(f"ERROR DE CONEXIÓN: No se pudo cargar usuarios. Detalle: {e}")
                            except Exception as e:
                                print(f"Error inesperado al cargar usuarios: {e}")
                            
                    elif botones[2].es_clicado(posicion_clic):
                        estado_actual = ESTADO_PUNTUACIONES
                        
                    elif botones[3].es_clicado(posicion_clic):
                        running = False

                elif estado_actual == ESTADO_REGISTRO_USUARIO:

                    if btn_regresar_registro.es_clicado(posicion_clic):
                        estado_actual = ESTADO_MENU
                        input_username.texto = ""

                    elif btn_guardar_usuario.es_clicado(posicion_clic):
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
                                    input_username.texto = ""

                            except ConnectionFailure as e:
                                print(f"ERROR DE CONEXIÓN: No se pudo guardar el usuario. Revisa que MongoDB esté activo. Detalle: {e}")
                            
                            except Exception as e:
                                print(f"Ha ocurrido un error inesperado al guardar: {e}")
                
                
                elif estado_actual == ESTADO_CARGAR_USUARIO:
                    
                    if btn_regresar_cargar.es_clicado(posicion_clic):
                        estado_actual = ESTADO_MENU
                        botones_usuarios.clear()
                    
                    for boton_usuario in botones_usuarios:
                        if boton_usuario.es_clicado(posicion_clic):
                            usuario_actual = boton_usuario.texto_str
                            print(f"Usuario seleccionado: {usuario_actual}")
                            
                            estado_actual = ESTADO_JUEGO
                            iniciar_juego_completo() 
                            
                            botones_usuarios.clear()
                            break
                
                elif estado_actual == ESTADO_PUNTUACIONES:
                    if btn_regresar_puntuaciones.es_clicado(posicion_clic):
                        estado_actual = ESTADO_MENU
                        
                elif estado_actual == ESTADO_JUEGO:
                    
                    if estado_partida == "GANADA":
                        if btn_siguiente_palabra.es_clicado(posicion_clic):
                            if not iniciar_nueva_ronda(): 
                                print("Juego terminado (todas las palabras). Regresando al menú.")
                                guardar_puntuacion(usuario_actual, puntuacion_sesion) 
                                estado_actual = ESTADO_MENU
                                usuario_actual = None
                    
                    if btn_terminar_juego.es_clicado(posicion_clic):
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
        
        for boton in botones:
            boton.dibujar(pantalla)
            
    elif estado_actual == ESTADO_REGISTRO_USUARIO:
        fuente_titulo = pygame.font.Font(None, 40)
        fuente_input = pygame.font.Font(None, 36)

        texto_titulo = fuente_titulo.render("REGISTRAR NUEVO USUARIO", True, NEGRO)
        pantalla.blit(texto_titulo, (ANCHO_PANTALLA//2 - texto_titulo.get_width()//2, 100))

        fuente_instruccion = pygame.font.Font(None, 30)
        texto_instruccion = fuente_instruccion.render("Nombre de usuario:", True, NEGRO)
        pantalla.blit(texto_instruccion, (ANCHO_PANTALLA // 2 - 100, 270))

        input_username.dibujar(pantalla)

        btn_guardar_usuario.dibujar(pantalla)
        btn_regresar_registro.dibujar(pantalla)
        
    elif estado_actual == ESTADO_CARGAR_USUARIO:
        
        fuente_titulo = pygame.font.Font(None, 40)
        texto_titulo = fuente_titulo.render("SELECCIONA TU USUARIO", True, NEGRO)
        pantalla.blit(texto_titulo, (ANCHO_PANTALLA//2 - texto_titulo.get_width()//2, 80))

        for boton_usuario in botones_usuarios:
            boton_usuario.dibujar(pantalla)
            
        if not botones_usuarios and usuarios_collection is not None:
            fuente_msg = pygame.font.Font(None, 30)
            texto_msg = fuente_msg.render("No hay usuarios registrados. Crea uno nuevo.", True, NEGRO)
            pantalla.blit(texto_msg, (ANCHO_PANTALLA//2 - texto_msg.get_width()//2, 350))

        btn_regresar_cargar.dibujar(pantalla)
        
    elif estado_actual == ESTADO_PUNTUACIONES:
        fuente_titulo = pygame.font.Font(None, 50)
        texto_titulo = fuente_titulo.render("MEJORES PUNTUACIONES", True, NEGRO)
        titulo_rect = texto_titulo.get_rect(center=(ANCHO_PANTALLA // 2, 80))
        pantalla.blit(texto_titulo, titulo_rect)

        try:
            if usuarios_collection is None:
                raise Exception("No hay conexión a la base de datos.")

            lista_puntuaciones = list(usuarios_collection.find(
                {},  
                {"nombre": 1, "puntuacion_maxima": 1, "_id": 0} 
            ).sort(
                "puntuacion_maxima", -1 
            ).limit(10)) 

            if not lista_puntuaciones:
                fuente_msg = pygame.font.Font(None, 30)
                texto_msg = fuente_msg.render("Aún no hay puntuaciones registradas.", True, NEGRO)
                msg_rect = texto_msg.get_rect(center=(ANCHO_PANTALLA // 2, 300))
                pantalla.blit(texto_msg, msg_rect)
            else:
                fuente_score = pygame.font.Font(None, 36)
                y_inicio_scores = 150
                altura_linea = 40

                for i, doc in enumerate(lista_puntuaciones):
                    nombre_usuario = doc.get("nombre", "N/A")
                    score = doc.get("puntuacion_maxima", 0)
                    
                    texto_linea = f"{i + 1}. {nombre_usuario} - {score} pts"
                    
                    texto_renderizado = fuente_score.render(texto_linea, True, NEGRO)
                    
                    linea_rect = texto_renderizado.get_rect(center=(ANCHO_PANTALLA // 2, y_inicio_scores + (i * altura_linea)))
                    pantalla.blit(texto_renderizado, linea_rect)

        except Exception as e:
            print(f"Error al cargar puntuaciones: {e}")
            fuente_msg = pygame.font.Font(None, 30)
            texto_error = fuente_msg.render("Error al cargar puntuaciones.", True, ROJO)
            error_rect = texto_error.get_rect(center=(ANCHO_PANTALLA // 2, 300))
            pantalla.blit(texto_error, error_rect)

        btn_regresar_puntuaciones.dibujar(pantalla)

    elif estado_actual == ESTADO_JUEGO:
        dibujar_juego(pantalla)
    pygame.display.flip()

pygame.quit()
sys.exit()
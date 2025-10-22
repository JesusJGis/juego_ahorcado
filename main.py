import pygame
import sys
import random
from pygame.locals import *
from variables_constantes import *
from PIL import Image
from conexion.cliente import usuarios_collection
from pymongo.errors import ConnectionFailure 
from componentes.boton_clase import Boton
from componentes.input_box import InputBox

pygame.init()

pantalla = pygame.display.set_mode((ANCHO_PANTALLA, ALTO_PANTALLA))
pygame.display.set_caption('Ahorcado')

try:
    fondo = pygame.image.load('imagenes/prototipo_fondo_1.png')
    fondo = pygame.transform.scale(fondo, (ANCHO_PANTALLA, ALTO_PANTALLA))
except pygame.error as e:
    print(f"Error: No se pudo cargar la imagen de fondo. Detalle: {e}")
    fondo = None

botones = []
botones_usuarios = []
usuario_actual = None
nombres_botones = ["Nuevo Usuario", "Cargar Usuario", "Puntuaciones", "Salir"]

try:
    sprite_img = pygame.image.load('imagenes/LOGO.png')
    sprite_img = pygame.transform.scale(sprite_img, (400, 400)) 
    
    sprite_rect = sprite_img.get_rect()
    sprite_rect.centerx = ANCHO_PANTALLA // 2

    sprite_rect.top = -150
    
except pygame.error as e:
    print(f"Error: No se pudo cargar el sprite del ahorcado. Detalle: {e}")
    sprite_img = None
    sprite_rect = None

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
color_texto=BLANCO)

btn_regresar_registro = Boton(
x=ANCHO_PANTALLA // 2 - 75,
y=470,
ancho=150, 
alto=50, 
color=(150, 0, 0),
texto_str="Regresar", 
color_texto=BLANCO)

btn_regresar_cargar = Boton(
    x=(ANCHO_PANTALLA // 2) - (ANCHO_BOTON // 2), 
    y=ALTO_PANTALLA - ALTO_BOTON - MARGEN,
    ancho=ANCHO_BOTON, 
    alto=ALTO_BOTON, 
    color=ROJO, 
    texto_str="Regresar", 
    color_texto=BLANCO
)

btn_regresar_perfil = Boton(
    x=(ANCHO_PANTALLA // 2) - (ANCHO_BOTON // 2), 
    y=ALTO_PANTALLA - ALTO_BOTON - MARGEN,
    ancho=ANCHO_BOTON, 
    alto=ALTO_BOTON, 
    color=ROJO, 
    texto_str="Regresar al Menú", 
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

running = True
while running:

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if estado_actual == ESTADO_REGISTRO_USUARIO:
            input_username.handle_event(event)

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
                                    estado_actual = ESTADO_PERFIL_CARGADO
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
                            
                            estado_actual = ESTADO_PERFIL_CARGADO 
                            botones_usuarios.clear() 
                            break                
                
                elif estado_actual == ESTADO_PUNTUACIONES:
                    if btn_regresar_puntuaciones.es_clicado(posicion_clic):
                        estado_actual = ESTADO_MENU
                        
                elif estado_actual == ESTADO_PERFIL_CARGADO:
                    if btn_regresar_perfil.es_clicado(posicion_clic):
                        estado_actual = ESTADO_MENU
                
    if fondo:
        pantalla.blit(fondo, (0, 0))
    else:
        pantalla.fill(NEGRO)

    if estado_actual == ESTADO_MENU:
        
        if sprite_img:
            pantalla.blit(sprite_img, sprite_rect) 
        
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
        fuente = pygame.font.Font(None, 50)
        texto_puntos = fuente.render("VENTANA PUNTUACIONES", True, VERDE)
        pantalla.blit(texto_puntos, (ANCHO_PANTALLA//2 - texto_puntos.get_width()//2, 350))

        btn_regresar_puntuaciones.dibujar(pantalla)

    elif estado_actual == ESTADO_PERFIL_CARGADO:
            fuente_titulo = pygame.font.Font(None, 50)
            
            if usuario_actual:
                texto_bienvenida = fuente_titulo.render(f"Perfil de: {usuario_actual}", True, NEGRO)
                pantalla.blit(texto_bienvenida, (ANCHO_PANTALLA//2 - texto_bienvenida.get_width()//2, 250))
                btn_regresar_perfil.dibujar(pantalla)
        
    pygame.display.flip()

pygame.quit()
sys.exit()
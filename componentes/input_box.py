import pygame
from variables_constantes import * # Asegúrate que NEGRO esté aquí

class InputBox:
    def __init__(self, x, y, w, h, texto=''):
        self.rect = pygame.Rect(x, y, w, h)
        self.ancho_original = w 
        self.color_inactivo = (180, 180, 180) 
        self.color_activo = (255, 255, 255) 
        self.color = self.color_inactivo
        self.texto = texto
        self.fuente = pygame.font.Font(None, 36)
        self.activo = False
        
        self.color_borde = NEGRO
        self.color_texto = NEGRO

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.activo = not self.activo
            else:
                self.activo = False
            self.color = self.color_activo if self.activo else self.color_inactivo
            
        if event.type == pygame.KEYDOWN:
            if self.activo:
                if event.key == pygame.K_RETURN:
                    self.activo = False
                    self.color = self.color_inactivo
                elif event.key == pygame.K_BACKSPACE:
                    self.texto = self.texto[:-1] 
                else:
                    self.texto += event.unicode
    def dibujar(self, pantalla):
        pygame.draw.rect(pantalla, self.color, self.rect)
        texto_surface = self.fuente.render(self.texto, True, self.color_texto)
        ancho_usable_caja = self.rect.w - 10 
        ancho_texto = texto_surface.get_width()
        pos_x_texto = self.rect.x + 5 
        
        if ancho_texto > ancho_usable_caja:
            pos_x_texto = self.rect.right - 5 - ancho_texto
        clip_original = pantalla.get_clip()
        pantalla.set_clip(self.rect.inflate(-6, -6))
        pantalla.blit(texto_surface, (pos_x_texto, self.rect.y + 5))
        pantalla.set_clip(clip_original)
        pygame.draw.rect(pantalla, self.color_borde, self.rect, 2)
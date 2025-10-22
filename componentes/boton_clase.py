import pygame
from variables_constantes import *

class Boton:
    def __init__(self, x, y, ancho, alto, color, texto_str, color_texto):
        self.rect = pygame.Rect(x, y, ancho, alto)
        self.color = color
        self.texto_str = texto_str
        self.color_texto = color_texto
        
        self.fuente = pygame.font.Font(None, 30)
        self.texto_renderizado = self.fuente.render(self.texto_str, True, self.color_texto)
        self.texto_rect = self.texto_renderizado.get_rect(center=self.rect.center)

    def dibujar(self, superficie):
        pygame.draw.rect(superficie, self.color, self.rect)
        superficie.blit(self.texto_renderizado, self.texto_rect)

    def es_clicado(self, pos):
        return self.rect.collidepoint(pos)
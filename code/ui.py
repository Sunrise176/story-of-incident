import pygame
from settings import * 

class UI:
	def __init__(self):
		
		# инициализация
		self.display_surface = pygame.display.get_surface()
		self.font = pygame.font.Font(UI_FONT,UI_FONT_SIZE)

		# настройки полос хп и стамины
		self.health_bar_rect = pygame.Rect(10,10,HEALTH_BAR_WIDTH,BAR_HEIGHT)
		self.energy_bar_rect = pygame.Rect(10,34,ENERGY_BAR_WIDTH,BAR_HEIGHT)

	def show_bar(self,current,max_amount,bg_rect,color):
		# рисуем фон
		pygame.draw.rect(self.display_surface,UI_BG_COLOR,bg_rect)

		# конвертируем характеристики игрока в пиксели
		ratio = current / max_amount
		current_width = bg_rect.width * ratio
		current_rect = bg_rect.copy()
		current_rect.width = current_width

		# рисуем полосы
		pygame.draw.rect(self.display_surface,color,current_rect)
		pygame.draw.rect(self.display_surface,UI_BORDER_COLOR,bg_rect,3)

	# рисуем сколько у игрока очков
	def show_exp(self,exp):
		text_surf = self.font.render(str(int(exp)),False,TEXT_COLOR)
		x = self.display_surface.get_size()[0] - 20
		y = self.display_surface.get_size()[1] - 20
		text_rect = text_surf.get_rect(bottomright = (x,y))

		pygame.draw.rect(self.display_surface,UI_BG_COLOR,text_rect.inflate(20,20))
		self.display_surface.blit(text_surf,text_rect)
		pygame.draw.rect(self.display_surface,UI_BORDER_COLOR,text_rect.inflate(20,20),3)

	# отображаем что нарисовали
	def display(self,player):
		self.show_bar(player.health,player.stats['health'],self.health_bar_rect,HEALTH_COLOR)
		self.show_bar(player.stamina,player.stats['energy'],self.energy_bar_rect,ENERGY_COLOR)

		self.show_exp(player.exp)
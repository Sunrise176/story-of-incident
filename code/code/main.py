import pygame, sys
from settings import *
from level import Level
from player import *


class Game:
	def __init__(self):

		# инициализация
		pygame.init()
		self.screen = pygame.display.set_mode((WIDTH,HEIGTH))
		pygame.display.set_caption('Story of incident')
		self.clock = pygame.time.Clock()

		self.level = Level()

		# музыка
		main_sound = pygame.mixer.Sound('../audio/main1.ogg')
		main_sound.set_volume(0.5)
		# для повторения музыки
		main_sound.play(loops = -1)
	
	def run(self):
		while True:
			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					pygame.quit()
					sys.exit()

			self.screen.fill(WATER_COLOR)
			self.level.run()
			pygame.display.update()
			self.clock.tick(FPS)


if __name__ == '__main__':
	game = Game()
	game.run()
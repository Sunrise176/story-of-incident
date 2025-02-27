import pygame 
from settings import *
from tile import Tile
from player import Player
from support import *
from random import choice, randint
from weapon import Weapon
from ui import UI
from enemy import Enemy
from particles import AnimationPlayer

class Level:
	def __init__(self):

		# поверхность отображения
		self.display_surface = pygame.display.get_surface()

		# создаем группы
		self.visible_sprites = YSortCameraGroup()
		self.obstacle_sprites = pygame.sprite.Group()

		# спрайты атаки
		self.current_attack = None
		self.attack_sprites = pygame.sprite.Group()
		self.attackable_sprites = pygame.sprite.Group()

		# загрузка спрайтов
		self.create_map()

		# интерфейс
		self.ui = UI()

		# частицы
		self.animation_player = AnimationPlayer()

	# перед началом игры создаем все спрайты с помощью файлов
	def create_map(self):
		layouts = {
			'boundary': import_csv_layout('../map/map_FloorBlocks.csv'),
			'grass': import_csv_layout('../map/map_Grass.csv'),
			'object': import_csv_layout('../map/map_Objects.csv'),
			'entities': import_csv_layout('../map/map_Entities.csv')
		}
		path_obj = import_path('../graphics/objects')
		path_grass = import_path('../graphics/grass')
		for type, layout in layouts.items():
			for row_index,row in enumerate(layout):
				for cell_index, cell in enumerate(row):
					if cell != '-1':
						x = cell_index * TILESIZE
						y = row_index * TILESIZE
						if type == 'boundary':
							Tile((x,y),[self.obstacle_sprites],'invisible')

						if type == 'grass':
							surf = path_grass[cell]
							Tile(
								(x,y),
								[self.visible_sprites,self.obstacle_sprites,self.attackable_sprites],
								'grass',
								surf)

						if type == 'object':
							if cell in path_obj.keys():
								surf = path_obj[cell]
								Tile((x,y),[self.visible_sprites,self.obstacle_sprites],'object',surf)

						if type == 'entities':
							if cell == '1536':
								self.player = Player(
									(x,y),
									[self.visible_sprites],
									self.obstacle_sprites,
									self.create_attack,
									self.destroy_attack)
							else:
								if cell == '1528':
									monster_name = 'spider'
								elif cell == '1530':
									monster_name = 'spirit'
								elif cell == '1532':
									monster_name = 'tengu'
								else:
									monster_name = 'bear'
								Enemy(
									monster_name,
									(x,y),
									[self.visible_sprites,self.attackable_sprites],
									self.obstacle_sprites,
									self.damage_player,
									self.trigger_death_particles,
									self.add_points)

	#создаем спрайт меча
	def create_attack(self):
		self.current_attack = Weapon(self.player,[self.visible_sprites,self.attack_sprites])

	#время вышло и мы убираем спрайт меча
	def destroy_attack(self):
		if self.current_attack:
			self.current_attack.kill()
		self.current_attack = None

	#прописываем логику атаки: с кем сталкивается и т.д.
	def player_attack_logic(self):
		if self.attack_sprites:
			for attack_sprite in self.attack_sprites:
				collision_sprites = pygame.sprite.spritecollide(attack_sprite,self.attackable_sprites,False)
				if collision_sprites:
					for target_sprite in collision_sprites:
						if target_sprite.sprite_type == 'grass':
							pos = target_sprite.rect.center
							offset = pygame.math.Vector2(0,75)
							for leaf in range(randint(3,6)):
								self.animation_player.create_grass_particles(pos - offset,[self.visible_sprites])
							target_sprite.kill()
						else:
							target_sprite.get_damage(self.player,attack_sprite.sprite_type)

	#отнимаем у игрока хп
	def damage_player(self,amount,attack_type):
		if self.player.vulnerable:
			self.player.health -= amount
			self.player.vulnerable = False
			self.player.hurt_time = pygame.time.get_ticks()
			self.animation_player.create_particles(attack_type,self.player.rect.center,[self.visible_sprites])

	#если враг повержен - запускаем анимацию поражения
	def trigger_death_particles(self,pos,particle_type):
		self.animation_player.create_particles(particle_type,pos,self.visible_sprites)

	# добавляем очки
	def add_points(self,amount):
		self.player.exp += amount

	# проверяем смерть игрока ()
	def check_death_player(self):
		if self.player.health <= 0:
			for sprite in self.attackable_sprites:
				sprite.kill()
			self.player.destroy_attack()
			self.player.kill()
			layout = import_csv_layout('../map/map_Entities.csv')
			for row_index, row  in enumerate(layout):
				for cell_index, cell in enumerate(row):
					if cell != '-1':
						x = cell_index * TILESIZE
						y = row_index * TILESIZE
						if cell == '1536':
							self.player = Player(
								(x,y),
								[self.visible_sprites],
								self.obstacle_sprites,
								self.create_attack,
								self.destroy_attack)
						else:
							if cell == '1528':
								monster_name = 'spider'
							elif cell == '1530':
								monster_name = 'spirit'
							elif cell == '1532':
								monster_name = 'tengu'
							else:
								monster_name = 'bear'
							Enemy(
								monster_name,
								(x,y),
								[self.visible_sprites,self.attackable_sprites],
								self.obstacle_sprites,
								self.damage_player,
								self.trigger_death_particles,
								self.add_points)




	# цикл игры
	def run(self):
		self.visible_sprites.custom_draw(self.player)
		self.ui.display(self.player)
		self.visible_sprites.update()
		self.visible_sprites.enemy_update(self.player)
		self.player_attack_logic()
		self.check_death_player()
		

class YSortCameraGroup(pygame.sprite.Group):
	def __init__(self):

		# инициализация
		super().__init__()
		self.display_surface = pygame.display.get_surface()
		self.half_width = self.display_surface.get_size()[0] // 2
		self.half_height = self.display_surface.get_size()[1] // 2
		self.cam_pos = pygame.math.Vector2()

		# создаем пол
		self.floor_surf = pygame.image.load('../graphics/tilemap/ground.png').convert()
		self.floor_rect = self.floor_surf.get_rect(topleft = (0,0))

	def custom_draw(self,player):

		# ищем смещение камеры
		self.cam_pos.x = player.rect.centerx - self.half_width
		self.cam_pos.y = player.rect.centery - self.half_height

		# рисуем пол
		floor_offset_pos = self.floor_rect.topleft - self.cam_pos
		self.display_surface.blit(self.floor_surf,floor_offset_pos)

		# рисуем спрайты по Y
		for sprite in sorted(self.sprites(),key = lambda sprite: sprite.rect.centery):
			offset_pos = sprite.rect.topleft - self.cam_pos
			self.display_surface.blit(sprite.image,offset_pos)

	# обновляем врагов
	def enemy_update(self,player):
		enemy_sprites = [sprite for sprite in self.sprites() if hasattr(sprite,'sprite_type') if sprite.sprite_type == 'enemy']
		for enemy in enemy_sprites:
			enemy.enemy_update(player)

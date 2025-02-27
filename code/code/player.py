import pygame 
from settings import *
from support import import_folder


class Player(pygame.sprite.Sprite):
	def __init__(self,pos,groups,obstacle_sprites,create_attack,destroy_attack):
		# инициализация игрока
		super().__init__(groups)
		self.frame_index = 0
		self.animation_speed = 0.15
		self.direction = pygame.math.Vector2()
		self.image = pygame.image.load('../graphics/player/down_idle/idle_down.png').convert_alpha()
		self.rect = self.image.get_rect(topleft = pos)
		self.hitbox = self.rect.inflate(-6,HITBOX_OFFSET['player'])

		# импортируем графику
		self.import_player_assets()
		self.status = 'down'

		# передвижение и атака
		self.attacking = False
		self.attack_cooldown = 400
		self.attack_time = None
		self.obstacle_sprites = obstacle_sprites

		# настраиваем оружие
		self.create_attack = create_attack
		self.destroy_attack = destroy_attack

		# настраиваем параметры
		self.stats = {'health': 100,'energy':60,'attack': 10,'magic': 4,'speed': 5}
		self.health = self.stats['health'] * 0.5
		self.stamina = self.stats['energy'] * 0.8
		self.exp = 0
		self.speed = self.stats['speed']

		# добавляем игроку неуязвимость
		self.vulnerable = True
		self.hurt_time = None
		self.invulnerability_duration = 500

		# музыка
		self.weapon_attack_sound = pygame.mixer.Sound('../audio/sword.wav')
		self.weapon_attack_sound.set_volume(0.4)

		# движение игрока
	def move(self, speed):
		if self.direction.magnitude() != 0:
			self.direction = self.direction.normalize()
			self.stamina -= speed * 0.02
		if self.stamina <= 0:
			speed *= 0.5
		self.hitbox.x += self.direction.x * speed
		self.collision('horizontal')
		self.hitbox.y += self.direction.y * speed
		self.collision('vertical')
		self.rect.center = self.hitbox.center


		# обработка столкновений
	def collision(self, direction):
		if direction == 'horizontal':
			for sprite in self.obstacle_sprites:
				if sprite.hitbox.colliderect(self.hitbox):
					if self.direction.x > 0:  # moving right
						self.hitbox.right = sprite.hitbox.left
					if self.direction.x < 0:  # moving left
						self.hitbox.left = sprite.hitbox.right

		if direction == 'vertical':
			for sprite in self.obstacle_sprites:
				if sprite.hitbox.colliderect(self.hitbox):
					if self.direction.y > 0:  # moving down
						self.hitbox.bottom = sprite.hitbox.top
					if self.direction.y < 0:  # moving up
						self.hitbox.top = sprite.hitbox.bottom

	#импортируем графику игрока
	def import_player_assets(self):
		character_path = '../graphics/player/'
		self.animations = {'up': [],'down': [],'left': [],'right': [],
			'right_idle':[],'left_idle':[],'up_idle':[],'down_idle':[],
			'right_attack':[],'left_attack':[],'up_attack':[],'down_attack':[]}

		for animation in self.animations.keys():
			full_path = character_path + animation
			self.animations[animation] = import_folder(full_path)

	# обрабатываем клавиши атаки и движения
	def input(self):
		if not self.attacking:
			keys = pygame.key.get_pressed()

			if keys[pygame.K_w]:
				self.direction.y = -1
				self.status = 'up'
			elif keys[pygame.K_s]:
				self.direction.y = 1
				self.status = 'down'
			else:
				self.direction.y = 0

			if keys[pygame.K_d]:
				self.direction.x = 1
				self.status = 'right'
			elif keys[pygame.K_a]:
				self.direction.x = -1
				self.status = 'left'
			else:
				self.direction.x = 0

			if keys[pygame.K_SPACE]:
				self.attacking = True
				self.attack_time = pygame.time.get_ticks()
				self.create_attack()
				self.weapon_attack_sound.play()

	# находим статус игрока
	def get_status(self):
		# idle status
		if self.direction.x == 0 and self.direction.y == 0:
			if not 'idle' in self.status and not 'attack' in self.status:
				self.status = self.status + '_idle'

		if self.attacking:
			self.direction.x = 0
			self.direction.y = 0
			if not 'attack' in self.status:
				if 'idle' in self.status:
					self.status = self.status.replace('_idle','_attack')
				else:
					self.status = self.status + '_attack'
		else:
			if 'attack' in self.status:
				self.status = self.status.replace('_attack','')

	# проверяем откатилась ли у игрока атака и не нужно ли снять неуязвимость
	def cooldowns(self):
		current_time = pygame.time.get_ticks()

		if self.attacking:
			if current_time - self.attack_time >= self.attack_cooldown + weapon_data['cooldown']:
				self.attacking = False
				self.destroy_attack()

		if not self.vulnerable:
			if current_time - self.hurt_time >= self.invulnerability_duration:
				self.vulnerable = True

	# анимация игрока
	def animate(self):
		animation = self.animations[self.status]

		# если анимация проигралась
		self.frame_index += self.animation_speed
		if self.frame_index >= len(animation):
			self.frame_index = 0

		# задаем изображение
		self.image = animation[int(self.frame_index)]
		self.rect = self.image.get_rect(center = self.hitbox.center)

	# восстанавливаем ресурсы
	def recovery(self):
		if self.stamina < self.stats['energy']:
			self.stamina += 0.01 * self.stats['magic']
		else:
			self.stamina = self.stats['energy']

		if self.health < self.stats['health']:
			self.health += 0.00005 * self.stats['health']
		else:
			self.health = self.stats['health']

	# для обновления спрайта
	def update(self):
		self.input()
		self.cooldowns()
		self.get_status()
		self.animate()
		self.move(self.stats['speed'])
		self.recovery()
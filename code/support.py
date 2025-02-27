from csv import reader
from os import walk
import pygame


# считываем информацию с файлов карты
def import_csv_layout(path):
	terrain_map = []
	with open(path) as level_map:
		layout = reader(level_map,delimiter = ',')
		for row in layout:
			terrain_map.append(list(row))
		return terrain_map


	# импортируем папку в список фреймов
def import_folder(path):
	surface_list = []

	for _,__,img_files in walk(path):
		for image in img_files:
			full_path = path + '/' + image
			image_surf = pygame.image.load(full_path).convert_alpha()
			surface_list.append(image_surf)

	return surface_list


	# импортируем папку в словарь, где ключ - имя файла, для создания обьектов на карте
def import_path(path):
	path_dict = {}
	for _, __, img_files in walk(path):
		for image in img_files:
			full_path = path + '/' + image
			image_surf = pygame.image.load(full_path).convert_alpha()
			path_dict[image[:-4]] = image_surf
	return path_dict
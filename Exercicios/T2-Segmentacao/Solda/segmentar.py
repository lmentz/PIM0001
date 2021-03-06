# Colorizador de imagens cinza
# by: Lucas Litter Mentz

import numpy as np
import cv2
from sys import argv

fundo = 0
limiar = 126
areaMinima = 0
contagem = dict()

def luminance(pix):
	b,g,r = pix
	lumi = 0.2126*r + 0.7152*g + 0.0722*b
	return lumi

def limiarizar(img):
	global limiar
	y, x = len(img), len(img[0])
	nimg = np.zeros((y, x), np.uint8)
	for i in xrange(0, y):
		for j in xrange(0, x):
			if fundo == 0:
				nimg[i,j] = int(luminance(img[i,j]) >= limiar)
			else:
				nimg[i,j] = int(luminance(img[i,j]) < limiar)
	return nimg

def rotular(label, img, aux, y, x):
	fila = [(y,x)]
	contagem[label] = 0
	while len(fila) > 0:
		y,x = fila.pop()
		aux[y, x] = label
		contagem[label] += 1
		''' Acima, direita, abaixo, esquerda '''
		if y > 0:
			if img[y,x] == img[y-1, x] and aux[y-1, x] == -1: fila.append((y-1, x))
		if x < len(img[0]) - 1:
			if img[y,x] == img[y, x+1] and aux[y, x+1] == -1: fila.append((y, x+1))
		if y < len(img) - 1:
			if img[y,x] == img[y+1, x] and aux[y+1, x] == -1: fila.append((y+1, x))
		if x > 0:
			if img[y,x] == img[y, x-1] and aux[y, x-1] == -1: fila.append((y, x-1))

def identify(img):
	y, x = len(img), len(img[0])
	aux = np.zeros((y, x), int)
	aux.fill(-1)
	label = 1
	# checar bordas verticais esquerda e direita
	for i in xrange(0, y):
		rotular(0, img, aux, i, 0)
		rotular(0, img, aux, i, x-1)
	# checar bordas horizontais cima e baixo
	for j in xrange(1, x-1):
		rotular(0, img, aux, 0, j)
		rotular(0, img, aux, y-1, j)
	# marcar normalmente o que nao eh fundo
	for i in xrange(1, y-1):
		for j in xrange(1, x-1):
			if aux[i,j] == -1:
				#rotular(img[i,j], img, aux, i, j)
				if img[i,j] == fundo:
					rotular(0, img, aux, i, j)
				else:
					rotular(label, img, aux, i, j)
					label += 1
	return aux

def segment(img, aux):
	global areaMinima, fundo
	y, x = len(img), len(img[0])
	out = np.zeros(img.shape, np.uint8)
	for i in xrange(0, y):
		for j in xrange(0, x):
			#if (aux[i,j] != fundo):
			if (aux[i,j] != fundo) and (contagem[aux[i,j]] >= areaMinima):
				out[i,j] = img[i,j]
	return out

if __name__ == '__main__':
	x, y, l = 10, 10, 0
	path = 'garbage'

	''' Ler variaveis da linha de comando '''
	#if len(argv) >= 5:
	if len(argv) >= 4:
		path = argv[1]
		limiar = int(argv[2])
		fundo = int(argv[3])
		areaMinima = int(argv[4])
	else:
		print("Uso: python %s <caminho da imagem> <limiar> <fundo> <areaminima>\n"
			  "     fundo: 0 para preto, 1 para branco\n"
			  "     limiar: Nivel de luminosidade para limiarizacao [0,255]\n"
			  "     areaminima: Tamanho minimo para selecionar uma area\n"
			  "---- O programa gera um arquivo de saida "
			  "(<caminho da imagem>_segmentada.png) no diretorio atual."
			  % argv[0])
		sys.exit(1)

	

	img = cv2.imread(path)
	y, x = len(img), len(img[0])
	nimg = limiarizar(img)
	aux = identify(nimg)
	#print(aux)
	#print(contagem)
	outimg = segment(img, aux)

	newPath = path.split('.')[0]
	cv2.imwrite(newPath + '_segmentada.png', outimg)

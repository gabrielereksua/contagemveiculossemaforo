import cv2
import numpy as np
from time import sleep
from constantes import *


def pega_centro(x, y, largura, altura):
    """
    :param x: x do objeto
    :param y: y do objeto
    :param largura: largura do objeto
    :param altura: altura do objeto
    :return: tupla que contém as coordenadas do centro de um objeto
    """
    x1 = largura // 2
    y1 = altura // 2
    cx = x + x1
    cy = y + y1
    return cx, cy


def set_info(detec, pos_ref_via=0):
    global carros_direita
    global carros_esquerda
    for (x, y) in detec:
        if (pos_linha + offset) > y > (pos_linha - offset):
            if x < pos_ref_via:
            	carros_esquerda += 1
            else:
            	carros_direita += 1
            cv2.line(frame1, (25, pos_linha), (1200, pos_linha), (0, 127, 255), 3)
            detec.remove((x, y))
            print("Carros detectados até o momento (esquerda): " + str(carros_esquerda))
            print("Carros detectados até o momento (direita): " + str(carros_direita))


def show_info(frame1, dilatada):

    text_esquerda = f'Carros (E): {carros_esquerda}'
    text_direita = f'Carros (D): {carros_direita}'
    cv2.putText(frame1, text_esquerda, (20, 70), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 255), 5)
    cv2.putText(frame1, text_direita, (20, 130), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 255), 5)
    cv2.imshow("Video Original", frame1)
    #cv2.imshow("Detectar", dilatada)


carros = caminhoes = 0
carros_direita = 0
carros_esquerda = 0
cap = cv2.VideoCapture('videos/highway.mp4')
subtracao = cv2.bgsegm.createBackgroundSubtractorMOG()  # Pega o fundo e subtrai do que está se movendo

esquerda = False

while True:

    ret, frame1 = cap.read()  # Pega cada frame do vídeo
    
    linhas, colunas, _ = frame1.shape
    
    linha_central = linhas // 2
    coluna_central = colunas // 2
    
    pos_ref_via = coluna_central
    #frame1 = frame1[linha_central-200:linha_central+200, coluna_central-400:coluna_central+400,:]
    #if not esquerda:
    # 	frame1 = frame1[:,coluna_central:,:]
    #else:
    #	frame1 = frame1[:,:coluna_central,:]
    
    
    tempo = float(1 / delay)
    sleep(tempo)  # Dá um delay entre cada processamento
    grey = cv2.cvtColor(frame1, cv2.COLOR_BGR2GRAY)  # Pega o frame e transforma para preto e branco
    blur = cv2.GaussianBlur(grey, (3, 3), 5)  # Faz um blur para tentar remover as imperfeições da imagem
    img_sub = subtracao.apply(blur)  # Faz a subtração da imagem aplicada no blur
    dilat = cv2.dilate(img_sub, np.ones((5, 5)))  # "Engrossa" o que sobrou da subtração
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (
        5, 5))  # Cria uma matriz 5x5, em que o formato da matriz entre 0 e 1 forma uma elipse dentro
    dilatada = cv2.morphologyEx(dilat, cv2.MORPH_CLOSE, kernel)  # Tenta preencher todos os "buracos" da imagem
    dilatada = cv2.morphologyEx(dilatada, cv2.MORPH_CLOSE, kernel)

    contorno, img = cv2.findContours(dilatada, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    cv2.line(frame1, (25, pos_linha), (730, pos_linha), (255, 127, 0), 3)
    for (i, c) in enumerate(contorno):
        (x, y, w, h) = cv2.boundingRect(c)
        validar_contorno = (w >= largura_min) and (h >= altura_min)
        if not validar_contorno:
            continue

        cv2.rectangle(frame1, (x, y), (x + w, y + h), (0, 255, 0), 1)
        centro = pega_centro(x, y, w, h)
        detec.append(centro)
        cv2.circle(frame1, centro, 4, (0, 0, 255), -1)

    set_info(detec, pos_ref_via)
    show_info(frame1, dilatada)

    if cv2.waitKey(1) == 27:
        break

cv2.destroyAllWindows()
cap.release()


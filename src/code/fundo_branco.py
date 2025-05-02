import cv2
import numpy as np
import cardData
import utils


def readCard():
    phoneCamFeed = True  # Flag indicando se as imagens estão sendo lidas ao vivo da câmera do celular ou de um arquivo de imagem
    pathImage = 'testImages/tiltright.jpg'  # Nome do arquivo da imagem
    cam = cv2.VideoCapture(1)  # Usa a fonte de vídeo 1 = celular; 0 = webcam do computador

    # Ajustado para a altura e largura reais de um card de Pokémon (6,6 cm x 8,8 cm)
    widthCard = utils.getWidthCard()
    heightCard = utils.getHeightCard()

    while True:
        # Cria uma imagem preta em branco
        blackImg = np.zeros((heightCard, widthCard, 3), np.uint8)

        # Verifica se está usando a câmera do celular ou uma imagem salva
        if phoneCamFeed:
            # Lê o quadro e rotaciona 90 graus, pois o vídeo vem na horizontal
            check, frame = cam.read()
            rot90frame = cv2.rotate(frame, cv2.ROTATE_90_CLOCKWISE)
            rot90frame = cv2.resize(rot90frame, (widthCard, heightCard))
        else:
            # Lê a imagem salva e a redimensiona para normalizar
            pic = cv2.imread(pathImage)
            rot90frame = pic.copy()
        
        # Converte a imagem para escala de cinza
        grayFrame = cv2.cvtColor(rot90frame, cv2.COLOR_BGR2GRAY)
        grayFrame = cv2.equalizeHist(grayFrame)
        # Aplica um desfoque na imagem para reduzir o ruído
        blurredFrame = cv2.GaussianBlur(grayFrame, (7, 7), 1)



        # Usa a detecção de bordas de Canny para identificar as bordas
        edgedFrame = cv2.Canny(image=blurredFrame, threshold1=100, threshold2=200)

        # Refina as bordas
        kernel = np.ones((5, 5))
        frameDial = cv2.dilate(edgedFrame, kernel, iterations=2)
        frameThreshold = cv2.erode(frameDial, kernel, iterations=1)

        # Obtém os contornos da imagem
        contourFrame = rot90frame.copy()
        bigContour = rot90frame.copy()
        contours, hierarchy = cv2.findContours(frameThreshold, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        cv2.drawContours(contourFrame, contours, -1, (0, 255, 0), 10)

        imgWarpColored = blackImg  # Define imgWarpColored
        # Obtém o maior contorno
        corners, maxArea = utils.biggestContour(contours)

        
        if len(corners) == 4:
            corners = [corners[0][0], corners[1][0], corners[2][0], corners[3][0]]
            corners = utils.reorderCorners(corners)  # Reordena os cantos para [topLeft, topRight, bottomLeft, bottomRight]
            # cv2.drawContours(bigContour, corners, -1, (0, 255, 0), 10)
            bigContour = utils.drawRectangle(bigContour, corners)
            pts1 = np.float32(corners)
            pts2 = np.float32([[0, 0], [widthCard, 0], [0, heightCard], [widthCard, heightCard]])
            # Cria uma matriz que transforma o card detectado em um retângulo vertical
            matrix = cv2.getPerspectiveTransform(pts1, pts2)
            # Transforma o card em um retângulo com dimensões widthCard x heightCard
            imgWarpColored = cv2.warpPerspective(rot90frame, matrix, (widthCard, heightCard))

        # Redimensiona todas as imagens para as mesmas dimensões
        # Nota: imgWarpColored já está redimensionada e matchingCard será redimensionada em utils.getMatchingCard()
        rot90frame = cv2.resize(rot90frame, (widthCard, heightCard))
        grayFrame = cv2.resize(grayFrame, (widthCard, heightCard))
        blurredFrame = cv2.resize(blurredFrame, (widthCard, heightCard))
        edgedFrame = cv2.resize(edgedFrame, (widthCard, heightCard))
        contourFrame = cv2.resize(contourFrame, (widthCard, heightCard))
        bigContour = cv2.resize(bigContour, (widthCard, heightCard))

        # Verifica se um card correspondente foi encontrado e, se sim, exibe-o
        #found, matchingCard = utils.findCard(imgWarpColored.copy())  # Verifica se um card correspondente foi encontrado

        
        # Um array contendo todas as 8 imagens
        imageArr = ([rot90frame, grayFrame, blurredFrame, edgedFrame],
                    [contourFrame, bigContour, imgWarpColored, imgWarpColored])

        # Rótulos para cada imagem
        labels = [["Original", "Cinza", "Desfocada", "Binarizada"],
                  ["Contornos", "Maior Contorno", "Perspectiva Corrigida", "Card Correspondente"]]

        # Empilha todas as 8 imagens em uma só e adiciona os rótulos
        stackedImage = utils.makeDisplayImage(imageArr, labels)

        # Exibe a imagem
        cv2.imshow("Card Finder", stackedImage)

        if not phoneCamFeed:  # Se estiver lendo uma imagem salva, mantém a exibição até que uma tecla seja pressionada
            #if not found:  # Se um card correspondente não foi encontrado
                #print('Tente outra imagem. O card não foi encontrado.')
            cv2.waitKey(0)  # Mantém a janela aberta até que qualquer tecla seja pressionada
            break
        elif cv2.waitKey(1) & 0xFF == ord('q'):  # Se estiver lendo de um vídeo, sai se a tecla 'q' for pressionada
            break
        #elif found:  # Se a entrada for um vídeo e um card correspondente foi encontrado
            #print('\n\nPressione qualquer tecla para sair.')
            #cv2.waitKey(0)
            #break

    # Encerra a câmera e fecha a janela de exibição
    cam.release()
    cv2.destroyAllWindows()


if __name__ == '__main__':
    isFirst = False  # True se for a primeira vez executando este código; criará um novo banco de dados
    if isFirst:
        cardData.createDatabase()
    readCard()  # Encontra e lê de uma imagem salva ou de uma câmera ao vivo

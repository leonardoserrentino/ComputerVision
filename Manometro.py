import cv2
import time
import numpy as np

#Input dati sulla struttura del manometro
min_angle = float(input("Inserire l'angolo minimo: "))
max_angle = float(input("Inserire l'angolo massimo: "))
min_value = 0
max_value = float(input("Inserire il valore massimo: "))

#Utilizzo i dati in input per settare i range con cui mappare angoli->valori
angle_range = (max_angle - min_angle)
value_range = (max_value - min_value)

#Configurazione Camera
cap = cv2.VideoCapture(0)

#Metodo per fare la media dei cerchi rilevati
def avg_circles(circles, b):
    avg_x=0
    avg_y=0
    avg_r=0
    for i in range(b):
        avg_x = avg_x + circles[0][i][0]
        avg_y = avg_y + circles[0][i][1]
        avg_r = avg_r + circles[0][i][2]
    avg_x = int(avg_x/(b))
    avg_y = int(avg_y/(b))
    avg_r = int(avg_r/(b))
    return avg_x, avg_y, avg_r

#Calcola la distanza di due punti date le coordinate
def dist_2_pts(x1, y1, x2, y2):
    return np.sqrt((x2 - x1)**2 + (y2 - y1)**2)

while(cap.isOpened()): 
    while True:
        try:
            success, img = cap.read()
            cv2.imshow('Camera', img)

            #Elaborazione immagine
            blurredImg = cv2.GaussianBlur(img, (5,5), 3)
            gray = cv2.cvtColor(blurredImg, cv2.COLOR_BGR2GRAY)  #convert to gray
            height, width = img.shape[:2]
            
            #Identifica dove si trova il cerchio principale (contorno manometro)
            #Tutti i cerchi più grandi
            circles = cv2.HoughCircles(gray, cv2.HOUGH_GRADIENT, 1, 20, np.array([]), 100, 50, int(height*0.35), int(height*0.48))
            a,b,c = circles.shape
            #Filtra facendo la media tra i vari cerchi trovati (esempio interno ed esterno manometro)
            x,y,r = avg_circles(circles, b)
            
            #Elabora immagine nuovamente per le linee
            gray2 = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

            thresh = 175
            maxValue = 255

            th, dst2 = cv2.threshold(gray2, thresh, maxValue, cv2.THRESH_BINARY_INV);

            #Detection delle linee principali nell'immagine con il cerchio
            minLineLength = 50
            maxLineGap = 0
            lines = cv2.HoughLinesP(image=dst2, rho=3, theta=np.pi / 180, threshold=100,minLineLength=minLineLength, maxLineGap=0)

            #Creo lista di possibili linee candidate
            final_line_list = []

            #Imposto i Bound in modo che le linee candidate siano piu vicine possibili al centro (lancetta parte da li)
            diff1LowerBound = 0.15
            diff1UpperBound = 0.25
            diff2LowerBound = 0.5
            diff2UpperBound = 1.0
            for i in range(0, len(lines)):
                for x1, y1, x2, y2 in lines[i]:
                    diff1 = dist_2_pts(x, y, x1, y1)  
                    diff2 = dist_2_pts(x, y, x2, y2)  
                    if (diff1 > diff2):
                        temp = diff1
                        diff1 = diff2
                        diff2 = temp
                    if (((diff1<diff1UpperBound*r) and (diff1>diff1LowerBound*r) and (diff2<diff2UpperBound*r)) and (diff2>diff2LowerBound*r)):
                        line_length = dist_2_pts(x1, y1, x2, y2)
                        final_line_list.append([x1, y1, x2, y2])

            #Do per scontato che la prima linea sia quella buona
            x1 = final_line_list[0][0]
            y1 = final_line_list[0][1]
            x2 = final_line_list[0][2]
            y2 = final_line_list[0][3]
            cv2.line(img, (x1, y1), (x2, y2), (0, 255, 0), 2)

            #Utilizzo trigonometria per risolvere l'angolatura in modulo pi/2 (90 gradi)
            dist_pt_0 = dist_2_pts(x, y, x1, y1)
            dist_pt_1 = dist_2_pts(x, y, x2, y2)
            if (dist_pt_0 > dist_pt_1):
                x_angle = x1 - x
                y_angle = y - y1
            else:
                x_angle = x2 - x
                y_angle = y - y2
            res = np.arctan(np.divide(float(y_angle), float(x_angle)))

            #Identifico il quadrante a cui sottrarre il valore assoluto in 90 gradi
            res = np.rad2deg(res)
            if x_angle > 0 and y_angle > 0:  #Primo Quadrante
                final_angle = 270 - res
            if x_angle < 0 and y_angle > 0:  #Secondo Quadrante
                final_angle = 90 - res
            if x_angle < 0 and y_angle < 0:  #Terzo Quadrante
                final_angle = 90 - res
            if x_angle > 0 and y_angle < 0:  #Quarto Quadrante
                final_angle = 270 - res

            #Calcolo il valore dell'angolo mappandolo con la scala del manometro
            val = (((final_angle - min_angle) * value_range) / angle_range) + min_value
            print ("Valore attuale: %s BAR" %("%.2f" % val))

            #Interrompi imshow (convenzione)
            if cv2.waitKey(30) & 0xff == ord('q'):
                break

        except ValueError as ve:
            x = "do nothing"
        except IndexError:
            x = "do nothing"
            
    #Process Kill per non lasciare pendenze di sistema
    cap.release()
    cv2.destroyAllWindows()
else:
    #Controllare bene l'id di VideoCapture perche sia coerente con il numero di cams disponibili
    print("Alert ! Camera disconnected")
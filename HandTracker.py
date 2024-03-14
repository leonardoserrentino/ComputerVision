import cv2
import mediapipe as mp
import time

cap = cv2.VideoCapture(0) #id of camera

mpHands = mp.solutions.hands
hands = mpHands.Hands()
mpDraw = mp.solutions.drawing_utils

#tracking time for fps
pTime = 0
cTime = 0

while True:
    success, img = cap.read()
    imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    results = hands.process(imgRGB)
    #print(results.multi_hand_landmarks)

    if results.multi_hand_landmarks:
        for handLms in results.multi_hand_landmarks:
            for id,lm in enumerate(handLms.landmark):
                #print(id,lm)
                #x,y,z con scala corretta
                h,w,d = img.shape
                cx, cy = int(lm.x*w), int(lm.y*h)
                print(id, cx, cy) 
                #Cambiando l'id da 0 a 20 possiamo tracciare il movimento di una delle giunture del tracker della mano, come l'indice, il pollice, o la punta del mignolo, o la base della mano
                if id==0:
                    cv2.circle(img, (cx,cy), 15, (255,0,255), cv2.FILLED)
            mpDraw.draw_landmarks(img, handLms, mpHands.HAND_CONNECTIONS)
             

    """
    #FPS 
    cTime = time.time()
    fps = 1/(cTime-pTime)
    pTime = cTime
    cv2.putText(img, str(int(fps)), (10,70), cv2.FONT_HERSHEY_PLAIN, 3, (255,0,255), 3)
    """

    cv2.imshow("Image", img)
    cv2.waitKey(1)
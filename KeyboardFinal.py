import cv2
from cvzone.HandTrackingModule import HandDetector
import time
from pynput.keyboard import Controller, Key
import numpy as np 

# Inisialisasi Kamera
cap = cv2.VideoCapture(0)
cap.set(3, 1280)
cap.set(4, 720)

# Inisialisasi Detektor Tangan dan Kontroler Keyboard
detector = HandDetector(detectionCon=0.8, maxHands=1)
keyboard = Controller()

# Variabel untuk sistem cooldown
CLICK_DELAY = 0.35
last_click_time = 0

# Layout Keyboard
keys = [["Q", "W", "E", "R", "T", "Y", "U", "I", "O", "P", "BACKSPACE"],
        ["A", "S", "D", "F", "G", "H", "J", "K", "L", ";", "ENTER"],
        ["Z", "X", "C", "V", "B", "N", "M", ",", ".", "/"],
        [" "]]
finalText = ""

# Class Button tidak diubah
class Button():
    def __init__(self, pos, text, size=[85, 85]):
        self.pos = pos
        self.size = size
        self.text = text

# Logika pembuatan layout tombol tidak diubah
buttonList = []
x_start, y_start, gap = 50, 50, 15
y_pos = y_start
for row in keys:
    x_pos = x_start
    for key in row:
        size = [85, 85]
        if key == "BACKSPACE" or key == "ENTER":
            size = [185, 85]
        elif key == " ":
            size = [600, 85]
            x_pos = 250
        
        buttonList.append(Button([x_pos, y_pos], key, size))
        x_pos += size[0] + gap
    y_pos += 85 + gap


# Fungsi gambar semua tombol dengan efek transparan
def drawAll(img, buttonList):
    # Buat sebuah lapisan overlay kosong untuk menggambar tombol transparan
    overlay = img.copy()
    
    for button in buttonList:
        x, y = button.pos
        w, h = button.size
        # Gambar kotak solid pada lapisan overlay
        cv2.rectangle(overlay, button.pos, (x + w, y + h), (255, 0, 255), cv2.FILLED)
    
    # Blend lapisan overlay dengan gambar asli untuk menciptakan efek transparan
    alpha = 0.2 # Tingkat transparansi (0.0 = full transparan, 1.0 = solid)
    img = cv2.addWeighted(overlay, alpha, img, 1 - alpha, 0)

    # Gambar teks di atas gambar yang sudah di-blend agar teks tetap solid
    for button in buttonList:
        x, y = button.pos
        w, h = button.size
        text = button.text
        font = cv2.FONT_HERSHEY_PLAIN
        font_scale = 4
        font_thickness = 4
        
        if text == "BACKSPACE":
            font_scale = 2
            font_thickness = 2
        elif text == "ENTER":
            font_scale = 3
            font_thickness = 3
        elif text == " ":
             text = "Space"
        
        text_size = cv2.getTextSize(text, font, font_scale, font_thickness)[0]
        text_x = x + (w - text_size[0]) // 2
        text_y = y + (h + text_size[1]) // 2
        
        cv2.putText(img, text, (text_x, text_y), font, font_scale, (255, 255, 255), font_thickness)
        
    return img

# ===== Loop Utama Program =====
while True:
    success, img = cap.read()
    img = cv2.flip(img, 1)

    hands, img = detector.findHands(img, flipType=False)
    img = drawAll(img, buttonList)

    if hands:
        lmList = hands[0]['lmList']
        if lmList:
            for button in buttonList:
                x, y = button.pos
                w, h = button.size

                if x < lmList[8][0] < x + w and y < lmList[8][1] < y + h:
                    # Logika highlight tombol yang disentuh
                    # Gambar ulang tombol yang disentuh dengan warna solid (tidak transparan)
                    cv2.rectangle(img, button.pos, (x + w, y + h), (255, 0, 255), cv2.FILLED)
                    
                    # Tulis ulang teks di atasnya agar terlihat
                    text = button.text
                    font = cv2.FONT_HERSHEY_PLAIN
                    font_scale = 4
                    font_thickness = 4
                    if text == "BACKSPACE":
                        font_scale = 2
                        font_thickness = 2
                    elif text == "ENTER":
                        font_scale = 3
                        font_thickness = 3
                    elif text == " ":
                        text = "Space"
                    text_size = cv2.getTextSize(text, font, font_scale, font_thickness)[0]
                    text_x = x + (w - text_size[0]) // 2
                    text_y = y + (h + text_size[1]) // 2
                    cv2.putText(img, text, (text_x, text_y), font, font_scale, (255, 255, 255), font_thickness)
                    
                    length, info, img = detector.findDistance(lmList[8][1:], lmList[12][1:], img)

                    current_time = time.time()
                    if length < 40 and (current_time - last_click_time) > CLICK_DELAY:
                        last_click_time = current_time
                        
                        # Logika klik tidak ada yang diubah
                        if button.text == "BACKSPACE":
                            keyboard.press(Key.backspace)
                            finalText = finalText[:-1]
                        elif button.text == "ENTER":
                            keyboard.press(Key.enter)
                            finalText += "\n"
                        elif button.text == " ":
                            keyboard.press(Key.space)
                            finalText += " "
                        else:
                            keyboard.press(button.text)
                            finalText += button.text

                        # Efek klik (hijau) tetap solid
                        cv2.rectangle(img, button.pos, (x + w, y + h), (0, 255, 0), cv2.FILLED)
                        cv2.putText(img, text, (text_x, text_y), font, font_scale, (255, 255, 255), font_thickness)

    # Menampilkan area teks
    cv2.rectangle(img, (50, 450), (1250, 650), (175, 0, 175), cv2.FILLED)
    
    y0, dy = 510, 80
    for i, line in enumerate(finalText.split('\n')):
        displayText = line
        if i == len(finalText.split('\n')) - 1:
            if (time.time() * 2) % 2 < 1:
                displayText += "|"
        
        y = y0 + i * dy
        cv2.putText(img, displayText, (60, y), cv2.FONT_HERSHEY_PLAIN, 5, (255, 255, 255), 5)

    cv2.imshow("Virtual Keyboard", img)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
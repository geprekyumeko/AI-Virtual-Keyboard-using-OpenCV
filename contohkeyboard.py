import cv2
from cvzone.HandTrackingModule import HandDetector
from time import sleep
import cvzone
from pynput.keyboard import Controller

# Inisialisasi Kamera
cap = cv2.VideoCapture(0)
cap.set(3, 1280)
cap.set(4, 720)

# Inisialisasi Detektor dan Keyboard
detector = HandDetector(detectionCon=0.8, maxHands=2)
keyboard = Controller()

# Tata Letak Keyboard
keys = [["Q", "W", "E", "R", "T", "Y", "U", "I", "O", "P"],
        ["A", "S", "D", "F", "G", "H", "J", "K", "L", ";"],
        ["Z", "X", "C", "V", "B", "N", "M", ",", ".", "/"]]
finalText = ""

# Class untuk merepresentasikan tombol
class Button():
    def __init__(self, pos, text, size=[85, 85]):
        self.pos = pos
        self.size = size
        self.text = text

# Membuat objek-objek tombol
buttonList = []
for i in range(len(keys)):
    for j, key in enumerate(keys[i]):
        buttonList.append(Button([100 * j + 50, 100 * i + 50], key))

# Fungsi untuk menggambar semua tombol
def drawAll(img, buttonList):
    for button in buttonList:
        x, y = button.pos
        w, h = button.size
        cv2.rectangle(img, button.pos, (x + w, y + h), (255, 0, 255), cv2.FILLED)
        cv2.putText(img, button.text, (x + 20, y + 65),
                    cv2.FONT_HERSHEY_PLAIN, 4, (255, 255, 255), 4)
    return img

# Loop Utama
while True:
    success, img = cap.read()
    img = cv2.flip(img, 1) # Balik gambar agar seperti cermin

    # Deteksi tangan
    hands, img = detector.findHands(img, flipType=False)
    
    # Gambar keyboard
    img = drawAll(img, buttonList)

    # Proses jika tangan terdeteksi
    if hands:
        lmList = hands[0]['lmList']
        if lmList:
            for button in buttonList:
                x, y = button.pos
                w, h = button.size

                # Cek hover: Ujung jari telunjuk (indeks 1 dari lmList[8]) berada di dalam tombol
                if x < lmList[8][1] < x + w and y < lmList[8][2] < y + h:
                    # Ubah warna tombol saat disentuh (hover)
                    cv2.rectangle(img, (x - 5, y - 5), (x + w + 5, y + h + 5), (175, 0, 175), cv2.FILLED)
                    cv2.putText(img, button.text, (x + 20, y + 65),
                                cv2.FONT_HERSHEY_PLAIN, 4, (255, 255, 255), 4)

                    # --- PERBAIKAN UTAMA DI SINI ---
                    # Hitung jarak dan tangkap semua 3 nilai return: length, info, img
                    length, info, img = detector.findDistance(lmList[8][1:], lmList[12][1:], img=img)
                    
                    # Cek klik: jika jarak sangat dekat
                    if length < 40:
                        keyboard.press(button.text)
                        # Ubah warna tombol saat diklik
                        cv2.rectangle(img, button.pos, (x + w, y + h), (0, 255, 0), cv2.FILLED)
                        cv2.putText(img, button.text, (x + 20, y + 65),
                                    cv2.FONT_HERSHEY_PLAIN, 4, (255, 255, 255), 4)
                        finalText += button.text
                        sleep(0.3) # Jeda untuk mencegah klik ganda

    # Tampilkan area teks
    cv2.rectangle(img, (50, 350), (700, 450), (175, 0, 175), cv2.FILLED)
    cv2.putText(img, finalText, (60, 430),
                cv2.FONT_HERSHEY_PLAIN, 5, (255, 255, 255), 5)

    # Tampilkan jendela
    cv2.imshow("Virtual Keyboard", img)
    # Keluar dari loop dengan menekan 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Lepaskan kamera dan tutup semua jendela
cap.release()
cv2.destroyAllWindows()
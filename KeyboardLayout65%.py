import cv2
from cvzone.HandTrackingModule import HandDetector
import time
from pynput.keyboard import Controller, Key
import numpy as np

# Inisialisasi Kamera
cap = cv2.VideoCapture(0)
# Usahakan menggunakan resolusi yang lebih umum seperti 1280x720
cap.set(3, 1280)
cap.set(4, 720)

# Inisialisasi Detektor Tangan dan Kontroler Keyboard
detector = HandDetector(detectionCon=0.8, maxHands=1)
keyboard = Controller()

#Variabel State untuk Tombol Modifier
is_caps_on = False
is_shift_on = False

# Mapping untuk Tombol Spesial & Shift
# Mapping teks tombol ke objek Key dari pynput
special_key_map = {
    "Backspace": Key.backspace, "Tab": Key.tab, "Enter": Key.enter,
    "Shift": Key.shift, "Ctrl": Key.ctrl, "Alt": Key.alt, "Win": Key.cmd, # Key.cmd untuk tombol Windows/Command
    "Caps": Key.caps_lock, "ESC": Key.esc, "Space": Key.space,
    "Home": Key.home, "Del": Key.delete, "PgUp": Key.page_up, "PgDn": Key.page_down,
    "Up": Key.up, "Down": Key.down, "Left": Key.left, "Right": Key.right
}

# Mapping karakter dasar ke versi Shift-nya
shift_map = {
    "1": "!", "2": "@", "3": "#", "4": "$", "5": "%", "6": "^", "7": "&", "8": "*", "9": "(", "0": ")",
    "-": "_", "=": "+", "[": "{", "]": "}", "\\": "|", ";": ":", "'": "\"", ",": "<", ".": ">", "/": "?"
}

# Layout Keyboard Baru Sesuai Desain
# Layout ini merepresentasikan karakter utama yang akan diketik
keys = [
    ["ESC", "1", "2", "3", "4", "5", "6", "7", "8", "9", "0", "-", "=", "Backspace", "Home"],
    ["Tab", "q", "w", "e", "r", "t", "y", "u", "i", "o", "p", "[", "]", "\\", "Del"],
    ["Caps", "a", "s", "d", "f", "g", "h", "j", "k", "l", ";", "'", "Enter", "PgUp"],
    ["Shift", "z", "x", "c", "v", "b", "n", "m", ",", ".", "/", "Shift", "Up", "PgDn"],
    ["Ctrl", "Win", "Alt", "Space", "Alt", "Fn", "Left", "Down", "Right"]
]

finalText = ""

class Button():
    def __init__(self, pos, text, size, display_text=None):
        self.pos = pos
        self.size = size
        self.text = text # Teks fungsional (misal: "a" atau "Shift")
        self.display_text = display_text if display_text is not None else text # Teks yang ditampilkan

# Logika Pembuatan Layout Tombol yang Lebih Fleksibel
def create_button_layout(keys_layout):
    buttonList = []
    # Posisi awal dan ukuran dasar
    x_start, y_start = 10, 50
    key_w, key_h = 65, 65
    gap = 10

    y_pos = y_start
    for i, row in enumerate(keys_layout):
        x_pos = x_start
        for j, key in enumerate(row):
            w, h = key_w, key_h
            display = key

            # Atur ukuran kustom untuk tombol-tombol tertentu
            if key == "Backspace": w = 140
            elif key == "\\": w = 105
            elif key == "Tab": w = 100
            elif key == "Enter": w = 170
            elif key == "Caps": w = 110
            elif i == 3 and j == 0: w = 140 # Shift Kiri
            elif i == 3 and j == 11: w = 140 # Shift Kanan
            elif key == "Space": w = 515
            elif key in ["Ctrl", "Win", "Alt", "Fn"]: w = 80

            # Kustomisasi teks display untuk tombol dengan 2 karakter
            if key == "1": display = "1!"
            elif key == "2": display = "2@"
            elif key == "3": display = "3#"
            elif key == "4": display = "4$"
            elif key == "5": display = "5%"
            elif key == "6": display = "6^"
            elif key == "7": display = "7&"
            elif key == "8": display = "8*"
            elif key == "9": display = "9("
            elif key == "0": display = "0)"
            elif key == "=": display = "=+"
            elif key == "-": display = "-_"
            elif key == "[": display = "[{"
            elif key == "]": display = "]}"
            elif key == "\\": display = "\\|"
            elif key == ";": display = ";:"
            elif key == "'": display = "'\""
            elif key == ",": display = ",<"
            elif key == ".": display = ".>"
            elif key == "/": display = "/?"

            buttonList.append(Button([x_pos, y_pos], key, [w, h], display_text=display))
            x_pos += w + gap
        y_pos += h + gap
    return buttonList

buttonList = create_button_layout(keys)


# Fungsi Menggambar Tombol dengan State Aktif
def drawAll(img, buttonList):
    overlay = img.copy()
    alpha = 0.3 # Transparansi normal
    
    for button in buttonList:
        x, y = button.pos
        w, h = button.size
        
        # Tentukan warna berdasarkan state tombol
        bg_color = (255, 0, 255) # Ungu default
        
        # Beri warna berbeda jika Caps/Shift aktif
        if (button.text == "Caps" and is_caps_on) or \
           (button.text == "Shift" and is_shift_on):
            bg_color = (180, 0, 180) # Warna ungu lebih gelap/terang saat aktif
            
        cv2.rectangle(overlay, button.pos, (x + w, y + h), bg_color, cv2.FILLED)

    img = cv2.addWeighted(overlay, alpha, img, 1 - alpha, 0)

    # Gambar teks di atasnya agar solid
    for button in buttonList:
        x, y = button.pos
        w, h = button.size
        text = button.display_text
        
        # Atur ukuran font secara dinamis agar pas
        font_face = cv2.FONT_HERSHEY_PLAIN
        font_scale = 1
        font_thickness = 1
        text_size = cv2.getTextSize(text, font_face, font_scale, font_thickness)[0]
        
        # Coba perbesar font selama masih muat di dalam tombol
        max_scale = 5
        for scale in range(2, max_scale + 1):
            new_text_size = cv2.getTextSize(text, font_face, scale, font_thickness+1)[0]
            if new_text_size[0] < w - 20 and new_text_size[1] < h - 20:
                font_scale = scale
                font_thickness += 1
            else:
                break
        
        if len(text) > 3: # Perkecil font untuk teks panjang seperti Backspace
            font_scale = max(1, font_scale - 1)
            
        text_size = cv2.getTextSize(text, font_face, font_scale, font_thickness)[0]
        text_x = x + (w - text_size[0]) // 2
        text_y = y + (h + text_size[1]) // 2
        
        cv2.putText(img, text, (text_x, text_y), font_face, font_scale, (255, 255, 255), font_thickness)
        
    return img

# ===== Loop Utama Program =====
CLICK_DELAY = 0.4 # Sedikit diperlama untuk stabilitas
last_click_time = 0

while True:
    success, img = cap.read()
    if not success:
        continue
    img = cv2.flip(img, 1)

    hands, img = detector.findHands(img, flipType=False)
    img = drawAll(img, buttonList)

    if hands:
        lmList = hands[0]['lmList']
        if lmList:
            for button in buttonList:
                x, y = button.pos
                w, h = button.size

                # Deteksi hover (jari telunjuk di atas tombol)
                if x < lmList[8][0] < x + w and y < lmList[8][1] < y + h:
                    # Highlight tombol yang di-hover
                    cv2.rectangle(img, button.pos, (x + w, y + h), (175, 0, 175), cv2.FILLED)
                    # Tulis ulang teks
                    # (Untuk simplicitas, kita bisa skip redraw teks saat hover karena sudah ada di drawAll)

                    # Deteksi klik (jari telunjuk dan tengah bertemu)
                    length, info, img = detector.findDistance(lmList[8][1:], lmList[12][1:], img)
                    current_time = time.time()
                    
                    if length < 40 and (current_time - last_click_time) > CLICK_DELAY:
                        last_click_time = current_time
                        
                        key_to_press = button.text
                        
                        # Efek visual saat klik
                        cv2.rectangle(img, button.pos, (x + w, y + h), (0, 255, 0), cv2.FILLED)
                        
                        # Logika Klik yang Ditingkatkan
                        
                        # 1. Handle tombol toggle (Caps & Shift)
                        if key_to_press == "Caps":
                            is_caps_on = not is_caps_on
                            # pynput menangani state caps lock sendiri, jadi kita tidak perlu press
                            continue # Lanjut ke iterasi berikutnya
                        
                        if key_to_press == "Shift":
                            is_shift_on = not is_shift_on
                            continue

                        # Tombol Fn biasanya ditangani oleh hardware, jadi kita abaikan
                        if key_to_press == "Fn":
                            continue

                        # 2. Handle tombol spesial lainnya (Enter, Backspace, dll)
                        if key_to_press in special_key_map:
                            keyboard.press(special_key_map[key_to_press])
                            keyboard.release(special_key_map[key_to_press]) # Rilis segera untuk tombol non-modifier
                            if key_to_press == "Backspace":
                                finalText = finalText[:-1]
                            elif key_to_press == "Enter":
                                finalText += "\n"
                            elif key_to_press == "Space":
                                finalText += " "
                            elif key_to_press == "Tab":
                                finalText += "\t" # Tambah tab ke teks
                        
                        # 3. Handle tombol karakter (huruf, angka, simbol)
                        else:
                            # Tentukan karakter yang akan diketik
                            output_char = key_to_press
                            
                            # Jika shift aktif, gunakan map atau ubah jadi uppercase
                            if is_shift_on:
                                if key_to_press.isalpha():
                                    output_char = key_to_press.upper()
                                elif key_to_press in shift_map:
                                    output_char = shift_map[key_to_press]
                            else: # Jika shift tidak aktif
                                if key_to_press.isalpha():
                                    output_char = key_to_press.lower()

                            # Handle Caps Lock (hanya untuk huruf)
                            if key_to_press.isalpha() and is_caps_on:
                                # XOR: jika shift dan caps sama-sama on, hasilnya lowercase
                                if not is_shift_on:
                                    output_char = key_to_press.upper()
                                else:
                                    output_char = key_to_press.lower()
                            
                            keyboard.press(output_char)
                            finalText += output_char
                            
                            # Non-aktifkan Shift setelah digunakan (mode sekali pakai)
                            if is_shift_on:
                                is_shift_on = False

    # Menampilkan area teks
    cv2.rectangle(img, (10, 520), (1270, 710), (175, 0, 175), cv2.FILLED)
    
    # Menampilkan teks dengan word wrapping sederhana
    y0, dy = 560, 50
    for i, line in enumerate(finalText.split('\n')):
        displayText = line
        if i == len(finalText.split('\n')) - 1:
            if (time.time() * 2) % 2 < 1: # Kursor berkedip
                displayText += "|"
        
        y = y0 + i * dy
        cv2.putText(img, displayText, (20, y), cv2.FONT_HERSHEY_PLAIN, 4, (255, 255, 255), 4)

    cv2.imshow("Virtual Keyboard Layout 65%", img)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
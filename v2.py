from gtts import gTTS  # Thêm thư viện Google Text-to-Speech
import os
import pygame

def text_to_speech(text, filename="temp_speech.mp3", language='vi'):
    try:
        if pygame.mixer.music.get_busy():
            pygame.mixer.music.stop()
        pygame.mixer.music.unload()

        if os.path.exists(filename):
            try:
                os.remove(filename)
            except PermissionError:
                print("Không thể xóa file âm thanh cũ.")
                return False

        tts = gTTS(text=text, lang=language, slow=False)
        tts.save(filename)
        pygame.mixer.music.load(filename)
        pygame.mixer.music.play()

        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)

        return True
    except Exception as e:
        print("Lỗi khi phát âm thanh:", e)
        return False
# --- Init ---
pygame.init()
pygame.mixer.init()

text_to_speech("chào bạn")




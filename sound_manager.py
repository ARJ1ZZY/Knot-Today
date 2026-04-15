# sound_manager.py
import pygame
import settings as s
import os

class SoundManager:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        self._initialized = True
        self.sounds = {}
        self.enabled = s.SOUND_ENABLED
        self._load_sounds()
    
    def _load_sounds(self):
        sound_files = {
            "click": "click.wav",
            "correct": "correct.wav",
            "wrong": "wrong.wav",
            "win": "win.wav",
            "lose": "lose.wav"
        }
        
        sound_dir = os.path.join("assets", "sounds")
        os.makedirs(sound_dir, exist_ok=True)
        
        for name, filename in sound_files.items():
            path = os.path.join(sound_dir, filename)
            try:
                if os.path.exists(path):
                    sound = pygame.mixer.Sound(path)
                    sound.set_volume(s.SOUND_VOLUME)
                    self.sounds[name] = sound
                else:
                    self.sounds[name] = None
            except:
                self.sounds[name] = None
    
    def play(self, name):
        if self.enabled and name in self.sounds and self.sounds[name]:
            try:
                self.sounds[name].play()
            except:
                pass
    
    def toggle_mute(self):
        self.enabled = not self.enabled
        return self.enabled
    
    def get_mute_text(self):
        return "Unmute" if not self.enabled else "Mute"
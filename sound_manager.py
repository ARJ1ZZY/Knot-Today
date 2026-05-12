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
        self.current_music = None
        self.music_channel = None
        self.sfx_channel = None
        self.music_volume = s.SOUND_VOLUME
        self.sfx_volume = s.SOUND_VOLUME
        self._load_sounds()
    
    def _load_sounds(self):
        sound_files = {
            "hover": "hover.wav",
            "correct": "correct.wav",
            "incorrect": "incorrect.wav",
            "win": "win.mp3",
            "soundtrack": "soundtrack.mp3",
            "fail": "fail.mp3",
            "hint": "hint.wav"
        }
        
        sound_dir = os.path.join("assets", "sounds")
        os.makedirs(sound_dir, exist_ok=True)
        
        # Initialize channels: Channel 0 for music, Channel 1 for SFX
        pygame.mixer.set_num_channels(8)
        self.music_channel = pygame.mixer.Channel(0)
        self.sfx_channel = pygame.mixer.Channel(1)
        
        # Set channel volumes
        self.music_channel.set_volume(self.music_volume)
        self.sfx_channel.set_volume(self.sfx_volume)
        
        for name, filename in sound_files.items():
            path = os.path.join(sound_dir, filename)
            try:
                if os.path.exists(path):
                    sound = pygame.mixer.Sound(path)
                    if name == "soundtrack":
                        sound.set_volume(self.music_volume)
                    else:
                        sound.set_volume(self.sfx_volume)
                    self.sounds[name] = sound
                else:
                    self.sounds[name] = None
                    print(f"Warning: Sound file not found: {path}")
            except Exception as e:
                print(f"Error loading sound {name}: {e}")
                self.sounds[name] = None
    
    def play_music(self, name, loop=True):
        """Play background music - stops any current music first"""
        if not self.enabled:
            return
        
        # Don't restart if same music is already playing
        if self.current_music == name and self.music_channel and self.music_channel.get_busy():
            return
        
        # Stop current music if playing
        self.stop_music()
        
        if name in self.sounds and self.sounds[name]:
            try:
                if loop:
                    self.music_channel.play(self.sounds[name], loops=-1)
                else:
                    self.music_channel.play(self.sounds[name])
                self.current_music = name
            except:
                pass
    
    def play_sfx(self, name):
        """Play sound effect - interrupts current SFX"""
        if not self.enabled:
            return
        
        if name in self.sounds and self.sounds[name]:
            try:
                # Interrupt current SFX by stopping and playing on same channel
                self.sfx_channel.stop()
                self.sfx_channel.play(self.sounds[name])
            except:
                pass
    
    def stop_music(self):
        """Stop currently playing background music"""
        if self.music_channel:
            self.music_channel.stop()
        self.current_music = None
    
    def set_music_volume(self, volume):
        """Set background music volume (0.0 to 1.0)"""
        self.music_volume = max(0.0, min(1.0, volume))
        if self.music_channel:
            self.music_channel.set_volume(self.music_volume)
        if "soundtrack" in self.sounds and self.sounds["soundtrack"]:
            self.sounds["soundtrack"].set_volume(self.music_volume)
    
    def set_sfx_volume(self, volume):
        """Set sound effects volume (0.0 to 1.0)"""
        self.sfx_volume = max(0.0, min(1.0, volume))
        if self.sfx_channel:
            self.sfx_channel.set_volume(self.sfx_volume)
    
    def toggle_mute(self):
        self.enabled = not self.enabled
        if not self.enabled:
            self.stop_music()
        else:
            # Resume music if it was playing before mute
            if self.current_music == "soundtrack":
                self.play_music("soundtrack", loop=True)
        return self.enabled
    
    def get_mute_text(self):
        return "UNMUTE" if not self.enabled else "MUTE"
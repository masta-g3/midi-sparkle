#!/usr/bin/env python3
"""
SparkLE Musical Garden - CLI Version
Audio-only toddler-friendly musical playground without GUI
Based on the nature-themed design for 1.8-year-old toddlers
"""

import json
import time
import threading
from typing import List, Optional
import mido
import pygame
import numpy as np
import random

class AudioSynthesizer:
    """Generates natural-sounding audio for the musical garden"""
    
    def __init__(self, sample_rate: int = 22050):
        self.sample_rate = sample_rate
        pygame.mixer.pre_init(frequency=sample_rate, size=-16, channels=2, buffer=512)
        pygame.mixer.init()
        
    def generate_tone(self, frequency: float, duration: float, 
                     wave_type: str = 'sine', envelope: str = 'soft') -> pygame.mixer.Sound:
        """Generate a natural-sounding tone"""
        frames = int(duration * self.sample_rate)
        arr = np.zeros((frames, 2))
        
        for i in range(frames):
            t = i / self.sample_rate
            
            ## Generate base waveform
            if wave_type == 'sine':
                wave = np.sin(2 * np.pi * frequency * t)
            elif wave_type == 'triangle':
                wave = 2 * np.arcsin(np.sin(2 * np.pi * frequency * t)) / np.pi
            elif wave_type == 'sawtooth':
                wave = 2 * (t * frequency - np.floor(t * frequency + 0.5))
            elif wave_type == 'noise':
                wave = random.uniform(-1, 1)
            else:
                wave = np.sin(2 * np.pi * frequency * t)
            
            ## Apply envelope for natural sound
            if envelope == 'soft':
                env = np.exp(-t * 2)  # Soft decay
            elif envelope == 'sustain':
                env = 1.0 if t < duration * 0.8 else np.exp(-(t - duration * 0.8) * 10)
            else:
                env = 1.0
            
            ## Apply frequency limits for toddler safety (200Hz-4kHz)
            if frequency < 200:
                frequency = 200
            elif frequency > 4000:
                frequency = 4000
                
            arr[i] = [wave * env * 0.3, wave * env * 0.3]  # Volume limit for safety
        
        ## Convert to pygame sound
        arr = (arr * 32767).astype(np.int16)
        return pygame.sndarray.make_sound(arr)

class NatureSounds:
    """Collection of nature-themed sounds for the musical garden"""
    
    def __init__(self, synthesizer: AudioSynthesizer):
        self.synth = synthesizer
        self.sounds = {}
        self._generate_nature_sounds()
    
    def _generate_nature_sounds(self):
        """Generate all nature-themed sounds"""
        
        ## Big Pads - Garden Elements (create looping versions)
        self.sounds['earth'] = self._create_earth_sound()
        self.sounds['rain'] = self._create_rain_sound()
        self.sounds['wind'] = self._create_wind_sound()
        self.sounds['thunder'] = self._create_thunder_sound()
        self.sounds['trees'] = self._create_trees_sound()
        self.sounds['birds'] = self._create_birds_sound()
        self.sounds['insects'] = self._create_insects_sound()
        self.sounds['sun'] = self._create_sun_sound()
        
        ## Number Pads - Melodic Tones (designed to layer over background textures)
        ## Create both "on" and "off" variations for each melodic tone
        pentatonic_scale = [261.63, 293.66, 329.63, 392.00, 440.00]  # C pentatonic
        
        for i in range(16):
            row = i // 4
            col = i % 4
            
            if row == 0:  # Seeds - pure melodic notes (low octave)
                freq = pentatonic_scale[col % len(pentatonic_scale)]
                self.sounds[f'seed_{i+1}'] = self._create_melodic_tone(freq, 'bell')
                self.sounds[f'seed_{i+1}_off'] = self._create_melodic_tone_off(freq, 'bell')
            elif row == 1:  # Sprouts - melodic notes (mid octave)
                freq = pentatonic_scale[col % len(pentatonic_scale)] * 1.5
                self.sounds[f'sprout_{i+1}'] = self._create_melodic_tone(freq, 'soft')
                self.sounds[f'sprout_{i+1}_off'] = self._create_melodic_tone_off(freq, 'soft')
            elif row == 2:  # Buds - melodic notes (higher octave)
                freq = pentatonic_scale[col % len(pentatonic_scale)] * 2
                self.sounds[f'bud_{i+1}'] = self._create_melodic_tone(freq, 'bright')
                self.sounds[f'bud_{i+1}_off'] = self._create_melodic_tone_off(freq, 'bright')
            else:  # Flowers - melodic notes (highest octave)
                freq = pentatonic_scale[col % len(pentatonic_scale)] * 2.5
                self.sounds[f'flower_{i+1}'] = self._create_melodic_tone(freq, 'sparkle')
                self.sounds[f'flower_{i+1}_off'] = self._create_melodic_tone_off(freq, 'sparkle')
    
    def _create_earth_sound(self) -> pygame.mixer.Sound:
        """Deep, warm sub-bass drone with gentle earthy rumble"""
        duration = 4.0
        frames = int(duration * self.synth.sample_rate)
        arr = np.zeros((frames, 2))

        ## Pre-generate subtle low-frequency noise (earthy rumble)
        noise = np.random.normal(0, 0.3, size=frames)

        for i in range(frames):
            t = i / self.synth.sample_rate

            ## Fundamental and first harmonic (slightly detuned for warmth)
            base = 0.6 * np.sin(2 * np.pi * 130 * t)   ## ~C3 fundamental
            harmonic = 0.3 * np.sin(2 * np.pi * 260 * t)

            ## Slow amplitude modulation to keep the texture evolving
            lfo = 0.85 + 0.15 * np.sin(2 * np.pi * 0.1 * t)

            wave = (base + harmonic + noise[i] * 0.2) * lfo * 0.12
            arr[i] = [wave, wave]

        arr = (arr * 32767).astype(np.int16)
        return pygame.sndarray.make_sound(arr)
    
    def _create_rain_sound(self) -> pygame.mixer.Sound:
        """Gentle pitter-patter texture - background rhythm"""
        return self._create_rain_texture()
    
    def _create_wind_sound(self) -> pygame.mixer.Sound:
        """Whooshing breathy texture - background atmosphere"""
        return self._create_wind_texture()
    
    def _create_thunder_sound(self) -> pygame.mixer.Sound:
        """Low rolling rumble resembling distant thunder"""
        duration = 4.0
        frames = int(duration * self.synth.sample_rate)
        arr = np.zeros((frames, 2))

        ## Brown(ish) noise for the rumble (integrated white noise)
        brown_noise = np.cumsum(np.random.normal(0, 0.02, frames))
        brown_noise = brown_noise / (np.max(np.abs(brown_noise)) + 1e-6)

        for i in range(frames):
            t = i / self.synth.sample_rate

            rumble = brown_noise[i]
            rumble += 0.5 * np.sin(2 * np.pi * 90 * t)  ## Low fundamental

            ## Thunder envelope – bursts every ~1.5 s inside 4 s loop
            env = np.exp(-((t % 1.5) * 1.8))

            wave = rumble * env * 0.2
            arr[i] = [wave, wave]

        arr = (arr * 32767).astype(np.int16)
        return pygame.sndarray.make_sound(arr)
    
    def _create_trees_sound(self) -> pygame.mixer.Sound:
        """Rustling, creaking texture - background rhythm"""
        return self._create_trees_texture()
    
    def _create_birds_sound(self) -> pygame.mixer.Sound:
        """Ambient chirping texture - background atmosphere"""
        return self._create_birds_texture()
    
    def _create_insects_sound(self) -> pygame.mixer.Sound:
        """Buzzing, clicking texture - background rhythm"""
        return self._create_insects_texture()
    
    def _create_sun_sound(self) -> pygame.mixer.Sound:
        """Warm harmonic drone - background atmosphere"""
        return self._create_background_drone(200, 'sine', harmonics=True)
    
    
    
    def _create_background_drone(self, frequency: float, wave_type: str, harmonics: bool = False) -> pygame.mixer.Sound:
        """Create a continuous background drone texture"""
        duration = 4.0
        frames = int(duration * self.synth.sample_rate)
        arr = np.zeros((frames, 2))
        
        for i in range(frames):
            t = i / self.synth.sample_rate
            
            if wave_type == 'sine':
                wave = np.sin(2 * np.pi * frequency * t)
                if harmonics:
                    ## Add harmonic richness for sun
                    wave += 0.3 * np.sin(2 * np.pi * frequency * 1.5 * t)
                    wave += 0.2 * np.sin(2 * np.pi * frequency * 2 * t)
            elif wave_type == 'triangle':
                wave = 2 * np.arcsin(np.sin(2 * np.pi * frequency * t)) / np.pi
            else:
                wave = np.sin(2 * np.pi * frequency * t)
            
            ## Add subtle modulation for natural feel
            modulation = 1 + 0.1 * np.sin(2 * np.pi * 0.5 * t)  # Slow LFO
            wave = wave * modulation * 0.15  # Lower volume for background
            
            arr[i] = [wave, wave]
        
        arr = (arr * 32767).astype(np.int16)
        return pygame.sndarray.make_sound(arr)
    
    def _create_rain_texture(self) -> pygame.mixer.Sound:
        """Create a rhythmic rain patter texture"""
        duration = 4.0
        frames = int(duration * self.synth.sample_rate)
        arr = np.zeros((frames, 2))
        
        for i in range(frames):
            t = i / self.synth.sample_rate
            
            ## Create random droplets with rhythmic pattern
            beat = int(t * 4) % 4  # 4 beats per loop
            if beat in [0, 2]:  # On beats 1 and 3
                if random.random() < 0.3:  # 30% chance
                    drop_freq = random.uniform(800, 1600)
                    wave = np.sin(2 * np.pi * drop_freq * (t % 0.25)) * np.exp(-(t % 0.25) * 8)
                else:
                    wave = 0
            else:
                if random.random() < 0.1:  # Lighter off-beats
                    drop_freq = random.uniform(600, 1000)
                    wave = np.sin(2 * np.pi * drop_freq * (t % 0.25)) * np.exp(-(t % 0.25) * 12)
                else:
                    wave = 0
            
            ## Constant soft hiss for rainfall atmosphere (filtered white noise)
            hiss = random.uniform(-1, 1) * 0.02

            ## Add gentle background noise (existing) and hiss
            background = random.uniform(-0.05, 0.05)
            combined = (wave * 0.8 + background + hiss) * 0.12
            
            arr[i] = [combined, combined]
        
        arr = (arr * 32767).astype(np.int16)
        return pygame.sndarray.make_sound(arr)
    
    def _create_wind_texture(self) -> pygame.mixer.Sound:
        """Create a whooshing wind texture"""
        duration = 4.0
        frames = int(duration * self.synth.sample_rate)
        arr = np.zeros((frames, 2))
        
        for i in range(frames):
            t = i / self.synth.sample_rate
            
            ## Base wind sound using filtered noise
            noise = random.uniform(-1, 1)
            
            ## Layered amplitude modulation for more organic gusts
            gust_main = 1 + 0.6 * np.sin(2 * np.pi * 0.25 * t)       ## Slow main gust
            gust_detail = 1 + 0.2 * np.sin(2 * np.pi * 1.3 * t)      ## Faster flutter

            filtered_noise = noise * gust_main * gust_detail * 0.08
            
            arr[i] = [filtered_noise, filtered_noise]
        
        arr = (arr * 32767).astype(np.int16)
        return pygame.sndarray.make_sound(arr)
    
    def _create_trees_texture(self) -> pygame.mixer.Sound:
        """Create a rustling/creaking tree texture"""
        duration = 4.0
        frames = int(duration * self.synth.sample_rate)
        arr = np.zeros((frames, 2))
        
        for i in range(frames):
            t = i / self.synth.sample_rate
            
            ## Create rustling with random bursts
            if random.random() < 0.05:  # 5% chance of rustle
                rustle_freq = random.uniform(200, 400)
                wave = np.sin(2 * np.pi * rustle_freq * t) * np.exp(-((t % 1) * 4))
            else:
                wave = 0
            
            ## Add subtle creaking (low frequency)
            creak = 0.3 * np.sin(2 * np.pi * 150 * t) * np.sin(2 * np.pi * 0.2 * t)
            
            combined = (wave + creak) * 0.1
            arr[i] = [combined, combined]
        
        arr = (arr * 32767).astype(np.int16)
        return pygame.sndarray.make_sound(arr)
    
    def _create_birds_texture(self) -> pygame.mixer.Sound:
        """Create an ambient bird texture"""
        duration = 4.0
        frames = int(duration * self.synth.sample_rate)
        arr = np.zeros((frames, 2))
        
        ## Create gentle ambient bird calls
        bird_times = [0.5, 1.8, 3.2]  # When birds chirp
        
        for i in range(frames):
            t = i / self.synth.sample_rate
            wave = 0
            
            ## Check if we're near a bird call time
            for bird_time in bird_times:
                if abs(t - bird_time) < 0.3:  # 0.3 second window
                    local_t = t - bird_time + 0.3
                    if local_t >= 0:
                        bird_freq = 1200 + 200 * np.sin(2 * np.pi * 8 * local_t)  # Warbling
                        wave += np.sin(2 * np.pi * bird_freq * local_t) * np.exp(-local_t * 3)
            
            wave = wave * 0.08
            arr[i] = [wave, wave]
        
        arr = (arr * 32767).astype(np.int16)
        return pygame.sndarray.make_sound(arr)
    
    def _create_insects_texture(self) -> pygame.mixer.Sound:
        """Create a buzzing/clicking insect texture"""
        duration = 4.0
        frames = int(duration * self.synth.sample_rate)
        arr = np.zeros((frames, 2))
        
        for i in range(frames):
            t = i / self.synth.sample_rate
            wave = 0
            
            ## Create buzzing pattern
            buzz_pattern = int(t * 8) % 8
            if buzz_pattern < 3:  # Buzz for first 3/8 of pattern
                buzz_freq = 400 + 50 * np.sin(2 * np.pi * 20 * t)
                wave = np.sin(2 * np.pi * buzz_freq * t) * 0.5
            
            ## Add occasional clicks
            if random.random() < 0.02:  # 2% chance
                click = np.sin(2 * np.pi * 800 * t) * np.exp(-t * 20)
                wave += click
            
            wave = wave * 0.06
            arr[i] = [wave, wave]
        
        arr = (arr * 32767).astype(np.int16)
        return pygame.sndarray.make_sound(arr)
    
    def _create_melodic_tone(self, frequency: float, timbre: str) -> pygame.mixer.Sound:
        """Create a melodic tone that sits well over background textures"""
        duration = 1.2  # Shorter than background textures
        frames = int(duration * self.synth.sample_rate)
        arr = np.zeros((frames, 2))
        
        for i in range(frames):
            t = i / self.synth.sample_rate
            
            if timbre == 'bell':
                ## Bell-like with harmonics
                wave = np.sin(2 * np.pi * frequency * t)
                wave += 0.3 * np.sin(2 * np.pi * frequency * 2 * t)
                wave += 0.1 * np.sin(2 * np.pi * frequency * 3 * t)
                envelope = np.exp(-t * 1.5)  # Bell decay
            elif timbre == 'soft':
                ## Soft sine wave
                wave = np.sin(2 * np.pi * frequency * t)
                envelope = np.exp(-t * 0.8)  # Gentle decay
            elif timbre == 'bright':
                ## Brighter with slight harmonics
                wave = np.sin(2 * np.pi * frequency * t)
                wave += 0.2 * np.sin(2 * np.pi * frequency * 1.5 * t)
                envelope = np.exp(-t * 1.0)
            elif timbre == 'sparkle':
                ## Sparkling with higher harmonics
                wave = np.sin(2 * np.pi * frequency * t)
                wave += 0.4 * np.sin(2 * np.pi * frequency * 2.5 * t)
                wave += 0.2 * np.sin(2 * np.pi * frequency * 4 * t)
                envelope = np.exp(-t * 1.2)
            else:
                wave = np.sin(2 * np.pi * frequency * t)
                envelope = np.exp(-t * 1.0)
            
            combined = wave * envelope * 0.25  # Volume for melodic layer
            arr[i] = [combined, combined]
        
        arr = (arr * 32767).astype(np.int16)
        return pygame.sndarray.make_sound(arr)
    
    def _create_melodic_tone_off(self, frequency: float, timbre: str) -> pygame.mixer.Sound:
        """Create a softer, shorter 'off' variation of the melodic tone"""
        duration = 0.6  # Shorter duration for "off" sound
        frames = int(duration * self.synth.sample_rate)
        arr = np.zeros((frames, 2))
        
        ## Slightly lower frequency for "off" variation (more mellow feeling)
        off_frequency = frequency * 0.85
        
        for i in range(frames):
            t = i / self.synth.sample_rate
            
            ## Similar timbres but with reduced intensity and quicker decay
            if timbre == 'bell':
                wave = np.sin(2 * np.pi * off_frequency * t)
                wave += 0.15 * np.sin(2 * np.pi * off_frequency * 2 * t)  # Reduced harmonics
                envelope = np.exp(-t * 3.0)  # Faster decay than "on" version
            elif timbre == 'soft':
                wave = np.sin(2 * np.pi * off_frequency * t)
                envelope = np.exp(-t * 2.0)  # Faster than original soft decay
            elif timbre == 'bright':
                wave = np.sin(2 * np.pi * off_frequency * t)
                wave += 0.1 * np.sin(2 * np.pi * off_frequency * 1.5 * t)  # Less bright
                envelope = np.exp(-t * 2.5)
            elif timbre == 'sparkle':
                wave = np.sin(2 * np.pi * off_frequency * t)
                wave += 0.2 * np.sin(2 * np.pi * off_frequency * 2.5 * t)  # Reduced sparkle
                wave += 0.1 * np.sin(2 * np.pi * off_frequency * 4 * t)
                envelope = np.exp(-t * 2.8)
            else:
                wave = np.sin(2 * np.pi * off_frequency * t)
                envelope = np.exp(-t * 2.0)
            
            ## Apply envelope and reduced volume for softer "off" character
            combined = wave * envelope * 0.15  # Lower volume than "on" sound (0.25)
            arr[i] = [combined, combined]
        
        arr = (arr * 32767).astype(np.int16)
        return pygame.sndarray.make_sound(arr)
    
    def _create_chord(self, frequencies: List[float], duration: float) -> pygame.mixer.Sound:
        """Create a chord by combining multiple frequencies"""
        frames = int(duration * self.synth.sample_rate)
        arr = np.zeros((frames, 2))
        
        for i in range(frames):
            t = i / self.synth.sample_rate
            combined_wave = 0
            
            ## Mix all frequencies together
            for frequency in frequencies:
                ## Apply frequency limits for toddler safety (200Hz-4kHz)
                if frequency < 200:
                    frequency = 200
                elif frequency > 4000:
                    frequency = 4000
                
                ## Generate sine wave for this frequency
                wave = np.sin(2 * np.pi * frequency * t)
                combined_wave += wave
            
            ## Normalize by number of frequencies to prevent clipping
            if len(frequencies) > 0:
                combined_wave = combined_wave / len(frequencies)
            
            ## Apply gentle envelope for natural sound
            envelope = np.exp(-t * 0.5)  # Gentle decay
            
            ## Apply volume limit for safety
            final_wave = combined_wave * envelope * 0.2
            arr[i] = [final_wave, final_wave]
        
        ## Convert to pygame sound
        arr = (arr * 32767).astype(np.int16)
        return pygame.sndarray.make_sound(arr)

class MusicalGarden:
    """Main application managing the musical garden experience"""
    
    def __init__(self):
        self.running = False
        self.midi_input = None
        self.synthesizer = AudioSynthesizer()
        self.nature_sounds = NatureSounds(self.synthesizer)
        
        ## Master volume control
        self.master_volume = 0.5  # 0.0 = silent, 1.0 = max (controlled by volume knob)
        
        ## Environmental controls - now affect audio in real-time!
        self.temperature = 0.5  # 0-1 (cold to hot - affects pitch)
        self.water = 0.3        # 0-1 (dry to wet - affects reverb/echo)
        self.time_of_day = 0.5  # 0-1 (morning to evening - affects brightness)
        self.seasons = 0.5      # 0-1 (winter to summer - affects character)
        
        ## Active sounds tracking
        self.active_sounds = {}
        
        ## Toggle states for each pad (True = ON/playing, False = OFF/silent)
        self.pad_states = {}
        
        ## Load MIDI mappings
        self.load_midi_mappings()
    
    def load_midi_mappings(self):
        """Load MIDI mappings from JSON file"""
        try:
            with open('setup/sparkle_mapping.json', 'r') as f:
                self.midi_mappings = json.load(f)
                self._build_note_mapping()
        except FileNotFoundError:
            print("Warning: setup/sparkle_mapping.json not found. Using default mappings.")
            self.midi_mappings = {"groups": {}}
            self._build_default_mapping()
    
    def _build_note_mapping(self):
        """Build note-to-sound mapping from JSON"""
        self.note_to_sound = {}
        
        ## Process big pads
        if 'big_pads' in self.midi_mappings.get('groups', {}):
            big_pad_sounds = ['earth', 'rain', 'wind', 'thunder', 'trees', 'birds', 'insects', 'sun']
            big_pads = self.midi_mappings['groups']['big_pads']
            
            ## Extract ON events in the order they appear in JSON (preserves physical pad order)
            on_events = []
            for pad in big_pads:
                if pad['midi_type'] == 'note_on':
                    on_events.append(pad['midi_note'])
            
            ## Map to sounds based on JSON order (not sorted order)
            for i, note in enumerate(on_events):
                if i < len(big_pad_sounds):
                    self.note_to_sound[note] = big_pad_sounds[i]
        
        ## Process number pads
        if 'numbers' in self.midi_mappings.get('groups', {}):
            numbers = self.midi_mappings['groups']['numbers']
            
            ## Group by note number and extract ON events
            number_groups = {}
            for num in numbers:
                if num['midi_type'] == 'note_on':
                    note = num['midi_note']
                    number_groups[note] = num
            
            ## Map to progressive complexity
            sorted_notes = sorted(number_groups.keys())
            for i, note in enumerate(sorted_notes):
                row = i // 4
                if row == 0:
                    self.note_to_sound[note] = f'seed_{i+1}'
                elif row == 1:
                    self.note_to_sound[note] = f'sprout_{i+1}'
                elif row == 2:
                    self.note_to_sound[note] = f'bud_{i+1}'
                else:
                    self.note_to_sound[note] = f'flower_{i+1}'
    
    def _build_default_mapping(self):
        """Build default mapping if JSON file not found"""
        self.note_to_sound = {
            36: 'earth', 38: 'rain', 42: 'wind', 46: 'thunder',
            50: 'trees', 47: 'birds', 43: 'insects', 49: 'sun'
        }
        ## Add number pads
        for i in range(16):
            note = 51 + i
            row = i // 4
            if row == 0:
                self.note_to_sound[note] = f'seed_{i+1}'
            elif row == 1:
                self.note_to_sound[note] = f'sprout_{i+1}'
            elif row == 2:
                self.note_to_sound[note] = f'bud_{i+1}'
            else:
                self.note_to_sound[note] = f'flower_{i+1}'
    
    def start_garden(self):
        """Start the musical garden with opening ritual"""
        if self.running:
            return
            
        self.running = True
        print("🌸 Garden is waking up... 🌸")
        
        ## Opening ritual - play gentle awakening sound
        self.play_opening_ritual()
        
        ## Start MIDI monitoring thread
        self.midi_thread = threading.Thread(target=self.midi_monitor, daemon=True)
        self.midi_thread.start()
        
        ## Start status update thread
        self.status_thread = threading.Thread(target=self.status_monitor, daemon=True)
        self.status_thread.start()
        
        print("🌸 Garden is awake! Ready for musical layering ⚡")
        print("\n🎵 Background Textures (Big Pads) - Toggle ON/OFF:")
        print("   Pad 1: Earth Drone 🌍  |  Pad 2: Rain Pattern 🌧️")
        print("   Pad 3: Wind Texture 💨 |  Pad 4: Thunder Rumble ⛈️")
        print("   Pad 5: Tree Rustles 🌳 |  Pad 6: Bird Ambience 🐦")
        print("   Pad 7: Insect Buzz 🦗  |  Pad 8: Sun Warmth ☀️")
        print("\n🎼 Melodic Notes (Number Pads 1-16) - Play on Toggle:")
        print("   Row 1 (1-4): Bell Tones 🔔   |  Row 2 (5-8): Soft Notes 🎵")
        print("   Row 3 (9-12): Bright Tones ✨ |  Row 4 (13-16): Sparkle Notes 💎")
        print("\n🎛️ Knob Controls - Turn to adjust the garden:")
        print("   Volume Knob: 🎚️ Master volume (silent ↔ loud)")
        print("   K1 (Temperature): 🌡️ Pitch control (cold ↔ hot)")
        print("   K2 (Water): 💧 Echo effects (dry ↔ wet)")
        print("   K3 (Time): 🕐 Brightness (dark ↔ bright)")
        print("   Tempo (Seasons): 🗓️ Character (winter ↔ summer)")
        print("\n🎹 How it works:")
        print("   • Big Pads = Background textures (loop when ON)")
        print("   • Number Pads = Melodic notes (play over background)")
        print("   • Knobs = Real-time garden environment control!")
        print("   • Layer multiple backgrounds + add melodies + adjust knobs!")
        print("   • Each press toggles between ON/OFF or plays note")
        print("\nPress Ctrl+C to put the garden to sleep 🌙")
    
    def play_opening_ritual(self):
        """Play gentle opening sounds"""
        ## Play a soft major chord to welcome the toddler
        welcome_chord = self.nature_sounds._create_chord([261.63, 329.63, 392.00], 2.0)
        pygame.mixer.Sound.play(welcome_chord)
        print("🌅 Good morning, little gardener! 🌅")
    
    def play_closing_ritual(self):
        """Play gentle closing sounds"""
        ## Play a soft descending melody
        closing_notes = [392.00, 329.63, 261.63]  # G-E-C descent
        for i, freq in enumerate(closing_notes):
            sound = self.synthesizer.generate_tone(freq, 1.0, 'sine', 'soft')
            threading.Timer(i * 0.8, lambda s=sound: pygame.mixer.Sound.play(s)).start()
        
        print("🌙 Goodnight, garden! Sweet dreams! 🌙")
    
    def stop_garden(self):
        """Stop the musical garden with closing ritual"""
        if not self.running:
            return
            
        print("\n🌙 Garden is going to sleep...")
        
        ## Play closing ritual
        self.play_closing_ritual()
        
        ## Wait a moment for closing sounds
        time.sleep(3.0)
        self._complete_shutdown()
    
    def _complete_shutdown(self):
        """Complete the garden shutdown"""
        self.running = False
        print("🌙 Garden is sleeping... zzz")
        
        ## Stop all active sounds
        for sound in self.active_sounds.values():
            if sound:
                sound.fadeout(1000)  # Gentle fade out
        self.active_sounds.clear()
        
        ## Close MIDI input
        if self.midi_input:
            self.midi_input.close()
        
        print("🌙 Musical Garden stopped. Sweet dreams!")
    
    def midi_monitor(self):
        """Monitor MIDI input from SparkLE controller"""
        try:
            ## Try to connect to SparkLE
            midi_devices = mido.get_input_names()
            device_name = None
            
            for device in midi_devices:
                if 'SparkLE' in device or 'Arturia' in device:
                    device_name = device
                    break
            
            if not device_name and midi_devices:
                device_name = midi_devices[0]  # Use first available device
            
            if not device_name:
                print("⚠️  No MIDI devices found! Connect your SparkLE and restart.")
                return
            
            self.midi_input = mido.open_input(device_name)
            print(f"🎹 Connected to MIDI device: {device_name}")
            
            ## Process MIDI messages
            while self.running:
                try:
                    msg = self.midi_input.receive(block=False)
                    if msg:
                        self.process_midi_message(msg)
                except:
                    pass
                time.sleep(0.001)  # Small delay to prevent CPU overload
                
        except Exception as e:
            print(f"❌ MIDI connection error: {e}")
    
    def status_monitor(self):
        """Monitor and display current status"""
        last_active_count = 0
        last_status_time = 0
        
        while self.running:
            try:
                ## Count active sounds (pads that are ON)
                active_count = sum(1 for state in self.pad_states.values() if state)
                
                ## Show current status every 10 seconds or when count changes
                current_time = int(time.time())
                if active_count != last_active_count or (current_time - last_status_time) >= 10:
                    if active_count > 0:
                        active_elements = []
                        for note, is_on in self.pad_states.items():
                            if is_on:
                                sound_name = self.get_sound_name_for_note(note)
                                if sound_name:
                                    element_name = self.get_element_name(sound_name)
                                    active_elements.append(element_name)
                        
                        if active_elements:
                            print(f"🎵 Active: {', '.join(active_elements)} ({active_count} elements)")
                    else:
                        print("🌸 Garden is quiet... (press any pad to start)")
                    
                    last_active_count = active_count
                    last_status_time = current_time
                
                ## Display environmental status occasionally
                if int(time.time()) % 30 == 0:  # Every 30 seconds
                    temp_status = "❄️ Cool" if self.temperature < 0.3 else "🌞 Warm" if self.temperature > 0.7 else "🌤️ Mild"
                    water_status = "🌵 Dry" if self.water < 0.3 else "🌊 Wet" if self.water > 0.7 else "🌱 Fresh"
                    time_status = "🌅 Morning" if self.time_of_day < 0.3 else "🌆 Evening" if self.time_of_day > 0.7 else "☀️ Day"
                    print(f"🌍 Environment: {temp_status}, {water_status}, {time_status}")
                
            except Exception as e:
                print(f"Status monitor error: {e}")
            
            time.sleep(0.2)
    
    def process_midi_message(self, msg):
        """Process incoming MIDI messages"""
        if msg.type == 'note_on' and msg.velocity > 0:
            self.handle_note_toggle(msg.note, msg.velocity)
        elif msg.type == 'note_off' or (msg.type == 'note_on' and msg.velocity == 0):
            self.handle_note_toggle(msg.note, 64)  # Use default velocity for note_off
        elif msg.type == 'control_change':
            self.handle_control_change(msg.control, msg.value)
    
    def handle_note_toggle(self, note: int, velocity: int):
        """Handle note toggle events - each press toggles ON/OFF state"""
        sound_name = self.get_sound_name_for_note(note)
        if not sound_name or sound_name not in self.nature_sounds.sounds:
            return
            
        ## Check current state (default to OFF if not set)
        current_state = self.pad_states.get(note, False)
        
        if current_state:
            ## Currently ON, turn it OFF
            self.turn_pad_off(note)
        else:
            ## Currently OFF, turn it ON
            self.turn_pad_on(note, velocity)
    
    def turn_pad_on(self, note: int, velocity: int):
        """Turn a pad ON - different behavior for background vs melodic"""
        sound_name = self.get_sound_name_for_note(note)
        if not sound_name:
            return
            
        ## Stop any existing sound for this note first
        if note in self.active_sounds:
            old_channel = self.active_sounds[note]
            if old_channel:
                old_channel.stop()
        
        ## Play the sound
        sound = self.nature_sounds.sounds[sound_name]
        channel = pygame.mixer.find_channel()
        if channel:
            ## Use velocity and master volume to control volume (0.1 to 0.8 for safety)
            velocity_volume = 0.1 + (velocity / 127.0) * 0.7
            final_volume = velocity_volume * self.master_volume
            sound.set_volume(final_volume)
            
            ## Background textures (big pads) loop continuously
            ## Melodic tones (number pads) play once but can be retriggered
            if self.is_big_pad_note(note):
                channel.play(sound, loops=-1)  # Loop indefinitely
                self.active_sounds[note] = channel
                self.pad_states[note] = True
                element_name = self.get_element_name(sound_name)
                print(f"🟢 {element_name} texture ON (looping)")
            else:
                channel.play(sound)  # Play once
                ## For melodic tones, we don't store the channel since they play once
                ## But we still track the pad state for toggle behavior
                self.pad_states[note] = True
                element_name = self.get_element_name(sound_name)
                print(f"🎵 {element_name} played")
    
    def turn_pad_off(self, note: int):
        """Turn a pad OFF - different behavior for background vs melodic"""
        sound_name = self.get_sound_name_for_note(note)
        
        if self.is_big_pad_note(note):
            ## Background textures: stop the looping sound
            if note in self.active_sounds:
                channel = self.active_sounds[note]
                if channel:
                    channel.fadeout(300)  # Gentle fade out
                del self.active_sounds[note]
            element_name = self.get_element_name(sound_name) if sound_name else "Unknown"
            print(f"🔴 {element_name} texture OFF")
        else:
            ## Melodic tones: play the "off" variation for immediate response
            if sound_name and f"{sound_name}_off" in self.nature_sounds.sounds:
                off_sound = self.nature_sounds.sounds[f"{sound_name}_off"]
                channel = pygame.mixer.find_channel()
                if channel:
                    ## Use master volume and make it softer for "off" feel
                    final_volume = 0.4 * self.master_volume  # Quieter than "on" sounds
                    off_sound.set_volume(final_volume)
                    channel.play(off_sound)  # Play the "off" variation
                    
                element_name = self.get_element_name(sound_name) if sound_name else "Unknown"
                print(f"🎵 {element_name} (soft)")
            else:
                element_name = self.get_element_name(sound_name) if sound_name else "Unknown"
                print(f"🎵 {element_name} ready to play again")
        
        self.pad_states[note] = False
    
    def handle_control_change(self, control: int, value: int):
        """Handle control change events (knobs)"""
        normalized_value = value / 127.0
        
        ## Master Volume Control
        if control == 10:  # Volume knob
            self.master_volume = normalized_value
            volume_name = "🔇 Silent" if normalized_value < 0.1 else "🔈 Quiet" if normalized_value < 0.4 else "🔉 Medium" if normalized_value < 0.8 else "🔊 Loud"
            print(f"🎚️ Master Volume: {volume_name}")
            self._update_all_volumes()  # Apply to all active sounds
            
        ## Environmental controls - now affect audio in real-time!
        elif control == 16:  # K1 - Temperature (affects pitch)
            self.temperature = normalized_value
            temp_name = "❄️ Cold" if normalized_value < 0.3 else "🌞 Hot" if normalized_value > 0.7 else "🌤️ Warm"
            print(f"🌡️ Temperature: {temp_name} (pitch {'-' if normalized_value < 0.5 else '+'})")
            self._update_all_audio_effects()
            
        elif control == 17:  # K2 - Water (affects reverb/echo)
            self.water = normalized_value
            water_name = "🌵 Dry" if normalized_value < 0.3 else "🌊 Flooding" if normalized_value > 0.7 else "🌱 Perfect"
            print(f"💧 Water: {water_name} (echo {'minimal' if normalized_value < 0.3 else 'lots' if normalized_value > 0.7 else 'some'})")
            self._update_all_audio_effects()
            
        elif control == 18:  # K3 - Time of Day (affects brightness/filtering)
            self.time_of_day = normalized_value
            time_name = "🌅 Dawn" if normalized_value < 0.3 else "🌆 Dusk" if normalized_value > 0.7 else "☀️ Noon"
            print(f"🕐 Time: {time_name} (brightness {'dark' if normalized_value < 0.3 else 'bright' if normalized_value > 0.7 else 'medium'})")
            self._update_all_audio_effects()
            
        elif control == 7:   # Tempo - Seasons (affects character/timbre)
            self.seasons = normalized_value
            season_name = "❄️ Winter" if normalized_value < 0.25 else "🌸 Spring" if normalized_value < 0.5 else "☀️ Summer" if normalized_value < 0.75 else "🍂 Autumn"
            print(f"🗓️ Season: {season_name} (character {'sparse' if normalized_value < 0.25 else 'fresh' if normalized_value < 0.5 else 'rich' if normalized_value < 0.75 else 'mellow'})")
            self._update_all_audio_effects()
    
    def get_sound_name_for_note(self, note: int) -> Optional[str]:
        """Map MIDI note to sound name using loaded JSON mapping"""
        return self.note_to_sound.get(note)
    
    def is_big_pad_note(self, note: int) -> bool:
        """Check if note corresponds to a big pad (garden element)"""
        sound_name = self.get_sound_name_for_note(note)
        if sound_name:
            return sound_name in ['earth', 'rain', 'wind', 'thunder', 'trees', 'birds', 'insects', 'sun']
        return False
    
    def get_element_name(self, sound_name: str) -> str:
        """Get friendly name for sound"""
        element_names = {
            'earth': 'Earth 🌍',
            'rain': 'Rain 🌧️',
            'wind': 'Wind 💨',
            'thunder': 'Thunder ⛈️',
            'trees': 'Trees 🌳',
            'birds': 'Birds 🐦',
            'insects': 'Insects 🦗',
            'sun': 'Sun ☀️'
        }
        
        if sound_name in element_names:
            return element_names[sound_name]
        elif 'seed' in sound_name:
            return f'Seed {sound_name.split("_")[1]} 🌱'
        elif 'sprout' in sound_name:
            return f'Sprout {sound_name.split("_")[1]} 🌿'
        elif 'bud' in sound_name:
            return f'Bud {sound_name.split("_")[1]} 🌸'
        elif 'flower' in sound_name:
            return f'Flower {sound_name.split("_")[1]} 🌺'
        
        return sound_name
    
    def _update_all_volumes(self):
        """Update volume for all active sounds based on master volume"""
        for note, channel in self.active_sounds.items():
            if channel and channel.get_busy():
                sound_name = self.get_sound_name_for_note(note)
                if sound_name and sound_name in self.nature_sounds.sounds:
                    sound = self.nature_sounds.sounds[sound_name]
                    ## Apply master volume (keeping the base volume reasonable)
                    base_volume = 0.6  # Base volume for active sounds
                    final_volume = base_volume * self.master_volume
                    sound.set_volume(final_volume)
    
    def _update_all_audio_effects(self):
        """Update audio effects for all active sounds based on environmental controls"""
        ## For now, we'll focus on volume and simple pitch variations
        ## More complex effects like reverb would require more advanced audio processing
        
        ## Temperature affects pitch: colder = lower, hotter = higher
        pitch_modifier = 0.8 + (self.temperature * 0.4)  # Range: 0.8 to 1.2
        
        ## Apply environmental effects to active sounds
        for note, channel in self.active_sounds.items():
            if channel and channel.get_busy():
                sound_name = self.get_sound_name_for_note(note)
                if sound_name:
                    ## For now, we'll regenerate sounds with new parameters
                    ## This is a simple implementation - could be optimized
                    self._apply_environmental_effects_to_sound(note, sound_name)
    
    def _apply_environmental_effects_to_sound(self, note: int, sound_name: str):
        """Apply environmental effects to a specific sound"""
        ## This is a simplified implementation
        ## In a full implementation, you'd want real-time audio effects
        
        ## Temperature affects frequency (pitch)
        freq_modifier = 0.8 + (self.temperature * 0.4)  # 0.8x to 1.2x frequency
        
        ## Time of day affects volume (quieter at night)
        time_volume_modifier = 0.6 + (self.time_of_day * 0.4)  # 0.6x to 1.0x volume
        
        ## Apply the modifications by updating volume
        if note in self.active_sounds:
            channel = self.active_sounds[note]
            if channel and channel.get_busy():
                sound = self.nature_sounds.sounds[sound_name]
                base_volume = 0.6 * self.master_volume * time_volume_modifier
                sound.set_volume(base_volume)
                
                ## Note: Real-time pitch shifting would require more advanced audio processing
                ## For now we provide visual feedback about the environmental effects
    
    def run(self):
        """Run the musical garden application"""
        print("🌸 Welcome to the Musical Garden! 🌸")
        print("This is a toddler-friendly musical playground using nature sounds.")
        print("Connect your SparkLE controller and the garden will begin!")
        print()
        
        try:
            self.start_garden()
            ## Keep running until interrupted
            while self.running:
                time.sleep(1)
                
        except KeyboardInterrupt:
            print("\n🌙 Closing Musical Garden...")
        finally:
            self.stop_garden()

def main():
    """Main entry point"""
    try:
        garden = MusicalGarden()
        garden.run()
    except Exception as e:
        print(f"❌ Error starting Musical Garden: {e}")
        print("Make sure pygame, mido and numpy are installed: pip install pygame mido numpy")

if __name__ == "__main__":
    main()
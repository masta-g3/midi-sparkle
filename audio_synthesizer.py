#!/usr/bin/env python3
"""
Audio Synthesizer - Core synthesis engine for Musical Garden
Generates natural-sounding audio with safety limits for toddlers
"""

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
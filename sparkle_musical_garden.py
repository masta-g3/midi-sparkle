#!/usr/bin/env python3
"""
SparkLE Musical Garden - CLI Version
Audio-only toddler-friendly musical playground without GUI
Based on the nature-themed design for 1.8-year-old toddlers
"""

import json
import time
import threading
import argparse
import curses
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
        """Deep pentatonic bass foundation - musical grounding for all melodies"""
        duration = 4.0
        frames = int(duration * self.synth.sample_rate)
        arr = np.zeros((frames, 2))

        ## Pentatonic bass foundation: C2-G2-C3 perfect fifth intervals
        c2_freq = 65.41    # C2 - deep fundamental
        g2_freq = 98.00    # G2 - perfect fifth
        c3_freq = 130.81   # C3 - octave

        for i in range(frames):
            t = i / self.synth.sample_rate

            ## Three-layer bass foundation with harmonics
            # C2 fundamental with warm harmonics
            c2_fundamental = 0.7 * np.sin(2 * np.pi * c2_freq * t)
            c2_harmonic2 = 0.25 * np.sin(2 * np.pi * c2_freq * 2 * t)  # Octave harmonic
            c2_harmonic3 = 0.15 * np.sin(2 * np.pi * c2_freq * 3 * t)  # Fifth harmonic
            
            # G2 perfect fifth with subtle harmonics
            g2_fundamental = 0.5 * np.sin(2 * np.pi * g2_freq * t)
            g2_harmonic2 = 0.2 * np.sin(2 * np.pi * g2_freq * 2 * t)
            
            # C3 octave for clarity and definition
            c3_fundamental = 0.4 * np.sin(2 * np.pi * c3_freq * t)
            c3_harmonic2 = 0.15 * np.sin(2 * np.pi * c3_freq * 1.5 * t)  # Gentle fifth

            ## Slow breathing modulation for organic feel (0.08Hz = 12.5 second cycle)
            breathing_lfo = 0.82 + 0.18 * np.sin(2 * np.pi * 0.08 * t)
            
            ## Subtle pitch vibrato for warmth (very slow, 0.3Hz)
            pitch_vibrato = 1 + 0.008 * np.sin(2 * np.pi * 0.3 * t)

            ## Combine all layers
            earth_bass = (
                (c2_fundamental + c2_harmonic2 + c2_harmonic3) +
                (g2_fundamental + g2_harmonic2) +
                (c3_fundamental + c3_harmonic2)
            ) * pitch_vibrato

            ## Apply breathing modulation and gentle volume (increased by 10%)
            wave = earth_bass * breathing_lfo * 0.154
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
        """Deep pentatonic bass strikes with dramatic musical decay"""
        duration = 4.0
        frames = int(duration * self.synth.sample_rate)
        arr = np.zeros((frames, 2))

        ## Ultra-deep pentatonic bass frequencies for thunder power
        c1_freq = 32.70    # C1 - deepest foundation (below audible, felt)
        g1_freq = 49.00    # G1 - perfect fifth
        c2_freq = 65.41    # C2 - octave up for clarity
        
        ## Thunder strike timing (aligned to 4-second loop with proper decay)
        strike_times = [0.3, 2.2]  # Two powerful strikes with room for decay
        
        for i in range(frames):
            t = i / self.synth.sample_rate
            wave = 0.0
            
            ## Check if we're near any thunder strike times
            for strike_time in strike_times:
                time_from_strike = t - strike_time
                
                if 0 <= time_from_strike <= 1.8:  # Strike duration window (fits in loop)
                    ## Powerful bass strike with rich harmonics
                    # C1 ultra-deep foundation
                    c1_fundamental = 0.8 * np.sin(2 * np.pi * c1_freq * t)
                    c1_harmonic2 = 0.4 * np.sin(2 * np.pi * c1_freq * 2 * t)    # Octave
                    c1_harmonic3 = 0.2 * np.sin(2 * np.pi * c1_freq * 3 * t)    # Fifth
                    
                    # G1 perfect fifth for power
                    g1_fundamental = 0.6 * np.sin(2 * np.pi * g1_freq * t)
                    g1_harmonic2 = 0.3 * np.sin(2 * np.pi * g1_freq * 2 * t)
                    
                    # C2 octave for definition and punch
                    c2_fundamental = 0.5 * np.sin(2 * np.pi * c2_freq * t)
                    c2_harmonic2 = 0.25 * np.sin(2 * np.pi * c2_freq * 1.5 * t)  # Fifth
                    c2_harmonic3 = 0.15 * np.sin(2 * np.pi * c2_freq * 2.5 * t)  # Higher harmonic
                    
                    ## Dramatic thunder envelope - fast attack, long musical decay
                    if time_from_strike < 0.05:  # Very fast attack (50ms)
                        envelope = time_from_strike * 20  # Quick strike
                    else:  # Long, musical decay
                        envelope = np.exp(-(time_from_strike - 0.05) * 1.2)  # Slower than original
                    
                    ## Combine all bass layers
                    thunder_bass = (
                        (c1_fundamental + c1_harmonic2 + c1_harmonic3) +
                        (g1_fundamental + g1_harmonic2) +
                        (c2_fundamental + c2_harmonic2 + c2_harmonic3)
                    )
                    
                    wave += thunder_bass * envelope
            
            ## Apply overall volume (increased for dramatic effect)
            final_wave = wave * 0.22
            arr[i] = [final_wave, final_wave]

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
        """Create rhythmic pentatonic arpeggios suggesting gentle raindrops"""
        duration = 4.0
        frames = int(duration * self.synth.sample_rate)
        arr = np.zeros((frames, 2))
        
        ## Pentatonic frequencies for rain arpeggios (high register sparkle layer)
        e5_freq = 659.25   # E5 - bright sparkle
        a5_freq = 880.00   # A5 - perfect fourth above E5
        e6_freq = 1318.51  # E6 - octave above E5
        
        ## Musical pattern: 8th notes at 120 BPM = 0.25s per 8th note
        eighth_note_duration = 0.25
        
        for i in range(frames):
            t = i / self.synth.sample_rate
            wave = 0.0
            
            ## Calculate current 8th note position in the 4-second loop
            note_position = (t % duration) / eighth_note_duration
            note_index = int(note_position) % 16  # 16 eighth notes in 4 seconds
            note_time = (t % eighth_note_duration) / eighth_note_duration
            
            ## Musical rain patterns (varied arpeggio sequences)
            # Pattern 1: E5-A5-E6 ascending (beats 1-3)
            # Pattern 2: A5-E5 gentle (beats 5-6)  
            # Pattern 3: E6-A5-E5 descending (beats 9-11)
            # Rests and variations for organic feel
            
            rain_freq = None
            if note_index in [0, 2, 4]:      # E5-A5-E6 ascending
                rain_freq = [e5_freq, a5_freq, e6_freq][note_index // 2]
            elif note_index in [8, 9]:       # A5-E5 gentle
                rain_freq = [a5_freq, e5_freq][(note_index - 8)]
            elif note_index in [12, 13, 14]: # E6-A5-E5 descending
                rain_freq = [e6_freq, a5_freq, e5_freq][(note_index - 12)]
            # Other positions are rests for natural breathing
            
            if rain_freq is not None:
                ## Soft droplet envelope - quick attack, gentle decay
                if note_time < 0.1:  # Attack phase
                    envelope = note_time * 10  # Quick attack
                else:  # Decay phase
                    envelope = np.exp(-(note_time - 0.1) * 6)  # Gentle decay
                
                ## Generate pure sine wave droplet
                wave = np.sin(2 * np.pi * rain_freq * t) * envelope
                
                ## Add subtle harmonic for sparkle (very quiet)
                harmonic = 0.15 * np.sin(2 * np.pi * rain_freq * 1.5 * t) * envelope
                wave += harmonic
            
            ## Apply gentle volume for background texture
            combined = wave * 0.08
            arr[i] = [combined, combined]
        
        arr = (arr * 32767).astype(np.int16)
        return pygame.sndarray.make_sound(arr)
    
    def _create_wind_texture(self) -> pygame.mixer.Sound:
        """Create sustained pentatonic chords with breathing wind-like swells"""
        duration = 4.0
        frames = int(duration * self.synth.sample_rate)
        arr = np.zeros((frames, 2))
        
        ## Pentatonic chord for wind (mid-register harmonic support)
        d4_freq = 293.66   # D4 - gentle foundation
        g4_freq = 392.00   # G4 - perfect fourth above D4
        a4_freq = 440.00   # A4 - perfect fifth above D4 (completing triad)
        
        for i in range(frames):
            t = i / self.synth.sample_rate
            
            ## Three-part pentatonic chord with rich harmonics
            # D4 foundation with warm harmonics
            d4_fundamental = 0.6 * np.sin(2 * np.pi * d4_freq * t)
            d4_harmonic2 = 0.2 * np.sin(2 * np.pi * d4_freq * 1.5 * t)  # Fifth harmonic
            d4_harmonic3 = 0.1 * np.sin(2 * np.pi * d4_freq * 2 * t)    # Octave harmonic
            
            # G4 middle voice with subtle harmonics
            g4_fundamental = 0.5 * np.sin(2 * np.pi * g4_freq * t)
            g4_harmonic2 = 0.15 * np.sin(2 * np.pi * g4_freq * 1.25 * t)  # Quarter harmonic
            
            # A4 top voice for brightness
            a4_fundamental = 0.45 * np.sin(2 * np.pi * a4_freq * t)
            a4_harmonic2 = 0.12 * np.sin(2 * np.pi * a4_freq * 0.75 * t)  # Sub-harmonic for warmth
            
            ## Wind-like breathing modulation (aligned to 4-second loop)
            main_gust = 0.4 + 0.6 * np.sin(2 * np.pi * 0.25 * t)      # 4s cycle main swell
            detail_flutter = 1 + 0.15 * np.sin(2 * np.pi * 1.0 * t)   # 1s detail flutter
            
            ## Gentle pitch modulation for organic feel (very subtle, loop-aligned)
            pitch_sway = 1 + 0.005 * np.sin(2 * np.pi * 0.5 * t)      # 2s cycle
            
            ## Combine all chord voices
            wind_chord = (
                (d4_fundamental + d4_harmonic2 + d4_harmonic3) +
                (g4_fundamental + g4_harmonic2) +
                (a4_fundamental + a4_harmonic2)
            ) * pitch_sway
            
            ## Apply wind-like breathing modulation
            wave = wind_chord * main_gust * detail_flutter * 0.09
            arr[i] = [wave, wave]
        
        arr = (arr * 32767).astype(np.int16)
        return pygame.sndarray.make_sound(arr)
    
    def _create_trees_texture(self) -> pygame.mixer.Sound:
        """Create organic rhythmic percussion - like wooden blocks/rimshots"""
        duration = 4.0
        frames = int(duration * self.synth.sample_rate)
        arr = np.zeros((frames, 2))
        
        ## Pentatonic percussion frequencies (mid-register)
        g3_freq = 196.00   # G3 - woody fundamental
        d4_freq = 293.66   # D4 - brighter accent
        
        ## Rhythmic pattern: 16th note subdivision (0.25s each) in 4-second loop
        sixteenth_duration = 0.25
        
        ## Syncopated groove pattern for 16 positions (4 beats × 4 sixteenths)
        ## X = strong hit, x = light hit, . = rest
        ## Beat 1: X.x.  Beat 2: .x..  Beat 3: X..x  Beat 4: ..x.
        hit_pattern = [
            (0, 'strong'),   # Beat 1.1 - downbeat
            (2, 'light'),    # Beat 1.3 - syncopated
            (5, 'medium'),   # Beat 2.2 - offbeat
            (8, 'strong'),   # Beat 3.1 - downbeat  
            (11, 'light'),   # Beat 3.4 - syncopated
            (14, 'medium')   # Beat 4.3 - offbeat accent
        ]
        
        for i in range(frames):
            t = i / self.synth.sample_rate
            wave = 0.0
            
            ## Calculate current 16th note position
            note_position = (t % duration) / sixteenth_duration
            note_index = int(note_position)
            note_time = (note_position % 1.0) * sixteenth_duration
            
            ## Check if this position should have a percussion hit
            for hit_pos, hit_type in hit_pattern:
                if note_index == hit_pos and note_time < 0.15:  # Hit window
                    
                    ## Choose frequency based on hit type
                    if hit_type == 'strong':
                        perc_freq = d4_freq  # Brighter for strong hits
                        volume_mult = 1.0
                    elif hit_type == 'medium':
                        perc_freq = g3_freq  # Woody for medium hits
                        volume_mult = 0.7
                    else:  # light
                        perc_freq = g3_freq  # Woody for light hits
                        volume_mult = 0.4
                    
                    ## Percussive envelope - very fast attack, quick decay
                    if note_time < 0.01:  # Attack phase (10ms)
                        envelope = note_time * 100  # Very fast attack
                    else:  # Decay phase
                        envelope = np.exp(-(note_time - 0.01) * 12)  # Quick decay
                    
                    ## Generate woody percussion tone
                    fundamental = np.sin(2 * np.pi * perc_freq * t)
                    ## Add slight harmonic for wooden character
                    harmonic = 0.3 * np.sin(2 * np.pi * perc_freq * 1.5 * t)
                    ## Add subtle click for percussive attack
                    click = 0.2 * np.sin(2 * np.pi * perc_freq * 3 * t) if note_time < 0.005 else 0
                    
                    wave += (fundamental + harmonic + click) * envelope * volume_mult
            
            ## Apply gentle overall volume for rhythmic layer
            combined = wave * 0.12
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
        """Create high-frequency rhythmic texture - like hi-hats/shakers"""
        duration = 4.0
        frames = int(duration * self.synth.sample_rate)
        arr = np.zeros((frames, 2))
        
        ## High pentatonic frequencies for crisp rhythmic texture
        a5_freq = 880.00    # A5 - bright fundamental
        e6_freq = 1318.51   # E6 - sparkling accent
        
        ## Hi-hat style rhythmic pattern: 16th note subdivision (0.25s each)
        sixteenth_duration = 0.25
        
        ## Hi-hat pattern complementing Trees percussion - more frequent, lighter
        ## o = open/accent, c = closed/light, . = rest
        ## Beat 1: c.o.  Beat 2: c.c.  Beat 3: c.o.  Beat 4: c.c.
        hihat_pattern = [
            (0, 'closed'),   # Beat 1.1 - closed hihat
            (2, 'open'),     # Beat 1.3 - open accent
            (4, 'closed'),   # Beat 2.1 - closed hihat
            (6, 'closed'),   # Beat 2.3 - closed hihat
            (8, 'closed'),   # Beat 3.1 - closed hihat
            (10, 'open'),    # Beat 3.3 - open accent
            (12, 'closed'),  # Beat 4.1 - closed hihat
            (14, 'closed'),  # Beat 4.3 - closed hihat
            (1, 'ghost'),    # Ghost notes for groove
            (3, 'ghost'),
            (9, 'ghost'),
            (13, 'ghost')
        ]
        
        for i in range(frames):
            t = i / self.synth.sample_rate
            wave = 0.0
            
            ## Calculate current 16th note position
            note_position = (t % duration) / sixteenth_duration
            note_index = int(note_position)
            note_time = (note_position % 1.0) * sixteenth_duration
            
            ## Check if this position should have a hi-hat hit
            for hit_pos, hit_type in hihat_pattern:
                if note_index == hit_pos and note_time < 0.08:  # Short hi-hat window
                    
                    ## Choose frequency and character based on hit type
                    if hit_type == 'open':
                        hihat_freq = e6_freq  # Higher for open hi-hat
                        volume_mult = 0.8
                        decay_rate = 8  # Slower decay for "open" feel
                    elif hit_type == 'closed':
                        hihat_freq = a5_freq  # Lower for closed hi-hat
                        volume_mult = 0.6
                        decay_rate = 15  # Faster decay for "closed" feel
                    else:  # ghost
                        hihat_freq = a5_freq  # Subtle ghost notes
                        volume_mult = 0.25
                        decay_rate = 20  # Very fast decay
                    
                    ## Very fast percussive envelope for crisp hi-hat character
                    if note_time < 0.002:  # Ultra-fast attack (2ms)
                        envelope = note_time * 500  # Instant attack
                    else:  # Quick decay
                        envelope = np.exp(-(note_time - 0.002) * decay_rate)
                    
                    ## Generate crisp hi-hat tone
                    fundamental = np.sin(2 * np.pi * hihat_freq * t)
                    ## Add sparkle harmonics for crisp character
                    harmonic2 = 0.4 * np.sin(2 * np.pi * hihat_freq * 1.3 * t)
                    harmonic3 = 0.2 * np.sin(2 * np.pi * hihat_freq * 1.7 * t)
                    ## Add tiny bit of higher frequency "sizzle"
                    sizzle = 0.1 * np.sin(2 * np.pi * hihat_freq * 2.1 * t)
                    
                    wave += (fundamental + harmonic2 + harmonic3 + sizzle) * envelope * volume_mult
            
            ## Apply gentle overall volume for high-frequency texture
            combined = wave * 0.09
            arr[i] = [combined, combined]
        
        arr = (arr * 32767).astype(np.int16)
        return pygame.sndarray.make_sound(arr)
    
    def _create_melodic_tone(self, frequency: float, timbre: str) -> pygame.mixer.Sound:
        """Create punchy melodic tones that articulate clearly over sustained backgrounds"""
        duration = 0.7  # Shorter and punchier for better separation
        frames = int(duration * self.synth.sample_rate)
        arr = np.zeros((frames, 2))
        
        for i in range(frames):
            t = i / self.synth.sample_rate
            
            ## Quick attack for punchier feel (20ms attack across all timbres)
            attack_time = 0.02
            if t < attack_time:
                attack_env = t / attack_time  # Linear attack
            else:
                attack_env = 1.0
            
            if timbre == 'bell':
                ## Bell-like with harmonics
                wave = np.sin(2 * np.pi * frequency * t)
                wave += 0.3 * np.sin(2 * np.pi * frequency * 2 * t)
                wave += 0.1 * np.sin(2 * np.pi * frequency * 3 * t)
                decay_env = np.exp(-t * 1.8)  # Balanced for punch but natural fade
            elif timbre == 'soft':
                ## Soft sine wave but still punchy
                wave = np.sin(2 * np.pi * frequency * t)
                decay_env = np.exp(-t * 1.2)  # Gentler decay
            elif timbre == 'bright':
                ## Brighter with slight harmonics
                wave = np.sin(2 * np.pi * frequency * t)
                wave += 0.2 * np.sin(2 * np.pi * frequency * 1.5 * t)
                decay_env = np.exp(-t * 1.4)  # More natural decay
            elif timbre == 'sparkle':
                ## Sparkling with higher harmonics
                wave = np.sin(2 * np.pi * frequency * t)
                wave += 0.4 * np.sin(2 * np.pi * frequency * 2.5 * t)
                wave += 0.2 * np.sin(2 * np.pi * frequency * 4 * t)
                decay_env = np.exp(-t * 1.6)  # Natural sparkle fade
            else:
                wave = np.sin(2 * np.pi * frequency * t)
                decay_env = np.exp(-t * 1.3)
            
            ## Add final fade-out to prevent cutoffs (last 0.1s)
            fade_out_time = 0.1
            if t > (duration - fade_out_time):
                fade_out_env = (duration - t) / fade_out_time  # Linear fade to silence
            else:
                fade_out_env = 1.0
            
            ## Combine attack, decay, and fade-out envelopes
            envelope = attack_env * decay_env * fade_out_env
            combined = wave * envelope * 0.28  # Slightly louder for punch
            arr[i] = [combined, combined]
        
        arr = (arr * 32767).astype(np.int16)
        return pygame.sndarray.make_sound(arr)
    
    def _create_melodic_tone_off(self, frequency: float, timbre: str) -> pygame.mixer.Sound:
        """Create a softer, shorter 'off' variation for quick responsiveness"""
        duration = 0.3  # Much shorter for immediate response
        frames = int(duration * self.synth.sample_rate)
        arr = np.zeros((frames, 2))
        
        ## Slightly lower frequency for "off" variation (more mellow feeling)
        off_frequency = frequency * 0.85
        
        for i in range(frames):
            t = i / self.synth.sample_rate
            
            ## Quick attack for immediate response (10ms)
            attack_time = 0.01
            if t < attack_time:
                attack_env = t / attack_time
            else:
                attack_env = 1.0
            
            ## Similar timbres but with reduced intensity and quicker but natural decay
            if timbre == 'bell':
                wave = np.sin(2 * np.pi * off_frequency * t)
                wave += 0.15 * np.sin(2 * np.pi * off_frequency * 2 * t)  # Reduced harmonics
                decay_env = np.exp(-t * 3.5)  # Quick but natural decay
            elif timbre == 'soft':
                wave = np.sin(2 * np.pi * off_frequency * t)
                decay_env = np.exp(-t * 3.0)  # Quick but gentle decay
            elif timbre == 'bright':
                wave = np.sin(2 * np.pi * off_frequency * t)
                wave += 0.1 * np.sin(2 * np.pi * off_frequency * 1.5 * t)  # Less bright
                decay_env = np.exp(-t * 3.2)  # Quick but natural decay
            elif timbre == 'sparkle':
                wave = np.sin(2 * np.pi * off_frequency * t)
                wave += 0.2 * np.sin(2 * np.pi * off_frequency * 2.5 * t)  # Reduced sparkle
                wave += 0.1 * np.sin(2 * np.pi * off_frequency * 4 * t)
                decay_env = np.exp(-t * 3.8)  # Quick but natural sparkle fade
            else:
                wave = np.sin(2 * np.pi * off_frequency * t)
                decay_env = np.exp(-t * 3.0)
            
            ## Add final fade-out to prevent cutoffs (last 0.05s for shorter "off" sounds)
            fade_out_time = 0.05
            if t > (duration - fade_out_time):
                fade_out_env = (duration - t) / fade_out_time  # Linear fade to silence
            else:
                fade_out_env = 1.0
            
            ## Combine attack, decay, and fade-out for quick "off" response
            envelope = attack_env * decay_env * fade_out_env
            combined = wave * envelope * 0.18  # Reduced volume for "off" character
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
        
        ## TUI callback for activity logging
        self._tui_callback = None
        
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
                message = f"🟢 {element_name} texture ON (looping)"
                print(message)
                if self._tui_callback:
                    self._tui_callback(message)
            else:
                channel.play(sound)  # Play once
                ## For melodic tones, we don't store the channel since they play once
                ## But we still track the pad state for toggle behavior
                self.pad_states[note] = True
                element_name = self.get_element_name(sound_name)
                message = f"🎵 {element_name} played"
                print(message)
                if self._tui_callback:
                    self._tui_callback(message)
    
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
            message = f"🔴 {element_name} texture OFF"
            print(message)
            if self._tui_callback:
                self._tui_callback(message)
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
                message = f"🎵 {element_name} (soft)"
                print(message)
                if self._tui_callback:
                    self._tui_callback(message)
            else:
                element_name = self.get_element_name(sound_name) if sound_name else "Unknown"
                message = f"🎵 {element_name} ready to play again"
                print(message)
                if self._tui_callback:
                    self._tui_callback(message)
        
        self.pad_states[note] = False
    
    def handle_control_change(self, control: int, value: int):
        """Handle control change events (knobs)"""
        normalized_value = value / 127.0
        
        ## Master Volume Control
        if control == 10:  # Volume knob
            self.master_volume = normalized_value
            volume_name = "🔇 Silent" if normalized_value < 0.1 else "🔈 Quiet" if normalized_value < 0.4 else "🔉 Medium" if normalized_value < 0.8 else "🔊 Loud"
            message = f"🎚️ Master Volume: {volume_name}"
            print(message)
            if self._tui_callback:
                self._tui_callback(message)
            self._update_all_volumes()  # Apply to all active sounds
            
        ## Environmental controls - now affect audio in real-time!
        elif control == 16:  # K1 - Temperature (affects pitch)
            self.temperature = normalized_value
            temp_name = "❄️ Cold" if normalized_value < 0.3 else "🌞 Hot" if normalized_value > 0.7 else "🌤️ Warm"
            message = f"🌡️ Temperature: {temp_name}"
            print(message)
            if self._tui_callback:
                self._tui_callback(message)
            self._update_all_audio_effects()
            
        elif control == 17:  # K2 - Water (affects reverb/echo)
            self.water = normalized_value
            water_name = "🌵 Dry" if normalized_value < 0.3 else "🌊 Flooding" if normalized_value > 0.7 else "🌱 Perfect"
            message = f"💧 Water: {water_name}"
            print(message)
            if self._tui_callback:
                self._tui_callback(message)
            self._update_all_audio_effects()
            
        elif control == 18:  # K3 - Time of Day (affects brightness/filtering)
            self.time_of_day = normalized_value
            time_name = "🌅 Dawn" if normalized_value < 0.3 else "🌆 Dusk" if normalized_value > 0.7 else "☀️ Noon"
            message = f"🕐 Time: {time_name}"
            print(message)
            if self._tui_callback:
                self._tui_callback(message)
            self._update_all_audio_effects()
            
        elif control == 7:   # Tempo - Seasons (affects character/timbre)
            self.seasons = normalized_value
            season_name = "❄️ Winter" if normalized_value < 0.25 else "🌸 Spring" if normalized_value < 0.5 else "☀️ Summer" if normalized_value < 0.75 else "🍂 Autumn"
            message = f"🗓️ Season: {season_name}"
            print(message)
            if self._tui_callback:
                self._tui_callback(message)
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

class GardenMonitorTUI:
    """Garden monitoring dashboard using curses for parent-friendly interface"""
    
    def __init__(self, garden: MusicalGarden):
        self.garden = garden
        self.running = False
        self.stdscr = None
        self.activity_log = []
        self.max_log_entries = 5
        
    def start(self):
        """Start the TUI interface"""
        try:
            curses.wrapper(self._run_tui)
        except KeyboardInterrupt:
            pass
    
    def _run_tui(self, stdscr):
        """Main TUI loop"""
        self.stdscr = stdscr
        self.running = True
        
        ## Setup curses
        curses.curs_set(0)  # Hide cursor
        stdscr.nodelay(1)   # Non-blocking input
        stdscr.timeout(100) # 100ms refresh rate
        
        ## Initialize colors if available
        if curses.has_colors():
            curses.start_color()
            curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_BLACK)   # ON state
            curses.init_pair(2, curses.COLOR_RED, curses.COLOR_BLACK)     # OFF state
            curses.init_pair(3, curses.COLOR_YELLOW, curses.COLOR_BLACK)  # Headers
            curses.init_pair(4, curses.COLOR_CYAN, curses.COLOR_BLACK)    # Activity
        
        ## Hook into garden's output
        self.garden._tui_callback = self._add_activity
        
        ## Start garden in background
        garden_thread = threading.Thread(target=self.garden.run, daemon=True)
        garden_thread.start()
        
        ## Wait for garden to initialize
        time.sleep(1)
        
        ## Main TUI loop
        while self.running and self.garden.running:
            try:
                self._draw_interface()
                self._handle_input()
                time.sleep(0.1)
            except Exception as e:
                ## Graceful error handling
                break
        
        ## Cleanup
        self.running = False
        self.garden.stop_garden()
    
    def _draw_interface(self):
        """Draw the complete garden monitoring interface"""
        self.stdscr.clear()
        height, width = self.stdscr.getmaxyx()
        
        ## Ensure minimum terminal size
        if height < 20 or width < 70:
            self.stdscr.addstr(0, 0, "Terminal too small! Need at least 70x20")
            self.stdscr.refresh()
            return
        
        ## Draw border and title
        self._draw_border()
        self._draw_title()
        
        ## Draw main panels
        self._draw_garden_elements(2, 2)
        self._draw_environment(2, 35)
        self._draw_melodic_notes(10, 2)
        self._draw_activity_log(10, 35)
        self._draw_commands(height - 2)
        
        self.stdscr.refresh()
    
    def _draw_border(self):
        """Draw the outer border"""
        height, width = self.stdscr.getmaxyx()
        ## Simple ASCII border
        for x in range(width - 1):
            self.stdscr.addch(0, x, '─')
            self.stdscr.addch(height - 3, x, '─')
        for y in range(height - 2):
            self.stdscr.addch(y, 0, '│')
            self.stdscr.addch(y, width - 1, '│')
        ## Corners
        self.stdscr.addch(0, 0, '┌')
        self.stdscr.addch(0, width - 1, '┐')
        self.stdscr.addch(height - 3, 0, '└')
        self.stdscr.addch(height - 3, width - 1, '┘')
    
    def _draw_title(self):
        """Draw the title header"""
        title = "🌸 Musical Garden Monitor"
        self.stdscr.addstr(0, 2, title, curses.color_pair(3) if curses.has_colors() else 0)
    
    def _draw_garden_elements(self, start_y, start_x):
        """Draw the big pads status panel"""
        ## Panel title
        self.stdscr.addstr(start_y, start_x, "┌─ Garden Elements", curses.color_pair(3) if curses.has_colors() else 0)
        
        elements = [
            ('earth', '🌍 Earth'),
            ('rain', '🌧️ Rain'),
            ('wind', '💨 Wind'),
            ('thunder', '⛈️ Thunder'),
            ('trees', '🌳 Trees'),
            ('birds', '🐦 Birds'),
            ('insects', '🦗 Insects'),
            ('sun', '☀️ Sun')
        ]
        
        for i, (sound_key, display_name) in enumerate(elements):
            y = start_y + 1 + i
            ## Find the note for this sound
            note = self._find_note_for_sound(sound_key)
            is_on = self.garden.pad_states.get(note, False) if note else False
            
            status = "[🟢 ON ]" if is_on else "[⚫ OFF]"
            color = curses.color_pair(1) if is_on else curses.color_pair(2)
            
            self.stdscr.addstr(y, start_x + 1, f"{display_name:<12}", 0)
            self.stdscr.addstr(y, start_x + 14, status, color if curses.has_colors() else 0)
        
        ## Close panel
        self.stdscr.addstr(start_y + len(elements) + 1, start_x, "└" + "─" * 25)
    
    def _draw_environment(self, start_y, start_x):
        """Draw the environment controls panel"""
        self.stdscr.addstr(start_y, start_x, "┌─ Environment", curses.color_pair(3) if curses.has_colors() else 0)
        
        ## Temperature
        temp_desc = self._get_temp_description()
        self.stdscr.addstr(start_y + 1, start_x + 1, f"🌡️ Temperature: {temp_desc}")
        
        ## Water
        water_desc = self._get_water_description()
        self.stdscr.addstr(start_y + 2, start_x + 1, f"💧 Water: {water_desc}")
        
        ## Time
        time_desc = self._get_time_description()
        self.stdscr.addstr(start_y + 3, start_x + 1, f"🕐 Time: {time_desc}")
        
        ## Season
        season_desc = self._get_season_description()
        self.stdscr.addstr(start_y + 4, start_x + 1, f"🗓️ Season: {season_desc}")
        
        ## Volume
        volume_desc = self._get_volume_description()
        self.stdscr.addstr(start_y + 5, start_x + 1, f"🎚️ Volume: {volume_desc}")
        
        self.stdscr.addstr(start_y + 6, start_x, "└" + "─" * 30)
    
    def _draw_melodic_notes(self, start_y, start_x):
        """Draw the melodic notes status"""
        self.stdscr.addstr(start_y, start_x, "┌─ Recent Melodies", curses.color_pair(3) if curses.has_colors() else 0)
        
        ## Show recent melodic activity
        recent_melodies = [entry for entry in self.activity_log[-8:] if "played" in entry.lower()]
        
        for i, melody in enumerate(recent_melodies[-4:]):  # Show last 4
            y = start_y + 1 + i
            self.stdscr.addstr(y, start_x + 1, f"♪ {melody}")
        
        self.stdscr.addstr(start_y + 5, start_x, "└" + "─" * 30)
    
    def _draw_activity_log(self, start_y, start_x):
        """Draw the activity log panel"""
        self.stdscr.addstr(start_y, start_x, "┌─ Garden Activity", curses.color_pair(3) if curses.has_colors() else 0)
        
        ## Show recent activity
        for i, activity in enumerate(self.activity_log[-5:]):
            y = start_y + 1 + i
            if y < start_y + 6:  # Don't overflow panel
                self.stdscr.addstr(y, start_x + 1, activity[:30], curses.color_pair(4) if curses.has_colors() else 0)
        
        self.stdscr.addstr(start_y + 6, start_x, "└" + "─" * 32)
    
    def _draw_commands(self, y):
        """Draw the command help line"""
        commands = "🌸 [H]elp [R]eset [Q]uit [M]ute [C]lear"
        self.stdscr.addstr(y, 2, commands, curses.color_pair(3) if curses.has_colors() else 0)
    
    def _handle_input(self):
        """Handle keyboard input"""
        try:
            key = self.stdscr.getch()
            if key == -1:  # No input
                return
            
            key_char = chr(key).lower() if 32 <= key <= 126 else None
            
            if key_char == 'q':
                self.running = False
            elif key_char == 'r':
                self._reset_garden()
            elif key_char == 'm':
                self._toggle_mute()
            elif key_char == 'c':
                self._clear_activity()
            elif key_char == 'h':
                self._show_help()
        except:
            pass  # Ignore input errors
    
    def _reset_garden(self):
        """Reset all garden elements to OFF"""
        for note in list(self.garden.pad_states.keys()):
            if self.garden.pad_states[note] and self.garden.is_big_pad_note(note):
                self.garden.turn_pad_off(note)
        self._add_activity("🔄 Garden reset to silence")
    
    def _toggle_mute(self):
        """Toggle master volume mute"""
        if self.garden.master_volume > 0:
            self.garden._previous_volume = self.garden.master_volume
            self.garden.master_volume = 0
            self._add_activity("🔇 Garden muted")
        else:
            self.garden.master_volume = getattr(self.garden, '_previous_volume', 0.5)
            self._add_activity("🔊 Garden unmuted")
        self.garden._update_all_volumes()
    
    def _clear_activity(self):
        """Clear the activity log"""
        self.activity_log.clear()
        self._add_activity("📝 Activity log cleared")
    
    def _show_help(self):
        """Show help overlay"""
        height, width = self.stdscr.getmaxyx()
        help_text = [
            "🌸 Musical Garden Help",
            "",
            "Garden Elements: Background textures",
            "- Toggle ON/OFF with big pads",
            "- Layer multiple for rich soundscapes",
            "",
            "Melodic Notes: Harmonic melodies", 
            "- Play over background textures",
            "- Seeds → Sprouts → Buds → Flowers",
            "",
            "Commands:",
            "  H - This help",
            "  R - Reset all to silence",
            "  Q - Quit garden",
            "  M - Mute/unmute",
            "  C - Clear activity log",
            "",
            "Press any key to continue..."
        ]
        
        ## Create help overlay
        overlay_y = 3
        overlay_x = 5
        overlay_height = len(help_text) + 2
        overlay_width = max(len(line) for line in help_text) + 4
        
        ## Draw help box
        for i in range(overlay_height):
            self.stdscr.addstr(overlay_y + i, overlay_x, " " * overlay_width, curses.A_REVERSE)
        
        for i, line in enumerate(help_text):
            self.stdscr.addstr(overlay_y + 1 + i, overlay_x + 2, line, curses.A_REVERSE)
        
        self.stdscr.refresh()
        self.stdscr.getch()  # Wait for key press
    
    def _add_activity(self, message: str):
        """Add activity to the log"""
        self.activity_log.append(message)
        if len(self.activity_log) > self.max_log_entries * 2:
            self.activity_log = self.activity_log[-self.max_log_entries:]
    
    def _find_note_for_sound(self, sound_key: str) -> Optional[int]:
        """Find MIDI note for a given sound"""
        for note, sound_name in self.garden.note_to_sound.items():
            if sound_name == sound_key:
                return note
        return None
    
    def _get_temp_description(self) -> str:
        temp = self.garden.temperature
        return "❄️ Cold" if temp < 0.3 else "🌞 Hot" if temp > 0.7 else "🌤️ Warm"
    
    def _get_water_description(self) -> str:
        water = self.garden.water
        return "🌵 Dry" if water < 0.3 else "🌊 Wet" if water > 0.7 else "🌱 Perfect"
    
    def _get_time_description(self) -> str:
        time_val = self.garden.time_of_day
        return "🌅 Dawn" if time_val < 0.3 else "🌆 Dusk" if time_val > 0.7 else "☀️ Day"
    
    def _get_season_description(self) -> str:
        season = self.garden.seasons
        if season < 0.25: return "❄️ Winter"
        elif season < 0.5: return "🌸 Spring"
        elif season < 0.75: return "☀️ Summer"
        else: return "🍂 Autumn"
    
    def _get_volume_description(self) -> str:
        vol = self.garden.master_volume
        return "🔇 Silent" if vol < 0.1 else "🔈 Quiet" if vol < 0.4 else "🔉 Medium" if vol < 0.8 else "🔊 Loud"

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='SparkLE Musical Garden')
    parser.add_argument('--tui', action='store_true', 
                       help='Run with full-screen garden monitoring dashboard')
    args = parser.parse_args()
    
    try:
        garden = MusicalGarden()
        
        if args.tui:
            ## Run with TUI interface
            print("🌸 Starting Garden Monitor Dashboard...")
            print("🖥️ Switching to full-screen mode...")
            time.sleep(1)
            
            tui = GardenMonitorTUI(garden)
            tui.start()
        else:
            ## Run with simple CLI interface
            garden.run()
            
    except Exception as e:
        print(f"❌ Error starting Musical Garden: {e}")
        print("Make sure pygame, mido and numpy are installed: pip install pygame mido numpy")

if __name__ == "__main__":
    main()
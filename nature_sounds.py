#!/usr/bin/env python3
"""
Nature Sounds - Sound generation library for Musical Garden
Creates nature-themed sounds and melodic tones for toddler-friendly musical experiences
"""

import pygame
import numpy as np
import random
from typing import List
from audio_synthesizer import AudioSynthesizer

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
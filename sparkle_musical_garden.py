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
from typing import Optional
import mido
import pygame
from audio_synthesizer import AudioSynthesizer
from nature_sounds import NatureSounds


class MusicalGarden:
    """Main application managing the musical garden experience"""
    
    def __init__(self, virtual_mode=False):
        self.running = False
        self.midi_input = None
        self.virtual_mode = virtual_mode
        self.synthesizer = AudioSynthesizer()
        self.nature_sounds = NatureSounds(self.synthesizer)
        
        ## Volume controls
        self.master_volume = 0.5    # CC 10 - Overall level
        self.background_volume = 0.7 # CC 12 (Divide) - Big pads volume
        self.melody_volume = 0.6     # CC 13 (Move) - Number pads volume
        
        ## Environmental effects
        self.temperature = 0.5  # CC 16 (K1) - Pitch control (0.8x to 1.2x)
        self.water = 0.3        # CC 17 (K2) - Echo/delay effect
        self.time_of_day = 0.5  # CC 18 (K3) - Brightness/filtering
        self.seasons = 0.5      # CC 7 (Tempo) - Harmonic content
        
        ## Active sounds tracking
        self.active_sounds = {}
        
        ## Toggle states for each pad
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
        print("   Volume: 🎚️ Master | Divide: 🌍 Background | Move: 🎵 Melody")
        print("   K1 (Temperature): 🌡️ Pitch | K2 (Water): 💧 Echo")
        print("   K3 (Time): 🕐 Brightness | Tempo (Seasons): 🗓️ Harmonics")
        print("\n🎹 How it works:")
        print("   • Big Pads = Background textures (loop when ON)")
        print("   • Number Pads = Melodic notes (play over background)")
        print("   • Volume knobs = Mix background vs melody levels")
        print("   • Effect knobs = Real-time environmental control")
        print("   • Layer textures + melodies + adjust mix + add effects!")
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
            ## Calculate volume based on pad type
            velocity_volume = 0.1 + (velocity / 127.0) * 0.7
            if self.is_big_pad_note(note):
                final_volume = velocity_volume * self.master_volume * self.background_volume
            else:
                final_volume = velocity_volume * self.master_volume * self.melody_volume
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
                    ## Use melody volume for "off" sounds (softer)
                    final_volume = 0.4 * self.master_volume * self.melody_volume
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
        
        ## Volume Controls
        if control == 10:  # Master Volume
            self._set_master_volume(normalized_value)
        elif control == 12:  # Divide - Background Volume
            self._set_background_volume(normalized_value)
        elif control == 13:  # Move - Melody Volume
            self._set_melody_volume(normalized_value)
            
        ## Environmental Effects
        elif control == 16:  # K1 - Temperature (pitch)
            self._set_temperature(normalized_value)
        elif control == 17:  # K2 - Water (echo)
            self._set_water(normalized_value)
        elif control == 18:  # K3 - Time (brightness)
            self._set_time_of_day(normalized_value)
        elif control == 7:   # Tempo - Seasons (harmonics)
            self._set_seasons(normalized_value)
    
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
    
    ## Volume Control Methods
    
    def _set_master_volume(self, value: float):
        """Set master volume with feedback"""
        self.master_volume = value
        volume_desc = self._get_volume_description(value)
        message = f"🎚️ Master Volume: {volume_desc} ({int(value * 100)}%)"
        print(message)
        if self._tui_callback:
            self._tui_callback(message)
        self._update_all_volumes()
    
    def _set_background_volume(self, value: float):
        """Set background texture volume"""
        self.background_volume = value
        message = f"🎚️ Background: {int(value * 100)}%"
        print(message)
        if self._tui_callback:
            self._tui_callback(message)
        self._update_background_volumes()
    
    def _set_melody_volume(self, value: float):
        """Set melody volume"""
        self.melody_volume = value
        message = f"🎚️ Melody: {int(value * 100)}%"
        print(message)
        if self._tui_callback:
            self._tui_callback(message)
        # Melody volumes are applied when notes are played
    
    def _update_all_volumes(self):
        """Update volume for all active sounds"""
        self._update_background_volumes()
        # Melody sounds get volume applied when triggered
    
    def _update_background_volumes(self):
        """Update volume for background textures only"""
        for note, channel in self.active_sounds.items():
            if channel and channel.get_busy() and self.is_big_pad_note(note):
                sound_name = self.get_sound_name_for_note(note)
                if sound_name and sound_name in self.nature_sounds.sounds:
                    sound = self.nature_sounds.sounds[sound_name]
                    # Apply time-of-day brightness as volume modifier
                    brightness_modifier = 0.6 + (self.time_of_day * 0.4)  # 60% to 100%
                    final_volume = 0.6 * self.master_volume * self.background_volume * brightness_modifier
                    sound.set_volume(final_volume)
    
    def _get_volume_description(self, volume: float) -> str:
        """Get descriptive text for volume level"""
        if volume < 0.1: return "🔇 Silent"
        elif volume < 0.4: return "🔈 Quiet"
        elif volume < 0.8: return "🔉 Medium"
        else: return "🔊 Loud"
    
    ## Environmental Effect Methods
    
    def _set_temperature(self, value: float):
        """Set temperature with pitch effect"""
        self.temperature = value
        temp_desc = self._get_temperature_description(value)
        pitch_change = int((value - 0.5) * 40)  # -20% to +20%
        message = f"🌡️ Temperature: {temp_desc} (pitch {pitch_change:+d}%)"
        print(message)
        if self._tui_callback:
            self._tui_callback(message)
        # Note: Pitch effects would be applied to new sounds
    
    def _set_water(self, value: float):
        """Set water with echo effect"""
        self.water = value
        water_desc = self._get_water_description(value)
        echo_desc = "No Echo" if value < 0.3 else "Light Echo" if value < 0.7 else "Heavy Echo"
        message = f"💧 Water: {water_desc} ({echo_desc})"
        print(message)
        if self._tui_callback:
            self._tui_callback(message)
    
    def _set_time_of_day(self, value: float):
        """Set time of day with brightness effect"""
        self.time_of_day = value
        time_desc = self._get_time_description(value)
        brightness = int(60 + value * 40)  # 60% to 100% brightness
        message = f"🕐 Time: {time_desc} (brightness {brightness}%)"
        print(message)
        if self._tui_callback:
            self._tui_callback(message)
        self._update_background_volumes()  # Apply brightness as volume modifier
    
    def _set_seasons(self, value: float):
        """Set seasons with harmonic content"""
        self.seasons = value
        season_desc = self._get_season_description(value)
        harmonic_desc = "Minimal" if value < 0.25 else "Light" if value < 0.5 else "Rich" if value < 0.75 else "Full"
        message = f"🗓️ Season: {season_desc} ({harmonic_desc} harmonics)"
        print(message)
        if self._tui_callback:
            self._tui_callback(message)
    
    def _get_temperature_description(self, temp: float) -> str:
        if temp < 0.3: return "❄️ Cold"
        elif temp > 0.7: return "🌞 Hot"
        else: return "🌤️ Warm"
    
    def _get_water_description(self, water: float) -> str:
        if water < 0.3: return "🌵 Dry"
        elif water > 0.7: return "🌊 Wet"
        else: return "🌱 Fresh"
    
    def _get_time_description(self, time_val: float) -> str:
        if time_val < 0.3: return "🌅 Dawn"
        elif time_val > 0.7: return "🌆 Dusk"
        else: return "☀️ Day"
    
    def _get_season_description(self, season: float) -> str:
        if season < 0.25: return "❄️ Winter"
        elif season < 0.5: return "🌸 Spring"
        elif season < 0.75: return "☀️ Summer"
        else: return "🍂 Autumn"
    
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
            except Exception:
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
        self._draw_melodic_notes(11, 2)
        self._draw_activity_log(11, 35)
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
        master_desc = self._get_volume_description()
        background_pct = int(self.garden.background_volume * 100)
        melody_pct = int(self.garden.melody_volume * 100)
        self.stdscr.addstr(start_y + 5, start_x + 1, f"🎚️ Master: {master_desc}")
        self.stdscr.addstr(start_y + 6, start_x + 1, f"🌍 Background: {background_pct}%")
        self.stdscr.addstr(start_y + 7, start_x + 1, f"🎵 Melody: {melody_pct}%")
        
        self.stdscr.addstr(start_y + 8, start_x, "└" + "─" * 30)
    
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
        return self.garden._get_temperature_description(self.garden.temperature)
    
    def _get_water_description(self) -> str:
        return self.garden._get_water_description(self.garden.water)
    
    def _get_time_description(self) -> str:
        return self.garden._get_time_description(self.garden.time_of_day)
    
    def _get_season_description(self) -> str:
        return self.garden._get_season_description(self.garden.seasons)
    
    def _get_volume_description(self) -> str:
        return self.garden._get_volume_description(self.garden.master_volume)


class VirtualSparkleController:
    """Virtual SparkLE MIDI controller interface with visual feedback"""
    
    def __init__(self, garden: MusicalGarden):
        self.garden = garden
        self.running = False
        self.stdscr = None
        
        ## Virtual knob states (0-127)
        self.knob_states = {
            'master_volume': 64,      # CC 10
            'background_volume': 90,  # CC 12 
            'melody_volume': 77,      # CC 13
            'temperature': 64,        # CC 16 (K1)
            'water': 38,             # CC 17 (K2)
            'time_of_day': 64,       # CC 18 (K3)
            'seasons': 64            # CC 7 (Tempo)
        }
        
        ## Virtual pad states
        self.pad_states = {}
        for note in range(36, 67):  # All MIDI notes used
            self.pad_states[note] = False
            
        ## Keyboard to MIDI mapping
        self._setup_keyboard_mapping()
        
        ## Set up garden callback for activity logging
        self.activity_log = []
        self.max_log_entries = 5
        self.garden._tui_callback = self._add_activity
    
    def _setup_keyboard_mapping(self):
        """Create keyboard to MIDI note mapping"""
        ## Big pads mapping (2x4 grid)
        self.big_pad_keys = {
            'q': 36, 'w': 38, 'e': 42, 'r': 46,  # Earth, Rain, Wind, Thunder
            'a': 50, 's': 47, 'd': 43, 'f': 49   # Trees, Birds, Insects, Sun
        }
        
        ## Number pads mapping (4x4 grid)
        self.number_pad_keys = {
            ## Seeds (Row 1)
            '1': 51, '2': 52, '3': 53, '4': 54,
            ## Sprouts (Row 2)  
            '5': 55, '6': 56, '7': 57, '8': 58,
            ## Buds (Row 3)
            '9': 59, '0': 60, '-': 61, '=': 62,
            ## Flowers (Row 4)
            'z': 63, 'x': 64, 'c': 65, 'v': 66
        }
        
        ## Combine all pad mappings
        self.key_to_note = {**self.big_pad_keys, **self.number_pad_keys}
        
        ## Knob control keys
        self.knob_keys = {
            ## Environmental controls
            '[': ('temperature', -5), ']': ('temperature', 5),
            ';': ('water', -5), "'": ('water', 5),
            ',': ('time_of_day', -5), '.': ('time_of_day', 5),
            '/': ('seasons', -5), '\\': ('seasons', 5),
            ## Volume controls
            '-': ('master_volume', -5), '=': ('master_volume', 5),
            'j': ('background_volume', -5), 'k': ('background_volume', 5),
            'n': ('melody_volume', -5), 'm': ('melody_volume', 5)
        }
    
    def start(self):
        """Start the virtual controller interface"""
        try:
            ## Set up garden for virtual input
            self.garden.running = True
            print("🌸 Welcome to the Virtual Musical Garden! 🌸")
            print("This is a toddler-friendly musical playground using keyboard input.")
            print("Your virtual SparkLE controller is ready to play!")
            print()
            
            ## Initialize curses
            self.stdscr = curses.initscr()
            curses.noecho()
            curses.cbreak()
            self.stdscr.keypad(True)
            self.stdscr.nodelay(True)
            curses.start_color()
            curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_BLACK)   # Active pads
            curses.init_pair(2, curses.COLOR_YELLOW, curses.COLOR_BLACK)  # Headers
            curses.init_pair(3, curses.COLOR_CYAN, curses.COLOR_BLACK)    # Knob values
            curses.init_pair(4, curses.COLOR_RED, curses.COLOR_BLACK)     # Warnings
            
            ## Check minimum terminal size
            height, width = self.stdscr.getmaxyx()
            if height < 20 or width < 70:
                raise Exception(f"Terminal too small. Need 20x70, got {height}x{width}")
            
            self.running = True
            self._main_loop()
            
        except KeyboardInterrupt:
            pass
        except Exception as e:
            if self.stdscr:
                curses.endwin()
            print(f"❌ Virtual controller error: {e}")
        finally:
            self._cleanup()
    
    def _main_loop(self):
        """Main input and display loop"""
        while self.running:
            try:
                ## Clear screen and draw interface
                self.stdscr.clear()
                self._draw_interface()
                self.stdscr.refresh()
                
                ## Handle input (non-blocking)
                key = self.stdscr.getch()
                if key != -1:  # Key was pressed
                    self._handle_keypress(key)
                
                ## Small delay to prevent excessive CPU usage
                time.sleep(0.05)
                
            except KeyboardInterrupt:
                break
    
    def _handle_keypress(self, key):
        """Handle keyboard input"""
        try:
            ## Handle special keys first
            if key == 27:  # ESC key
                self.running = False
                return
            
            key_char = chr(key).lower() if 32 <= key <= 126 else None
            
            ## Special command keys (highest priority)
            if key_char == 'h':
                self._show_help()
                return
            elif key == 32:  # Space bar for reset
                self._reset_all()
                return
            
            ## Knob keys (higher priority than pads for shared keys)
            if key_char and key_char in self.knob_keys:
                knob_name, delta = self.knob_keys[key_char]
                self._adjust_knob(knob_name, delta)
                return
            
            ## Pad keys (note on/off toggle) - lowest priority
            if key_char and key_char in self.key_to_note:
                note = self.key_to_note[key_char]
                self._toggle_pad(note)
                
        except ValueError:
            pass  # Ignore non-printable characters
    
    def _toggle_pad(self, note: int):
        """Toggle virtual pad state and send MIDI event"""
        ## Use the garden's toggle system directly
        self.garden.handle_note_toggle(note, 100)  # Velocity 100
        
        ## Update our local state to match garden state
        self.pad_states[note] = self.garden.pad_states.get(note, False)
        
        ## Log the activity
        sound_name = self.garden.get_sound_name_for_note(note)
        if sound_name:
            state = "ON" if self.pad_states[note] else "OFF"
            self._add_activity(f"🎵 {sound_name.replace('_', ' ').title()} {state}")
    
    def _adjust_knob(self, knob_name: str, delta: int):
        """Adjust virtual knob value and send control change"""
        current = self.knob_states[knob_name]
        new_value = max(0, min(127, current + delta))
        self.knob_states[knob_name] = new_value
        
        ## Map knob to appropriate CC
        cc_mapping = {
            'master_volume': 10,
            'background_volume': 12,
            'melody_volume': 13,
            'temperature': 16,
            'water': 17,
            'time_of_day': 18,
            'seasons': 7
        }
        
        if knob_name in cc_mapping:
            cc_number = cc_mapping[knob_name]
            self.garden.handle_control_change(cc_number, new_value)
            self._add_activity(f"🎛️ {knob_name.replace('_', ' ').title()}: {new_value}")
    
    def _draw_interface(self):
        """Draw the virtual SparkLE controller interface"""
        height, width = self.stdscr.getmaxyx()
        
        ## Title
        title = "🎹 Virtual SparkLE Controller - Musical Garden"
        self.stdscr.addstr(0, (width - len(title)) // 2, title, curses.color_pair(2) | curses.A_BOLD)
        
        ## Instructions
        instructions = "Press H for help • ESC to quit • SPACE to reset • Keys toggle pads • []/;',./ adjust knobs"
        self.stdscr.addstr(1, (width - len(instructions)) // 2, instructions)
        
        ## Draw controller layout with proper spacing
        self._draw_big_pads(3, 2)
        self._draw_number_pads(3, 40)
        self._draw_knobs(12, 2)
        self._draw_garden_status(3, 75)
        self._draw_activity_log(23, 2)
    
    def _draw_big_pads(self, start_y: int, start_x: int):
        """Draw big pads section"""
        self.stdscr.addstr(start_y, start_x, "🌍 Garden Elements (Big Pads)", curses.color_pair(2))
        
        ## Draw 2x4 grid
        pad_layout = [
            [('Q', 36, 'Earth'), ('W', 38, 'Rain'), ('E', 42, 'Wind'), ('R', 46, 'Thunder')],
            [('A', 50, 'Trees'), ('S', 47, 'Birds'), ('D', 43, 'Insects'), ('F', 49, 'Sun')]
        ]
        
        for row_idx, row in enumerate(pad_layout):
            y = start_y + 2 + row_idx * 2
            for col_idx, (key, note, name) in enumerate(row):
                x = start_x + col_idx * 8
                active = self.pad_states[note]
                color = curses.color_pair(1) if active else 0
                status = "●" if active else "○"
                self.stdscr.addstr(y, x, f"[{key}] {status} {name}", color)
    
    def _draw_number_pads(self, start_y: int, start_x: int):
        """Draw number pads section"""
        self.stdscr.addstr(start_y, start_x, "🎵 Melodic Tones (Number Pads)", curses.color_pair(2))
        
        ## Draw 4x4 grid
        pad_layout = [
            [('1', 51, 'Seed'), ('2', 52, 'Seed'), ('3', 53, 'Seed'), ('4', 54, 'Seed')],
            [('5', 55, 'Sprout'), ('6', 56, 'Sprout'), ('7', 57, 'Sprout'), ('8', 58, 'Sprout')],
            [('9', 59, 'Bud'), ('0', 60, 'Bud'), ('-', 61, 'Bud'), ('=', 62, 'Bud')],
            [('Z', 63, 'Flower'), ('X', 64, 'Flower'), ('C', 65, 'Flower'), ('V', 66, 'Flower')]
        ]
        
        for row_idx, row in enumerate(pad_layout):
            y = start_y + 2 + row_idx
            for col_idx, (key, note, name) in enumerate(row):
                x = start_x + col_idx * 7
                active = self.pad_states[note]
                color = curses.color_pair(1) if active else 0
                status = "●" if active else "○"
                self.stdscr.addstr(y, x, f"{key}{status}", color)
        
        ## Add legend
        self.stdscr.addstr(start_y + 7, start_x, "Seeds→Sprouts→Buds→Flowers", curses.A_DIM)
    
    def _draw_knobs(self, start_y: int, start_x: int):
        """Draw knobs section"""
        self.stdscr.addstr(start_y, start_x, "🎛️ Environmental Controls", curses.color_pair(2))
        
        knob_info = [
            ('Temperature', 'temperature', '[]', self.garden._get_temperature_description(self.garden.temperature)),
            ('Water', 'water', ";'", self.garden._get_water_description(self.garden.water)),
            ('Time', 'time_of_day', ',.', self.garden._get_time_description(self.garden.time_of_day)),
            ('Seasons', 'seasons', '/\\', self.garden._get_season_description(self.garden.seasons))
        ]
        
        for i, (name, key, controls, desc) in enumerate(knob_info):
            y = start_y + 1 + i
            value = self.knob_states[key]
            bar = "█" * (value // 8) + "░" * (16 - value // 8)
            self.stdscr.addstr(y, start_x, f"{controls} {name:12} [{bar}] {value:3} - {desc}")
        
        ## Volume controls
        self.stdscr.addstr(start_y + 6, start_x, "🔊 Volume Controls", curses.color_pair(2))
        volume_info = [
            ('Master', 'master_volume', '-=', self.garden._get_volume_description(self.garden.master_volume)),
            ('Background', 'background_volume', 'jk', f"{int(self.garden.background_volume * 100)}%"),
            ('Melody', 'melody_volume', 'nm', f"{int(self.garden.melody_volume * 100)}%")
        ]
        
        for i, (name, key, controls, desc) in enumerate(volume_info):
            y = start_y + 7 + i
            value = self.knob_states[key]
            bar = "█" * (value // 8) + "░" * (16 - value // 8)
            self.stdscr.addstr(y, start_x, f"{controls} {name:10} [{bar}] {value:3} - {desc}")
    
    def _draw_garden_status(self, start_y: int, start_x: int):
        """Draw garden status section"""
        self.stdscr.addstr(start_y, start_x, "🌸 Garden Status", curses.color_pair(2))
        
        ## Count active sounds
        active_backgrounds = sum(1 for note in self.garden.note_to_sound.keys() 
                               if self.pad_states.get(note, False) and self.garden.is_big_pad_note(note))
        active_melodies = sum(1 for note in self.garden.note_to_sound.keys()
                            if self.pad_states.get(note, False) and not self.garden.is_big_pad_note(note))
        
        status_lines = [
            f"Active Backgrounds: {active_backgrounds}/8",
            f"Active Melodies: {active_melodies}/16",
            f"Master Volume: {int(self.garden.master_volume * 100)}%",
            "",
            "Environment:",
            f"  {self.garden._get_temperature_description(self.garden.temperature)}",
            f"  {self.garden._get_water_description(self.garden.water)}",
            f"  {self.garden._get_time_description(self.garden.time_of_day)}",
            f"  {self.garden._get_season_description(self.garden.seasons)}"
        ]
        
        for i, line in enumerate(status_lines):
            if i < 10:  # Prevent overflow
                self.stdscr.addstr(start_y + 1 + i, start_x, line)
    
    def _draw_activity_log(self, start_y: int, start_x: int):
        """Draw recent activity log"""
        height, width = self.stdscr.getmaxyx()
        
        self.stdscr.addstr(start_y, start_x, "📝 Recent Activity", curses.color_pair(2))
        
        ## Display recent activities
        recent_activities = self.activity_log[-self.max_log_entries:]
        for i, activity in enumerate(recent_activities):
            if start_y + 1 + i < height - 1:
                max_width = width - start_x - 2
                display_text = activity[:max_width] if len(activity) > max_width else activity
                self.stdscr.addstr(start_y + 1 + i, start_x, display_text)
    
    def _show_help(self):
        """Show help overlay"""
        help_text = [
            "🎹 Virtual SparkLE Controller Help",
            "",
            "Big Pads (Garden Elements):",
            "  QWER - Earth, Rain, Wind, Thunder",
            "  ASDF - Trees, Birds, Insects, Sun", 
            "",
            "Number Pads (Melodic Tones):",
            "  1234 - Seeds (low tones)",
            "  5678 - Sprouts (mid tones)",
            "  90-= - Buds (high tones)",
            "  ZXCV - Flowers (highest tones)",
            "",
            "Environmental Controls:",
            "  [] - Temperature (pitch)",
            "  ;' - Water (echo)", 
            "  ,. - Time of Day (brightness)",
            "  /\\ - Seasons (character)",
            "",
            "Volume Controls:",
            "  -= - Master Volume",
            "  jk - Background Volume",
            "  nm - Melody Volume",
            "",
            "Commands:",
            "  H - This help",
            "  SPACE - Reset all to silence",
            "  ESC - Quit",
            "",
            "Press any key to continue..."
        ]
        
        ## Create help overlay
        height, width = self.stdscr.getmaxyx()
        overlay_y = 2
        overlay_x = 5
        overlay_height = len(help_text) + 2
        overlay_width = max(len(line) for line in help_text) + 4
        
        ## Draw help box
        for i in range(overlay_height):
            if overlay_y + i < height:
                self.stdscr.addstr(overlay_y + i, overlay_x, " " * min(overlay_width, width - overlay_x), curses.A_REVERSE)
        
        for i, line in enumerate(help_text):
            if overlay_y + 1 + i < height:
                max_line_width = width - overlay_x - 4
                display_line = line[:max_line_width] if len(line) > max_line_width else line
                self.stdscr.addstr(overlay_y + 1 + i, overlay_x + 2, display_line, curses.A_REVERSE)
        
        self.stdscr.refresh()
        self.stdscr.getch()  # Wait for key press
    
    def _reset_all(self):
        """Reset all pads to silent state"""
        for note in self.pad_states:
            if self.pad_states[note]:  # If currently active
                self.garden.turn_pad_off(note)
                self.pad_states[note] = False
        
        self._add_activity("🔄 All sounds reset to silence")
    
    def _add_activity(self, message: str):
        """Add activity to the log"""
        timestamp = time.strftime("%H:%M:%S")
        self.activity_log.append(f"[{timestamp}] {message}")
        if len(self.activity_log) > self.max_log_entries * 2:
            self.activity_log = self.activity_log[-self.max_log_entries:]
    
    def _cleanup(self):
        """Clean up curses interface"""
        if self.stdscr:
            try:
                curses.endwin()
            except:
                pass  # Ignore endwin errors
        self.garden._complete_shutdown()


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='SparkLE Musical Garden')
    group = parser.add_mutually_exclusive_group()
    group.add_argument('--tui', action='store_true', 
                       help='Run with full-screen garden monitoring dashboard')
    group.add_argument('--simulator', action='store_true',
                       help='Run with virtual SparkLE controller interface')
    args = parser.parse_args()
    
    try:
        if args.simulator:
            garden = MusicalGarden(virtual_mode=True)
            print("🎹 Starting Virtual SparkLE Controller...")
            print("🖥️ Switching to full-screen mode...")
            time.sleep(1)
            
            simulator = VirtualSparkleController(garden)
            simulator.start()
        elif args.tui:
            garden = MusicalGarden(virtual_mode=False)
            print("🌸 Starting Garden Monitor Dashboard...")
            print("🖥️ Switching to full-screen mode...")
            time.sleep(1)
            
            tui = GardenMonitorTUI(garden)
            tui.start()
        else:
            garden = MusicalGarden(virtual_mode=False)
            garden.run()
            
    except Exception as e:
        print(f"❌ Error starting Musical Garden: {e}")
        print("Make sure pygame, mido and numpy are installed: pip install pygame mido numpy")

if __name__ == "__main__":
    main()
# MIDI Sparkle Project Structure

## Overview
This project contains two main applications for the Arturia SparkLE MIDI controller:
1. **Mario Pipe MIDI Monitor** - Visual feedback system with Mario-themed graphics
2. **SparkLE Musical Garden** - Audio-only toddler-friendly musical playground

## Project Structure

```
midi-sparkle/
├── README.md                       # Project overview and Musical Garden documentation
├── STRUCTURE.md                    # This file - project organization
├── SOUND-DESIGN.md                 # Comprehensive sound design documentation
├── requirements.txt                # Python dependencies
├── sparkle_musical_garden.py      # Main Musical Garden application
├── audio_synthesizer.py           # Core audio synthesis engine
├── nature_sounds.py               # Nature-themed sound generation library
├── arturia-sparkle-1280x762.jpg   # Controller reference image
├── setup/
│   ├── sparkle_mapping.json       # MIDI controller mappings
│   └── setup_mapping.py           # Tool to create/edit MIDI mappings
└── deprecated/
    ├── midi_monitor.py             # Original Mario Pipe monitor (deprecated)
    └── toddler-sparkle-app-design.md # Design specification for Musical Garden
```

## Applications

### 1. SparkLE Musical Garden (`sparkle_musical_garden.py`)
**Purpose**: Audio-only musical playground designed for 1.8-year-old toddlers  
**Features**:
- Nature-themed sounds (Earth, Rain, Wind, Thunder, Trees, Birds, Insects, Sun)
- Progressive musical complexity (Seeds → Sprouts → Buds → Flowers)
- Interactive knob controls (Master Volume + 4 environmental effects)
- Real-time audio manipulation (Temperature→Pitch, Water→Echo, Time→Brightness, Seasons→Character)
- Toddler-safe audio processing (volume limits, frequency range 200Hz-4kHz)
- Opening and closing rituals for structured play sessions
- **Two Interface Modes**:
  - Simple CLI with minimal text feedback (default)
  - Garden Monitor Dashboard with full-screen TUI (`--tui` flag)

**Key Classes**:
- `AudioSynthesizer` (`audio_synthesizer.py`): Generates natural-sounding audio
- `NatureSounds` (`nature_sounds.py`): Collection of nature-themed sounds  
- `MusicalGarden`: Main application controller
- `GardenMonitorTUI`: Parent-friendly monitoring dashboard (curses-based)

### 2. Mario Pipe MIDI Monitor (`deprecated/midi_monitor.py`)
**Purpose**: Visual MIDI monitor with Mario-themed pipe graphics  
**Status**: Deprecated in favor of Musical Garden  
**Features**:
- 8-bit style green pipe animations
- Real-time button press visualization
- 4x4 grid layout matching SparkLE number pads

### 3. Design Documentation (`deprecated/toddler-sparkle-app-design.md`)
**Purpose**: Original design specification for the Musical Garden
**Status**: Moved to deprecated as implementation is complete
**Content**: Detailed design philosophy and psychological considerations for toddler development

## Configuration Files

### `setup/sparkle_mapping.json`
Contains MIDI mappings for the Arturia SparkLE controller:
- **big_pads**: 8 large drum pads (MIDI notes 36-49)
- **numbers**: 16 small numbered pads (MIDI notes 51-66)
- **parameter_knobs**: 3 parameter knobs (K1-K3, CC 16-18) - **ACTIVE**: Environmental controls
- **context_knobs**: 4 context knobs (Tempo, Volume, Divide, Move) - **VOLUME ACTIVE**: CC 10 master volume, CC 7 seasons
- **presets**: 4 preset knobs (Bank, Pattern, Sequence, Tune) - Available for future features
- **loop_controls**: 4 loop control knobs - Available for future features  
- **global_pads**: 6 global effect pads - Available for future features
- **control_pads**: 7 control pads - Available for future features

### `requirements.txt`
Python dependencies:
- `mido>=1.2.10` - MIDI I/O library
- `pygame>=2.5.0` - Audio playback and synthesis
- `numpy>=1.21.0` - Numerical operations for audio processing
- `python-rtmidi>=1.4.0` - Real-time MIDI support



## Usage

### Running the Musical Garden
```bash
# Install dependencies
pip install -r requirements.txt

# Run with simple CLI interface (default - requires hardware)
python sparkle_musical_garden.py

# Run with Garden Monitor Dashboard (parent-friendly TUI - requires hardware)
python sparkle_musical_garden.py --tui

# Run with Virtual SparkLE Controller (for testing without hardware)
python sparkle_musical_garden.py --simulator
```

### Interface Modes

#### Simple CLI Mode (Default)
- Minimal console output for clean operation
- Essential status messages and garden state updates
- Perfect for headless operation or minimal distraction
- All audio functionality and MIDI control unchanged
- **Requires SparkLE MIDI controller hardware**

#### Garden Monitor Dashboard (TUI Mode)
- Full-screen curses-based monitoring interface
- Real-time visual status of all garden elements (ON/OFF states)
- Live environmental parameter display (Temperature, Water, Time, Season, Volume)
- Parent-friendly controls: `[H]elp` `[R]eset` `[Q]uit` `[M]ute` `[C]lear`
- Activity logging with recent melodies and garden interactions
- Minimum terminal size: 70x20 characters
- Uses built-in `curses` library - no additional dependencies
- **Requires SparkLE MIDI controller hardware**

#### Virtual Controller Mode (Simulator)
- Full-screen virtual SparkLE controller interface
- Keyboard-based input instead of MIDI hardware
- Visual representation of all pads and knobs with real-time feedback
- All garden functionality available without physical controller
- Perfect for testing, development, or when hardware is unavailable
- Includes integrated garden monitoring (combines TUI + controller simulation)
- Minimum terminal size: 70x20 characters
- **No MIDI hardware required**

**Virtual Controller Keyboard Mapping:**
- **Big Pads**: QWET (top row), ASDF (bottom row) - Garden Elements
- **Number Pads**: 1234/5678/90-=/ZXCV (4x4 grid) - Melodic Tones  
- **Environmental Knobs**: []/;',./, /\\ - Temperature, Water, Time, Seasons
- **Volume Controls**: -=/jk/nm - Master, Background, Melody
- **Commands**: H (help), R (reset), ESC (quit)

### Setting up MIDI Mappings
```bash
# Create or edit MIDI mappings
python setup/setup_mapping.py
```

## Design Philosophy

The Musical Garden follows these principles:
- **Safety First**: All audio is limited in volume and frequency range
- **Nature Theme**: Uses natural sounds and concepts rather than synthetic ones
- **Progressive Learning**: Complexity increases naturally as child explores
- **No Failure States**: Everything is "correct" - focus on exploration
- **Parent-Friendly**: Simple monitoring interface for adults

## Development Notes

- **Modular Architecture**: Refactored into focused modules for maintainability
  - `audio_synthesizer.py`: Core synthesis engine (independent)
  - `nature_sounds.py`: Sound library (depends on AudioSynthesizer)
  - `sparkle_musical_garden.py`: Main application (imports both modules)
- Audio synthesis uses pentatonic scales to avoid dissonance
- All sounds have soft attack/release envelopes for gentle experience
- MIDI processing includes proper note_on/note_off handling
- Threading is used for real-time MIDI monitoring and status updates
- TUI interface uses built-in curses library for cross-platform terminal UI
- Clean dependency chain enables testing and reuse of sound modules
- Error handling ensures graceful degradation if MIDI device is unavailable

## Future Enhancements

Potential additions based on child development:
- **Phase 2 (2-2.5 years)**: Pattern recognition games
- **Phase 3 (2.5-3 years)**: Simple melodies and call-response
- Recording functionality for capturing musical moments
- Additional nature sound variations based on environmental controls
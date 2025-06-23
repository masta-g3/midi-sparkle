# MIDI Sparkle Project Structure

## Overview
This project contains two main applications for the Arturia SparkLE MIDI controller:
1. **Mario Pipe MIDI Monitor** - Visual feedback system with Mario-themed graphics
2. **SparkLE Musical Garden** - Audio-only toddler-friendly musical playground

## Project Structure

```
midi-sparkle/
├── README.md                       # Project overview and Mario Pipe documentation
├── STRUCTURE.md                    # This file - project organization
├── requirements.txt                # Python dependencies
├── sparkle_mapping.json           # MIDI controller mappings
├── setup_mapping.py               # Tool to create/edit MIDI mappings
├── toddler-sparkle-app-design.md  # Design specification for Musical Garden
├── sparkle_musical_garden.py      # Main Musical Garden application
├── arturia-sparkle-1280x762.jpg   # Controller reference image
└── deprecated/
    └── midi_monitor.py             # Original Mario Pipe monitor (deprecated)
```

## Applications

### 1. SparkLE Musical Garden (`sparkle_musical_garden.py`)
**Purpose**: Audio-only musical playground designed for 1.8-year-old toddlers  
**Features**:
- Nature-themed sounds (Earth, Rain, Wind, Thunder, Trees, Birds, Insects, Sun)
- Progressive musical complexity (Seeds → Sprouts → Buds → Flowers)
- Environmental controls via knobs (Temperature, Water, Time of Day, Seasons)
- Toddler-safe audio processing (volume limits, frequency range 200Hz-4kHz)
- Opening and closing rituals for structured play sessions
- Parent monitoring GUI with simple visual feedback

**Key Classes**:
- `AudioSynthesizer`: Generates natural-sounding audio
- `NatureSounds`: Collection of nature-themed sounds
- `MusicalGarden`: Main application controller

### 2. Mario Pipe MIDI Monitor (`deprecated/midi_monitor.py`)
**Purpose**: Visual MIDI monitor with Mario-themed pipe graphics  
**Status**: Deprecated in favor of Musical Garden  
**Features**:
- 8-bit style green pipe animations
- Real-time button press visualization
- 4x4 grid layout matching SparkLE number pads

## Configuration Files

### `sparkle_mapping.json`
Contains MIDI mappings for the Arturia SparkLE controller:
- **big_pads**: 8 large drum pads (MIDI notes 36-49)
- **numbers**: 16 small numbered pads (MIDI notes 51-66)
- **parameter_knobs**: 3 parameter knobs (K1-K3, CC 16-18)
- **context_knobs**: 4 context knobs (Tempo, Volume, Divide, Move)
- **presets**: 4 preset knobs (Bank, Pattern, Sequence, Tune)
- **loop_controls**: 4 loop control knobs
- **global_pads**: 6 global effect pads
- **control_pads**: 7 control pads

### `requirements.txt`
Python dependencies:
- `mido>=1.2.10` - MIDI I/O library
- `pygame>=2.5.0` - Audio playback and synthesis
- `numpy>=1.21.0` - Numerical operations for audio processing

## Usage

### Running the Musical Garden
```bash
# Install dependencies
pip install -r requirements.txt

# Run the application
python sparkle_musical_garden.py
```

### Setting up MIDI Mappings
```bash
# Create or edit MIDI mappings
python setup_mapping.py
```

## Design Philosophy

The Musical Garden follows these principles:
- **Safety First**: All audio is limited in volume and frequency range
- **Nature Theme**: Uses natural sounds and concepts rather than synthetic ones
- **Progressive Learning**: Complexity increases naturally as child explores
- **No Failure States**: Everything is "correct" - focus on exploration
- **Parent-Friendly**: Simple monitoring interface for adults

## Development Notes

- Audio synthesis uses pentatonic scales to avoid dissonance
- All sounds have soft attack/release envelopes for gentle experience
- MIDI processing includes proper note_on/note_off handling
- Threading is used for real-time MIDI monitoring and GUI updates
- Error handling ensures graceful degradation if MIDI device is unavailable

## Future Enhancements

Potential additions based on child development:
- **Phase 2 (2-2.5 years)**: Pattern recognition games
- **Phase 3 (2.5-3 years)**: Simple melodies and call-response
- Recording functionality for capturing musical moments
- Additional nature sound variations based on environmental controls
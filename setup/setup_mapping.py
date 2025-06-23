import mido
import json
import time
import os
from threading import Thread
import queue

class MIDIMapper:
    def __init__(self):
        self.midi_input = None
        self.running = True
        self.message_queue = queue.Queue()
        self.mapping = {}
        self.current_group = []
        self.current_filename = "sparkle_mapping.json"
        self.setup_midi()
    
    def setup_midi(self):
        """Setup MIDI input connection"""
        try:
            inputs = mido.get_input_names()
            print("\n🎹 Available MIDI devices:")
            for i, name in enumerate(inputs):
                print(f"  {i}: {name}")
            
            # Try to find SparkLE automatically
            sparkle_port = None
            for name in inputs:
                if 'spark' in name.lower() or 'arturia' in name.lower():
                    sparkle_port = name
                    break
            
            if sparkle_port:
                self.midi_input = mido.open_input(sparkle_port)
                print(f"\n✅ Auto-connected to: {sparkle_port}")
            elif inputs:
                print(f"\n❓ SparkLE not found. Use device 0? ({inputs[0]}) [y/n]: ", end="")
                choice = input().lower()
                if choice == 'y' or choice == '':
                    self.midi_input = mido.open_input(inputs[0])
                    print(f"✅ Connected to: {inputs[0]}")
                else:
                    print("Enter device number: ", end="")
                    device_num = int(input())
                    self.midi_input = mido.open_input(inputs[device_num])
                    print(f"✅ Connected to: {inputs[device_num]}")
            else:
                print("❌ No MIDI devices found!")
                return
                
        except Exception as e:
            print(f"❌ MIDI setup error: {e}")
            return
    
    def midi_thread(self):
        """MIDI input thread - captures all MIDI messages"""
        if not self.midi_input:
            return
            
        try:
            for msg in self.midi_input:
                if not self.running:
                    break
                
                # Only capture note_on, note_off, and control_change messages
                if msg.type in ['note_on', 'note_off', 'control_change']:
                    self.message_queue.put(msg)
                    
        except Exception as e:
            print(f"❌ MIDI thread error: {e}")
    
    def get_message_info(self, msg):
        """Extract useful info from MIDI message"""
        if msg.type == 'note_on':
            return {
                'type': 'button',
                'id': msg.note,
                'name': f"Pad {msg.note}",
                'midi_type': 'note_on',
                'midi_channel': msg.channel,
                'midi_note': msg.note
            }
        elif msg.type == 'note_off':
            return {
                'type': 'button',
                'id': msg.note,
                'name': f"Pad {msg.note}",
                'midi_type': 'note_off', 
                'midi_channel': msg.channel,
                'midi_note': msg.note
            }
        elif msg.type == 'control_change':
            return {
                'type': 'knob',
                'id': msg.control,
                'name': f"Knob/Slider CC{msg.control}",
                'midi_type': 'control_change',
                'midi_channel': msg.channel,
                'midi_control': msg.control
            }
    
    def wait_for_controls(self, group_name):
        """Wait for user to press/turn controls, then press Enter"""
        print(f"\n🎯 Mapping group: '{group_name}'")
        print("   📝 Press/turn the controls you want in this group")
        print("   🏷️ For buttons: Both note_on and note_off events will be created automatically")
        print("   🏷️ After detecting a control, type a custom name for it (or press ENTER to keep default)")
        print("   ⏎ Press ENTER on empty line when done to save this group")
        print("   ❌ Type 'cancel' to cancel this group")
        print("\n   Controls detected:")
        
        seen_controls = set()
        controls_in_group = []
        waiting_for_name = None  # Track if we're waiting for a custom name
        
        while True:
            # Check for MIDI messages
            try:
                msg = self.message_queue.get_nowait()
                control_info = self.get_message_info(msg)
                
                # Create unique ID for this control (for buttons, ignore note_on/note_off distinction)
                if control_info['type'] == 'button':
                    unique_id = f"button_{control_info['id']}"
                else:
                    unique_id = f"knob_{control_info['id']}"
                
                # Only add if we haven't seen this control yet
                if unique_id not in seen_controls and waiting_for_name is None:
                    seen_controls.add(unique_id)
                    waiting_for_name = control_info
                    
                    # Show what was detected and ask for name
                    control_type = "🔘" if control_info['type'] == 'button' else "🎛️"
                    if control_info['type'] == 'button':
                        print(f"   {control_type} Detected: {control_info['name']} (will create both ON and OFF events)")
                    else:
                        print(f"   {control_type} Detected: {control_info['name']}")
                    print(f"      💭 Enter custom name (or ENTER for default): ", end="", flush=True)
                    
            except queue.Empty:
                pass
            
            # Check for keyboard input (non-blocking)
            import select
            import sys
            
            if select.select([sys.stdin], [], [], 0)[0]:
                user_input = input().strip()
                
                if waiting_for_name is not None:
                    # We're waiting for a custom name for the last detected control
                    if user_input.lower() == 'cancel':
                        print("   ❌ Control cancelled")
                        waiting_for_name = None
                        continue
                    
                    # Set custom name if provided, otherwise keep default
                    base_name = user_input if user_input else waiting_for_name['name']
                    
                    if waiting_for_name['type'] == 'button':
                        # Create both note_on and note_off entries for buttons
                        note_on_control = {
                            'type': 'button',
                            'id': waiting_for_name['id'],
                            'name': f"Pad {waiting_for_name['id']} ON",
                            'midi_type': 'note_on',
                            'midi_channel': waiting_for_name['midi_channel'],
                            'midi_note': waiting_for_name['midi_note']
                        }
                        
                        note_off_control = {
                            'type': 'button',
                            'id': waiting_for_name['id'],
                            'name': f"Pad {waiting_for_name['id']} OFF", 
                            'midi_type': 'note_off',
                            'midi_channel': waiting_for_name['midi_channel'],
                            'midi_note': waiting_for_name['midi_note']
                        }
                        
                        # Set custom names with _on and _off suffixes
                        if user_input:
                            note_on_control['custom_name'] = f"{base_name}_on"
                            note_off_control['custom_name'] = f"{base_name}_off"
                            print(f"      ✅ Created: '{base_name}_on' and '{base_name}_off'")
                        else:
                            print(f"      ✅ Created: '{note_on_control['name']}' and '{note_off_control['name']}'")
                        
                        controls_in_group.append(note_on_control)
                        controls_in_group.append(note_off_control)
                        
                    else:
                        # For knobs/sliders, create single entry as before
                        if user_input:
                            waiting_for_name['name'] = base_name
                            waiting_for_name['custom_name'] = base_name
                            print(f"      ✅ Named: '{base_name}'")
                        else:
                            print(f"      ✅ Using default: '{waiting_for_name['name']}'")
                        
                        controls_in_group.append(waiting_for_name)
                    
                    waiting_for_name = None
                    print("   📝 Continue pressing controls, or ENTER when done...")
                
                elif user_input.lower() == 'cancel':
                    print("   ❌ Group cancelled")
                    return None
                elif user_input == '':
                    if controls_in_group:
                        button_count = len([c for c in controls_in_group if c['type'] == 'button']) // 2
                        knob_count = len([c for c in controls_in_group if c['type'] == 'knob'])
                        total_physical_controls = button_count + knob_count
                        print(f"   ✅ Saved group '{group_name}' with {total_physical_controls} controls ({len(controls_in_group)} total events)")
                        return controls_in_group
                    else:
                        print("   ⚠️ No controls detected yet. Keep pressing/turning controls...")
                else:
                    print("   ❓ Press ENTER to save group, or 'cancel' to cancel")
            
            time.sleep(0.01)  # Small delay to prevent busy waiting
    
    def display_current_mapping(self, show_controls=True):
        """Show current mapping state"""
        if not self.mapping:
            print(f"\n📋 No groups mapped yet (File: {self.current_filename})")
            return
            
        print(f"\n📋 Current mapping: {self.current_filename} ({len(self.mapping)} groups)")
        for group_name, controls in self.mapping.items():
            # Count unique physical controls (buttons count as 1 even though they have 2 events)
            button_ids = set()
            knob_count = 0
            for control in controls:
                if control['type'] == 'button':
                    button_ids.add(control['id'])
                else:
                    knob_count += 1
            physical_controls = len(button_ids) + knob_count
            
            print(f"   🏷️ {group_name}: ({physical_controls} controls, {len(controls)} total events)")
            if show_controls:
                # Group button controls by ID for cleaner display
                button_groups = {}
                knob_controls = []
                
                for control in controls:
                    if control['type'] == 'button':
                        if control['id'] not in button_groups:
                            button_groups[control['id']] = {'on': None, 'off': None}
                        if control['midi_type'] == 'note_on':
                            button_groups[control['id']]['on'] = control
                        else:
                            button_groups[control['id']]['off'] = control
                    else:
                        knob_controls.append(control)
                
                # Display button groups
                for button_id in sorted(button_groups.keys()):
                    group = button_groups[button_id]
                    on_control = group['on']
                    off_control = group['off']
                    
                    # Get the base name (remove _on/_off suffix if present)
                    if on_control and 'custom_name' in on_control:
                        base_name = on_control['custom_name'].replace('_on', '')
                    elif off_control and 'custom_name' in off_control:
                        base_name = off_control['custom_name'].replace('_off', '')
                    else:
                        base_name = f"Pad {button_id}"
                    
                    print(f"      🔘 {base_name} (ID: {button_id})")
                    if on_control:
                        on_name = on_control.get('custom_name', on_control['name'])
                        print(f"         ├─ ON:  {on_name}")
                    if off_control:
                        off_name = off_control.get('custom_name', off_control['name'])
                        print(f"         └─ OFF: {off_name}")
                
                # Display knob controls
                for control in knob_controls:
                    control_type = "🎛️"
                    display_name = control.get('custom_name', control['name'])
                    midi_info = f"(ID: {control['id']})"
                    print(f"      {control_type} {display_name} {midi_info}")
                    if 'custom_name' in control and control.get('name') != control['custom_name']:
                        print(f"          └─ Original: {control['name']}")
    
    def save_mapping(self, filename=None):
        """Save mapping to JSON file"""
        if filename is None:
            filename = self.current_filename
            
        try:
            # Add metadata
            mapping_data = {
                "device_name": "Arturia SparkLE",
                "created_at": time.strftime("%Y-%m-%d %H:%M:%S"),
                "groups": self.mapping
            }
            
            with open(filename, 'w') as f:
                json.dump(mapping_data, f, indent=2)
            
            self.current_filename = filename
            print(f"\n💾 Mapping saved to '{filename}'")
            return True
        except Exception as e:
            print(f"❌ Error saving mapping: {e}")
            return False
    
    def load_existing_mapping(self, filename="sparkle_mapping.json"):
        """Load existing mapping if it exists"""
        try:
            with open(filename, 'r') as f:
                data = json.load(f)
                self.mapping = data.get('groups', {})
                self.current_filename = filename
                device_name = data.get('device_name', 'Unknown device')
                created_at = data.get('created_at', 'Unknown')
                print(f"📂 Loaded mapping from '{filename}'")
                print(f"   Device: {device_name}, Created: {created_at}")
                print(f"   Groups: {len(self.mapping)}")
                return True
        except FileNotFoundError:
            print(f"📂 File '{filename}' not found")
            return False
        except Exception as e:
            print(f"❌ Error loading mapping: {e}")
            return False
    
    def run_mapping_session(self):
        """Main mapping session"""
        print("🗺️ SparkLE MIDI Control Mapper")
        print("=" * 50)
        
        if not self.midi_input:
            print("❌ No MIDI device connected. Exiting.")
            return
        
        # Start MIDI thread
        midi_thread = Thread(target=self.midi_thread)
        midi_thread.daemon = True
        midi_thread.start()
        
        # Try to load existing mapping
        self.load_existing_mapping()
        
        print("\n📖 Instructions:")
        print("   • NEW GROUP: Enter a group name to create/edit")
        print("   • COMMANDS:")
        print("     - 'load' - Load a different mapping file")
        print("     - 'save [filename]' - Save current mapping")
        print("     - 'show' - Display current mapping")
        print("     - 'edit <group>' - Edit existing group")
        print("     - 'delete <group>' - Delete a group")
        print("     - 'done' - Finish and save")
        
        while True:
            self.display_current_mapping(show_controls=False)
            
            print(f"\n🏷️ Enter group name or command: ", end="")
            user_input = input().strip()
            
            if user_input.lower() == 'done':
                break
            elif user_input.lower() == 'show':
                self.display_current_mapping(show_controls=True)
                continue
            elif user_input.lower() == 'load':
                self.load_mapping_interactive()
                continue
            elif user_input.lower().startswith('save'):
                parts = user_input.split()
                filename = parts[1] if len(parts) > 1 else None
                if filename and not filename.endswith('.json'):
                    filename += '.json'
                self.save_mapping(filename)
                continue
            elif user_input.lower().startswith('edit '):
                group_to_edit = user_input[5:].strip()
                self.edit_group_interactive(group_to_edit)
                continue
            elif user_input.lower().startswith('delete '):
                group_to_delete = user_input[7:].strip()
                if group_to_delete in self.mapping:
                    print(f"⚠️ Delete group '{group_to_delete}'? [y/n]: ", end="")
                    if input().lower() == 'y':
                        del self.mapping[group_to_delete]
                        print(f"✅ Deleted group '{group_to_delete}'")
                else:
                    print(f"❌ Group '{group_to_delete}' not found")
                continue
            elif user_input == '':
                print("❓ Please enter a group name or command")
                continue
            
            group_name = user_input
            
            # Check if group already exists
            if group_name in self.mapping:
                print(f"⚠️ Group '{group_name}' exists. [o]verwrite, [e]dit, or [c]ancel? ", end="")
                choice = input().lower()
                if choice == 'e':
                    self.edit_group_interactive(group_name)
                    continue
                elif choice != 'o':
                    continue
            
            # Wait for controls
            controls = self.wait_for_controls(group_name)
            
            if controls:
                self.mapping[group_name] = controls
        
        # Save final mapping
        if self.mapping:
            self.save_mapping()
            self.display_final_summary()
        else:
            print("\n❌ No mapping created")
    
    def display_final_summary(self):
        """Display final mapping summary"""
        print("\n" + "=" * 50)
        print("✅ MAPPING COMPLETE!")
        print("=" * 50)
        
        # Count physical controls vs total events
        total_events = sum(len(controls) for controls in self.mapping.values())
        button_ids = set()
        knob_count = 0
        
        for controls in self.mapping.values():
            for control in controls:
                if control['type'] == 'button':
                    button_ids.add(control['id'])
                else:
                    knob_count += 1
        
        physical_controls = len(button_ids) + knob_count
        
        print(f"📊 Total: {len(self.mapping)} groups, {physical_controls} physical controls, {total_events} total events")
        print(f"📊 Buttons: {len(button_ids)} (each creates note_on + note_off events)")
        print(f"📊 Knobs/Sliders: {knob_count}")
        
        self.display_current_mapping()
        
        print(f"\n🔧 Usage in your code:")
        print(f"   import json")
        print(f"   with open('{self.current_filename}', 'r') as f:")
        print(f"       mapping = json.load(f)")
        print(f"   groups = mapping['groups']")
        print(f"")
        print(f"   # Access groups like: groups['your_group_name']")
        print(f"   # Each button now has separate note_on and note_off entries:")
        print(f"   # Example: groups['main_pads'][0]['midi_type'] == 'note_on'")
        print(f"   #          groups['main_pads'][1]['midi_type'] == 'note_off'")
    
    def cleanup(self):
        """Clean up resources"""
        self.running = False
        if self.midi_input:
            self.midi_input.close()

    def list_mapping_files(self):
        """List available JSON mapping files"""
        json_files = [f for f in os.listdir('.') if f.endswith('.json')]
        return json_files

    def load_mapping_interactive(self):
        """Interactive mapping file loader"""
        json_files = self.list_mapping_files()
        
        if not json_files:
            print("❌ No JSON files found in current directory")
            return False
            
        print(f"\n📂 Available mapping files:")
        for i, filename in enumerate(json_files):
            try:
                with open(filename, 'r') as f:
                    data = json.load(f)
                    groups_count = len(data.get('groups', {}))
                    created_at = data.get('created_at', 'Unknown')
                    device_name = data.get('device_name', 'Unknown device')
                print(f"  {i}: {filename} - {device_name} ({groups_count} groups, {created_at})")
            except:
                print(f"  {i}: {filename} - (Invalid JSON)")
        
        print(f"\n📂 Enter file number to load (or filename): ", end="")
        user_input = input().strip()
        
        try:
            # Try as number first
            if user_input.isdigit():
                file_idx = int(user_input)
                if 0 <= file_idx < len(json_files):
                    filename = json_files[file_idx]
                else:
                    print("❌ Invalid file number")
                    return False
            else:
                # Try as filename
                filename = user_input
                if not filename.endswith('.json'):
                    filename += '.json'
                    
            return self.load_existing_mapping(filename)
            
        except ValueError:
            print("❌ Invalid input")
            return False

    def edit_group_interactive(self, group_name):
        """Interactive group editor"""
        if group_name not in self.mapping:
            print(f"❌ Group '{group_name}' not found")
            return
            
        while True:
            controls = self.mapping[group_name]
            print(f"\n✏️ Editing group: '{group_name}' ({len(controls)} total events)")
            
            # Group controls for display
            button_groups = {}
            knob_controls = []
            
            for i, control in enumerate(controls):
                if control['type'] == 'button':
                    if control['id'] not in button_groups:
                        button_groups[control['id']] = {'on': None, 'off': None, 'on_idx': None, 'off_idx': None}
                    if control['midi_type'] == 'note_on':
                        button_groups[control['id']]['on'] = control
                        button_groups[control['id']]['on_idx'] = i
                    else:
                        button_groups[control['id']]['off'] = control
                        button_groups[control['id']]['off_idx'] = i
                else:
                    knob_controls.append((i, control))
            
            # Display controls with indices
            display_index = 0
            index_map = {}  # Maps display index to actual control info
            
            # Display button groups
            for button_id in sorted(button_groups.keys()):
                group = button_groups[button_id]
                on_control = group['on']
                off_control = group['off']
                
                # Get the base name
                if on_control and 'custom_name' in on_control:
                    base_name = on_control['custom_name'].replace('_on', '')
                elif off_control and 'custom_name' in off_control:
                    base_name = off_control['custom_name'].replace('_off', '')
                else:
                    base_name = f"Pad {button_id}"
                
                print(f"  {display_index}: 🔘 {base_name} (ID: {button_id}) [BUTTON PAIR]")
                index_map[display_index] = ('button_pair', button_id, group)
                display_index += 1
                
                if on_control:
                    on_name = on_control.get('custom_name', on_control['name'])
                    print(f"    {display_index}: ├─ ON:  {on_name}")
                    index_map[display_index] = ('button_individual', 'on', group['on_idx'])
                    display_index += 1
                    
                if off_control:
                    off_name = off_control.get('custom_name', off_control['name'])
                    print(f"    {display_index}: └─ OFF: {off_name}")
                    index_map[display_index] = ('button_individual', 'off', group['off_idx'])
                    display_index += 1
            
            # Display knob controls
            for actual_idx, control in knob_controls:
                control_type = "🎛️"
                display_name = control.get('custom_name', control['name'])
                midi_info = f"(ID: {control['id']})"
                print(f"  {display_index}: {control_type} {display_name} {midi_info}")
                index_map[display_index] = ('knob', actual_idx)
                display_index += 1
            
            print(f"\n✏️ Group edit options:")
            print(f"  rename - Rename this group")
            print(f"  add - Add new controls to this group")
            print(f"  remove <num> - Remove control/pair by number")
            print(f"  edit <num> - Edit control/pair name by number")
            print(f"  back - Return to main menu")
            
            print(f"\n✏️ Enter command: ", end="")
            cmd = input().strip().lower()
            
            if cmd == 'back':
                break
            elif cmd == 'rename':
                print(f"📝 Enter new group name: ", end="")
                new_name = input().strip()
                if new_name and new_name != group_name:
                    if new_name in self.mapping:
                        print(f"❌ Group '{new_name}' already exists")
                    else:
                        self.mapping[new_name] = self.mapping.pop(group_name)
                        print(f"✅ Renamed group to '{new_name}'")
                        group_name = new_name
            elif cmd == 'add':
                new_controls = self.wait_for_controls(group_name)
                if new_controls:
                    self.mapping[group_name].extend(new_controls)
                    print(f"✅ Added {len(new_controls)} controls to group")
            elif cmd.startswith('remove '):
                try:
                    idx = int(cmd.split()[1])
                    if idx in index_map:
                        item_type, *item_data = index_map[idx]
                        
                        if item_type == 'button_pair':
                            button_id, group_info = item_data
                            # Remove both on and off controls
                            indices_to_remove = []
                            if group_info['on_idx'] is not None:
                                indices_to_remove.append(group_info['on_idx'])
                            if group_info['off_idx'] is not None:
                                indices_to_remove.append(group_info['off_idx'])
                            
                            # Remove in reverse order to maintain indices
                            for i in sorted(indices_to_remove, reverse=True):
                                controls.pop(i)
                            print(f"✅ Removed button pair (ID: {button_id})")
                            
                        elif item_type == 'button_individual':
                            event_type, actual_idx = item_data
                            removed = controls.pop(actual_idx)
                            display_name = removed.get('custom_name', removed['name'])
                            print(f"✅ Removed control: {display_name}")
                            
                        elif item_type == 'knob':
                            actual_idx = item_data[0]
                            removed = controls.pop(actual_idx)
                            display_name = removed.get('custom_name', removed['name'])
                            print(f"✅ Removed control: {display_name}")
                    else:
                        print("❌ Invalid control number")
                except (ValueError, IndexError):
                    print("❌ Usage: remove <number>")
                    
            elif cmd.startswith('edit '):
                try:
                    idx = int(cmd.split()[1])
                    if idx in index_map:
                        item_type, *item_data = index_map[idx]
                        
                        if item_type == 'button_pair':
                            button_id, group_info = item_data
                            on_control = group_info['on']
                            off_control = group_info['off']
                            
                            # Get current base name
                            if on_control and 'custom_name' in on_control:
                                current_base = on_control['custom_name'].replace('_on', '')
                            elif off_control and 'custom_name' in off_control:
                                current_base = off_control['custom_name'].replace('_off', '')
                            else:
                                current_base = f"Pad {button_id}"
                            
                            print(f"📝 Current base name: '{current_base}'")
                            print(f"📝 Enter new base name (or ENTER to keep current): ", end="")
                            new_base = input().strip()
                            
                            if new_base:
                                if on_control:
                                    on_control['custom_name'] = f"{new_base}_on"
                                if off_control:
                                    off_control['custom_name'] = f"{new_base}_off"
                                print(f"✅ Renamed button pair to: '{new_base}_on' and '{new_base}_off'")
                                
                        elif item_type == 'button_individual':
                            event_type, actual_idx = item_data
                            control = controls[actual_idx]
                            current_name = control.get('custom_name', control['name'])
                            print(f"📝 Current name: '{current_name}'")
                            print(f"📝 Enter new name (or ENTER to keep current): ", end="")
                            new_name = input().strip()
                            if new_name:
                                control['custom_name'] = new_name
                                print(f"✅ Renamed to: '{new_name}'")
                                
                        elif item_type == 'knob':
                            actual_idx = item_data[0]
                            control = controls[actual_idx]
                            current_name = control.get('custom_name', control['name'])
                            print(f"📝 Current name: '{current_name}'")
                            print(f"📝 Enter new name (or ENTER to keep current): ", end="")
                            new_name = input().strip()
                            if new_name:
                                control['custom_name'] = new_name
                                print(f"✅ Renamed to: '{new_name}'")
                    else:
                        print("❌ Invalid control number")
                except (ValueError, IndexError):
                    print("❌ Usage: edit <number>")
            else:
                print("❌ Invalid command")

def main():
    try:
        mapper = MIDIMapper()
        mapper.run_mapping_session()
    except KeyboardInterrupt:
        print("\n\n⏹️ Mapping session interrupted")
    except Exception as e:
        print(f"\n❌ Error: {e}")
    finally:
        if 'mapper' in locals():
            mapper.cleanup()

if __name__ == "__main__":
    main()
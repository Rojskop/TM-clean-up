#!/usr/bin/env python3
"""
TMX Translation Memory Cleaner - Desktop Application with Advanced Conditions

A GUI application for cleaning TMX files with comprehensive cleaning conditions.
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import xml.etree.ElementTree as ET
import re
import threading
from collections import defaultdict
from typing import Set, Tuple, List, Dict
import os
from datetime import datetime


class TMXCleaner:
    def __init__(self, progress_callback=None, log_callback=None, cleaning_options=None):
        self.stats = {
            'original_segments': 0,
            'duplicate_source_target_case_sensitive': 0,
            'duplicate_source_target_case_insensitive': 0,
            'duplicate_source_case_sensitive': 0,
            'duplicate_source_case_insensitive': 0,
            'source_same_as_target_case_sensitive': 0,
            'source_empty': 0,
            'target_empty': 0,
            'source_empty_target_not': 0,
            'target_empty_source_not': 0,
            'both_empty': 0,
            'inline_code': 0,
            'whitespace_cleaned': 0,
            'final_segments': 0
        }
        self.progress_callback = progress_callback
        self.log_callback = log_callback
        self.cleaning_options = cleaning_options or {}
        
    def log(self, message):
        """Log message to callback if available"""
        if self.log_callback:
            self.log_callback(message)
        else:
            print(message)
    
    def update_progress(self, value):
        """Update progress if callback available"""
        if self.progress_callback:
            self.progress_callback(value)
    
    def remove_inline_tags(self, text: str) -> str:
        """Remove common inline tags from text with smart spacing"""
        if not text:
            return text
            
        original_text = text
        
        # Smart spacing: Add spaces around inline tags only when needed
        # This prevents words from being concatenated when tags are removed
        
        # Pattern to match inline tags
        inline_tag_pattern = r'<(?:g|x|bx|ex|ph|it|mrk|hi|sub|ut)[^>]*/?>'
        
        # Find all inline tag matches with their positions
        matches = list(re.finditer(inline_tag_pattern, text, flags=re.IGNORECASE))
        
        # Process matches in reverse order to maintain correct positions
        for match in reversed(matches):
            start, end = match.span()
            tag = match.group()
            
            # Check characters before and after the tag
            char_before = text[start - 1] if start > 0 else ''
            char_after = text[end] if end < len(text) else ''
            
            # Determine if we need to add spaces
            need_space_before = (start > 0 and 
                               char_before not in ' \t\n\r' and 
                               char_before.isalnum())
            
            need_space_after = (end < len(text) and 
                              char_after not in ' \t\n\r' and 
                              char_after.isalnum())
            
            # Build replacement (spaces only where needed)
            replacement = ''
            if need_space_before:
                replacement = ' ' + replacement
            if need_space_after:
                replacement = replacement + ' '
            
            # Replace the tag with appropriate spacing
            text = text[:start] + replacement + text[end:]
        
        # Also handle any remaining XML-like tags with the same smart spacing
        remaining_tag_pattern = r'<[^>]+>'
        remaining_matches = list(re.finditer(remaining_tag_pattern, text))
        
        for match in reversed(remaining_matches):
            start, end = match.span()
            
            # Check characters before and after the tag
            char_before = text[start - 1] if start > 0 else ''
            char_after = text[end] if end < len(text) else ''
            
            # Determine if we need to add spaces
            need_space_before = (start > 0 and 
                               char_before not in ' \t\n\r' and 
                               char_before.isalnum())
            
            need_space_after = (end < len(text) and 
                              char_after not in ' \t\n\r' and 
                              char_after.isalnum())
            
            # Build replacement (spaces only where needed)
            replacement = ''
            if need_space_before:
                replacement = ' ' + replacement
            if need_space_after:
                replacement = replacement + ' '
            
            # Replace the tag with appropriate spacing
            text = text[:start] + replacement + text[end:]
        
        return text
    
    def clean_whitespace(self, text: str) -> str:
        """Remove leading/trailing whitespace and normalize internal whitespace"""
        if not text:
            return text
            
        original_text = text
        text = text.strip()
        text = re.sub(r'\s+', ' ', text)
        
        if original_text != text:
            self.stats['whitespace_cleaned'] += 1
            
        return text
    
    def has_inline_code(self, text: str) -> bool:
        """Check if text contains inline code/tags"""
        if not text:
            return False
        
        # Check for various inline code patterns
        patterns = [
            r'<[^>]+>',  # XML/HTML tags
            r'&[a-zA-Z]+;',  # HTML entities
            r'{\w+}',  # Placeholder patterns like {variable}
            r'\[[^\]]+\]',  # Bracket notation
            r'%\w+%',  # Percent notation like %variable%
        ]
        
        for pattern in patterns:
            if re.search(pattern, text):
                return True
        return False
    
    def extract_text_from_tuv(self, tuv_element) -> str:
        """Extract clean text from a TUV element"""
        seg_element = tuv_element.find('seg')
        if seg_element is None:
            return ""
        
        # Get all text content
        text_parts = []
        if seg_element.text:
            text_parts.append(seg_element.text)
        
        for child in seg_element:
            if child.text:
                text_parts.append(child.text)
            if child.tail:
                text_parts.append(child.tail)
        
        raw_text = ''.join(text_parts)
        
        # Apply cleaning based on options
        if self.cleaning_options.get('remove_inline_tags', False):
            raw_text = self.remove_inline_tags(raw_text)
        
        if self.cleaning_options.get('clean_whitespace', False):
            raw_text = self.clean_whitespace(raw_text)
        else:
            # Always do basic strip to avoid issues
            raw_text = raw_text.strip() if raw_text else ""
        
        return raw_text
    
    def should_remove_segment(self, source_text: str, target_text: str) -> Tuple[bool, str]:
        """Check if segment should be removed based on cleaning conditions"""
        source_clean = source_text.strip()
        target_clean = target_text.strip()
        
        # Check various conditions
        if self.cleaning_options.get('duplicate_source_target_case_sensitive', False):
            # This will be handled in the main loop with tracking
            pass
        
        if self.cleaning_options.get('duplicate_source_target_case_insensitive', False):
            # This will be handled in the main loop with tracking
            pass
            
        if self.cleaning_options.get('duplicate_source_case_sensitive', False):
            # This will be handled in the main loop with tracking
            pass
            
        if self.cleaning_options.get('duplicate_source_case_insensitive', False):
            # This will be handled in the main loop with tracking
            pass
        
        if self.cleaning_options.get('source_same_as_target_case_sensitive', False):
            if source_clean == target_clean and source_clean:
                self.stats['source_same_as_target_case_sensitive'] += 1
                return True, "Source same as target (case sensitive)"
        
        if self.cleaning_options.get('source_empty', False):
            if not source_clean:
                self.stats['source_empty'] += 1
                return True, "Source is empty"
        
        if self.cleaning_options.get('target_empty', False):
            if not target_clean:
                self.stats['target_empty'] += 1
                return True, "Target is empty"
        
        if self.cleaning_options.get('source_empty_target_not', False):
            if not source_clean and target_clean:
                self.stats['source_empty_target_not'] += 1
                return True, "Source empty but target not"
        
        if self.cleaning_options.get('target_empty_source_not', False):
            if not target_clean and source_clean:
                self.stats['target_empty_source_not'] += 1
                return True, "Target empty but source not"
        
        if self.cleaning_options.get('both_empty', False):
            if not source_clean and not target_clean:
                self.stats['both_empty'] += 1
                return True, "Both source and target empty"
        
        if self.cleaning_options.get('inline_code', False):
            if self.has_inline_code(source_clean) or self.has_inline_code(target_clean):
                self.stats['inline_code'] += 1
                return True, "Contains inline code"
        
        return False, ""
    
    def clean_tmx_file(self, input_file: str, output_file: str) -> bool:
        """Clean a TMX file and save the result"""
        self.log(f"Loading TMX file: {os.path.basename(input_file)}")
        
        try:
            tree = ET.parse(input_file)
            root = tree.getroot()
        except ET.ParseError as e:
            self.log(f"Error parsing TMX file: {e}")
            return False
        except FileNotFoundError:
            self.log(f"File not found: {input_file}")
            return False
        
        # Find all TU elements
        tu_elements = root.findall('.//tu')
        self.stats['original_segments'] = len(tu_elements)
        
        self.log(f"Found {self.stats['original_segments']:,} translation units")
        self.update_progress(10)
        
        # Track duplicates
        seen_segments_case_sensitive = set()
        seen_segments_case_insensitive = set()
        seen_sources_case_sensitive = set()
        seen_sources_case_insensitive = set()
        
        tu_to_remove = []
        total_segments = len(tu_elements)
        
        for i, tu in enumerate(tu_elements):
            # Update progress
            if i % 100 == 0:
                progress = 10 + (i / total_segments) * 70
                self.update_progress(progress)
            
            # Find source and target TUV elements
            tuv_elements = tu.findall('tuv')
            
            if len(tuv_elements) < 2:
                tu_to_remove.append(tu)
                continue
            
            # Extract source and target texts
            source_tuv = tuv_elements[0]
            target_tuv = tuv_elements[1]
            
            source_text = self.extract_text_from_tuv(source_tuv)
            target_text = self.extract_text_from_tuv(target_tuv)
            
            # Check basic removal conditions
            should_remove, reason = self.should_remove_segment(source_text, target_text)
            if should_remove:
                tu_to_remove.append(tu)
                continue
            
            # Check duplicate conditions
            if self.cleaning_options.get('duplicate_source_target_case_sensitive', False):
                segment_pair = (source_text, target_text)
                if segment_pair in seen_segments_case_sensitive:
                    tu_to_remove.append(tu)
                    self.stats['duplicate_source_target_case_sensitive'] += 1
                    continue
                seen_segments_case_sensitive.add(segment_pair)
            
            if self.cleaning_options.get('duplicate_source_target_case_insensitive', False):
                segment_pair_lower = (source_text.lower(), target_text.lower())
                if segment_pair_lower in seen_segments_case_insensitive:
                    tu_to_remove.append(tu)
                    self.stats['duplicate_source_target_case_insensitive'] += 1
                    continue
                seen_segments_case_insensitive.add(segment_pair_lower)
            
            if self.cleaning_options.get('duplicate_source_case_sensitive', False):
                if source_text in seen_sources_case_sensitive:
                    tu_to_remove.append(tu)
                    self.stats['duplicate_source_case_sensitive'] += 1
                    continue
                seen_sources_case_sensitive.add(source_text)
            
            if self.cleaning_options.get('duplicate_source_case_insensitive', False):
                source_lower = source_text.lower()
                if source_lower in seen_sources_case_insensitive:
                    tu_to_remove.append(tu)
                    self.stats['duplicate_source_case_insensitive'] += 1
                    continue
                seen_sources_case_insensitive.add(source_lower)
            
            # Update the TUV elements with cleaned text
            if self.cleaning_options.get('remove_inline_tags', False) or self.cleaning_options.get('clean_whitespace', False):
                source_seg = source_tuv.find('seg')
                target_seg = target_tuv.find('seg')
                
                if source_seg is not None:
                    source_seg.clear()
                    source_seg.text = source_text
                
                if target_seg is not None:
                    target_seg.clear()
                    target_seg.text = target_text
        
        self.update_progress(85)
        
        # Remove invalid TU elements
        body = root.find('.//body')
        if body is not None:
            for tu in tu_to_remove:
                body.remove(tu)
        
        self.stats['final_segments'] = len(root.findall('.//tu'))
        
        # Save cleaned TMX file
        self.log(f"Saving cleaned TMX file: {os.path.basename(output_file)}")
        
        try:
            os.makedirs(os.path.dirname(output_file), exist_ok=True)
            tree.write(output_file, encoding='utf-8', xml_declaration=True)
            self.update_progress(100)
            return True
        except Exception as e:
            self.log(f"Error saving file: {e}")
            return False
    
    def get_statistics_text(self):
        """Get formatted statistics text"""
        if self.stats['original_segments'] == 0:
            return "No statistics available"
        
        total_removed = self.stats['original_segments'] - self.stats['final_segments']
        retention_rate = (self.stats['final_segments'] / self.stats['original_segments'] * 100) if self.stats['original_segments'] > 0 else 0
        
        stats_text = f"""TMX CLEANING STATISTICS
{'='*60}
Original segments:                           {self.stats['original_segments']:,}

DUPLICATES REMOVED:
  Duplicate Source and Target (case sensitive):  {self.stats['duplicate_source_target_case_sensitive']:,}
  Duplicate Source and Target (case insensitive): {self.stats['duplicate_source_target_case_insensitive']:,}
  Duplicate Source (case sensitive):             {self.stats['duplicate_source_case_sensitive']:,}
  Duplicate Source (case insensitive):           {self.stats['duplicate_source_case_insensitive']:,}

CONTENT ISSUES REMOVED:
  Source same as Target (case sensitive):       {self.stats['source_same_as_target_case_sensitive']:,}
  Source is empty:                              {self.stats['source_empty']:,}
  Target is empty:                              {self.stats['target_empty']:,}
  Source empty, Target not:                     {self.stats['source_empty_target_not']:,}
  Target empty, Source not:                     {self.stats['target_empty_source_not']:,}
  Both Source and Target empty:                 {self.stats['both_empty']:,}
  Contains inline code:                         {self.stats['inline_code']:,}

CONTENT CLEANED:
  Segments with whitespace cleaned:             {self.stats['whitespace_cleaned']:,}

FINAL RESULTS:
  Final segments:                               {self.stats['final_segments']:,}
  Total segments removed:                       {total_removed:,}
  Retention rate:                               {retention_rate:.1f}%
{'='*60}"""
        return stats_text


class TMXCleanerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("TMX Translation Memory Cleaner - Advanced")
        self.root.geometry("900x800")
        self.root.minsize(700, 600)
        
        # Variables
        self.input_file = tk.StringVar()
        self.output_file = tk.StringVar()
        self.cleaning_in_progress = False
        
        # Cleaning option variables
        self.cleaning_vars = {
            'duplicate_source_target_case_sensitive': tk.BooleanVar(value=True),
            'duplicate_source_target_case_insensitive': tk.BooleanVar(value=False),
            'duplicate_source_case_sensitive': tk.BooleanVar(value=True),
            'duplicate_source_case_insensitive': tk.BooleanVar(value=False),
            'source_same_as_target_case_sensitive': tk.BooleanVar(value=True),
            'source_empty': tk.BooleanVar(value=True),
            'target_empty': tk.BooleanVar(value=True),
            'source_empty_target_not': tk.BooleanVar(value=True),
            'target_empty_source_not': tk.BooleanVar(value=True),
            'both_empty': tk.BooleanVar(value=True),
            'inline_code': tk.BooleanVar(value=False),
            'remove_inline_tags': tk.BooleanVar(value=True),
            'clean_whitespace': tk.BooleanVar(value=True)
        }
        
        self.setup_ui()
        
    def setup_ui(self):
        """Set up the user interface"""
        # Create notebook for tabs
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Main tab
        main_tab = ttk.Frame(notebook)
        notebook.add(main_tab, text="Main")
        
        # Options tab
        options_tab = ttk.Frame(notebook)
        notebook.add(options_tab, text="Cleaning Options")
        
        self.setup_main_tab(main_tab)
        self.setup_options_tab(options_tab)
        
    def setup_main_tab(self, parent):
        """Set up main tab"""
        main_frame = ttk.Frame(parent, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Configure grid weights
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(4, weight=1)
        
        # Title
        title_label = ttk.Label(main_frame, text="TMX Translation Memory Cleaner", 
                               font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # File selection
        ttk.Label(main_frame, text="Input TMX File:").grid(row=1, column=0, sticky=tk.W, pady=5)
        ttk.Entry(main_frame, textvariable=self.input_file, width=60).grid(row=1, column=1, sticky=(tk.W, tk.E), padx=5)
        ttk.Button(main_frame, text="Browse", command=self.browse_input_file).grid(row=1, column=2, padx=(5, 0))
        
        ttk.Label(main_frame, text="Output TMX File:").grid(row=2, column=0, sticky=tk.W, pady=5)
        ttk.Entry(main_frame, textvariable=self.output_file, width=60).grid(row=2, column=1, sticky=(tk.W, tk.E), padx=5)
        ttk.Button(main_frame, text="Browse", command=self.browse_output_file).grid(row=2, column=2, padx=(5, 0))
        
        # Progress and button
        progress_frame = ttk.Frame(main_frame)
        progress_frame.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=20)
        progress_frame.columnconfigure(0, weight=1)
        
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(progress_frame, variable=self.progress_var, maximum=100)
        self.progress_bar.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 10))
        
        self.clean_button = ttk.Button(progress_frame, text="Clean TMX File", command=self.start_cleaning)
        self.clean_button.grid(row=0, column=1)
        
        # Log area
        log_frame = ttk.LabelFrame(main_frame, text="Processing Log & Results", padding="5")
        log_frame.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(10, 0))
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=15, wrap=tk.WORD)
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Status bar
        self.status_var = tk.StringVar(value="Ready")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, relief=tk.SUNKEN)
        status_bar.grid(row=5, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(10, 0))
    
    def setup_options_tab(self, parent):
        """Set up cleaning options tab"""
        options_frame = ttk.Frame(parent, padding="10")
        options_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create canvas and scrollbar for scrollable options
        canvas = tk.Canvas(options_frame)
        scrollbar = ttk.Scrollbar(options_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Predefined conditions frame
        conditions_frame = ttk.LabelFrame(scrollable_frame, text="Predefined Conditions", padding="10")
        conditions_frame.pack(fill=tk.X, pady=(0, 10))
        
        row = 0
        
        # Duplicate conditions
        ttk.Label(conditions_frame, text="DUPLICATE CONDITIONS:", font=("Arial", 10, "bold")).grid(row=row, column=0, columnspan=2, sticky=tk.W, pady=(0, 5))
        row += 1
        
        ttk.Checkbutton(conditions_frame, text="Duplicate Source and Target (case sensitive)", 
                       variable=self.cleaning_vars['duplicate_source_target_case_sensitive']).grid(row=row, column=0, sticky=tk.W, pady=2)
        row += 1
        
        ttk.Checkbutton(conditions_frame, text="Duplicate Source and Target (case not sensitive)", 
                       variable=self.cleaning_vars['duplicate_source_target_case_insensitive']).grid(row=row, column=0, sticky=tk.W, pady=2)
        row += 1
        
        ttk.Checkbutton(conditions_frame, text="Duplicate Source (case sensitive)", 
                       variable=self.cleaning_vars['duplicate_source_case_sensitive']).grid(row=row, column=0, sticky=tk.W, pady=2)
        row += 1
        
        ttk.Checkbutton(conditions_frame, text="Duplicate Source (case not sensitive)", 
                       variable=self.cleaning_vars['duplicate_source_case_insensitive']).grid(row=row, column=0, sticky=tk.W, pady=2)
        row += 1
        
        # Empty/content conditions
        ttk.Label(conditions_frame, text="", font=("Arial", 8)).grid(row=row, column=0)
        row += 1
        ttk.Label(conditions_frame, text="CONTENT CONDITIONS:", font=("Arial", 10, "bold")).grid(row=row, column=0, columnspan=2, sticky=tk.W, pady=(0, 5))
        row += 1
        
        ttk.Checkbutton(conditions_frame, text="Source is the same as Target (case sensitive)", 
                       variable=self.cleaning_vars['source_same_as_target_case_sensitive']).grid(row=row, column=0, sticky=tk.W, pady=2)
        row += 1
        
        ttk.Checkbutton(conditions_frame, text="Source is empty", 
                       variable=self.cleaning_vars['source_empty']).grid(row=row, column=0, sticky=tk.W, pady=2)
        row += 1
        
        ttk.Checkbutton(conditions_frame, text="Target is empty", 
                       variable=self.cleaning_vars['target_empty']).grid(row=row, column=0, sticky=tk.W, pady=2)
        row += 1
        
        ttk.Checkbutton(conditions_frame, text="Source is empty, but not Target", 
                       variable=self.cleaning_vars['source_empty_target_not']).grid(row=row, column=0, sticky=tk.W, pady=2)
        row += 1
        
        ttk.Checkbutton(conditions_frame, text="Target is empty, but not Source", 
                       variable=self.cleaning_vars['target_empty_source_not']).grid(row=row, column=0, sticky=tk.W, pady=2)
        row += 1
        
        ttk.Checkbutton(conditions_frame, text="Source and Target are both empty", 
                       variable=self.cleaning_vars['both_empty']).grid(row=row, column=0, sticky=tk.W, pady=2)
        row += 1
        
        ttk.Checkbutton(conditions_frame, text="Source or Target has inline code", 
                       variable=self.cleaning_vars['inline_code']).grid(row=row, column=0, sticky=tk.W, pady=2)
        row += 1
        
        # Cleaning operations
        ttk.Label(conditions_frame, text="", font=("Arial", 8)).grid(row=row, column=0)
        row += 1
        ttk.Label(conditions_frame, text="CLEANING OPERATIONS:", font=("Arial", 10, "bold")).grid(row=row, column=0, columnspan=2, sticky=tk.W, pady=(0, 5))
        row += 1
        
        ttk.Checkbutton(conditions_frame, text="Remove inline tags from segments", 
                       variable=self.cleaning_vars['remove_inline_tags']).grid(row=row, column=0, sticky=tk.W, pady=2)
        row += 1
        
        ttk.Checkbutton(conditions_frame, text="Clean whitespace (trim and normalize)", 
                       variable=self.cleaning_vars['clean_whitespace']).grid(row=row, column=0, sticky=tk.W, pady=2)
        
        # Preset buttons
        preset_frame = ttk.LabelFrame(scrollable_frame, text="Quick Presets", padding="10")
        preset_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Button(preset_frame, text="Select All", command=self.select_all_options).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(preset_frame, text="Clear All", command=self.clear_all_options).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(preset_frame, text="Default Clean", command=self.default_clean_preset).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(preset_frame, text="Conservative", command=self.conservative_preset).pack(side=tk.LEFT)
        
        # Pack canvas and scrollbar
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Bind mousewheel to canvas
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        canvas.bind_all("<MouseWheel>", _on_mousewheel)
    
    def select_all_options(self):
        """Select all cleaning options"""
        for var in self.cleaning_vars.values():
            var.set(True)
    
    def clear_all_options(self):
        """Clear all cleaning options"""
        for var in self.cleaning_vars.values():
            var.set(False)
    
    def default_clean_preset(self):
        """Set default cleaning preset"""
        presets = {
            'duplicate_source_target_case_sensitive': True,
            'duplicate_source_case_sensitive': True,
            'source_same_as_target_case_sensitive': True,
            'source_empty': True,
            'target_empty': True,
            'source_empty_target_not': True,
            'target_empty_source_not': True,
            'both_empty': True,
            'remove_inline_tags': True,
            'clean_whitespace': True,
        }
        
        # Clear all first
        self.clear_all_options()
        
        # Set preset values
        for key, value in presets.items():
            if key in self.cleaning_vars:
                self.cleaning_vars[key].set(value)
    
    def conservative_preset(self):
        """Set conservative cleaning preset"""
        presets = {
            'duplicate_source_target_case_sensitive': True,
            'both_empty': True,
            'clean_whitespace': True,
        }
        
        # Clear all first
        self.clear_all_options()
        
        # Set preset values
        for key, value in presets.items():
            if key in self.cleaning_vars:
                self.cleaning_vars[key].set(value)
    
    def browse_input_file(self):
        """Browse for input TMX file"""
        filename = filedialog.askopenfilename(
            title="Select Input TMX File",
            filetypes=[("TMX files", "*.tmx"), ("All files", "*.*")]
        )
        if filename:
            self.input_file.set(filename)
            if not self.output_file.get():
                base, ext = os.path.splitext(filename)
                suggested_output = f"{base}_cleaned{ext}"
                self.output_file.set(suggested_output)
    
    def browse_output_file(self):
        """Browse for output TMX file"""
        filename = filedialog.asksaveasfilename(
            title="Save Cleaned TMX File As",
            defaultextension=".tmx",
            filetypes=[("TMX files", "*.tmx"), ("All files", "*.*")]
        )
        if filename:
            self.output_file.set(filename)
    
    def log_message(self, message):
        """Add message to log text widget"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        formatted_message = f"[{timestamp}] {message}\n"
        self.root.after(0, lambda: self._update_log(formatted_message))
    
    def _update_log(self, message):
        """Update log in main thread"""
        self.log_text.insert(tk.END, message)
        self.log_text.see(tk.END)
        self.root.update_idletasks()
    
    def update_progress(self, value):
        """Update progress bar"""
        self.root.after(0, lambda: self.progress_var.set(value))
    
    def update_status(self, status):
        """Update status bar"""
        self.root.after(0, lambda: self.status_var.set(status))
    
    def start_cleaning(self):
        """Start the cleaning process in a separate thread"""
        if self.cleaning_in_progress:
            return
        
        input_path = self.input_file.get().strip()
        output_path = self.output_file.get().strip()
        
        # Validate inputs
        if not input_path:
            messagebox.showerror("Error", "Please select an input TMX file")
            return
        
        if not output_path:
            messagebox.showerror("Error", "Please specify an output file path")
            return
        
        if not os.path.exists(input_path):
            messagebox.showerror("Error", f"Input file does not exist:\n{input_path}")
            return
        
        if input_path == output_path:
            messagebox.showerror("Error", "Input and output files cannot be the same")
            return
        
        # Check if any cleaning options are selected
        selected_options = {key: var.get() for key, var in self.cleaning_vars.items()}
        if not any(selected_options.values()):
            result = messagebox.askyesno("No Options Selected", 
                                       "No cleaning options are selected. The output file will be identical to the input file.\n\nDo you want to continue anyway?")
            if not result:
                return
        
        # Clear log and reset progress
        self.log_text.delete(1.0, tk.END)
        self.progress_var.set(0)
        
        # Log selected options
        self.log_message("Selected cleaning options:")
        for key, value in selected_options.items():
            if value:
                option_name = key.replace('_', ' ').title()
                self.log_message(f"  ✓ {option_name}")
        
        # Disable clean button
        self.cleaning_in_progress = True
        self.clean_button.config(state='disabled', text='Cleaning...')
        self.update_status("Cleaning in progress...")
        
        # Start cleaning in separate thread
        thread = threading.Thread(target=self.clean_tmx_thread, args=(input_path, output_path, selected_options))
        thread.daemon = True
        thread.start()
    
    def clean_tmx_thread(self, input_path, output_path, cleaning_options):
        """Clean TMX file in separate thread"""
        try:
            cleaner = TMXCleaner(
                progress_callback=self.update_progress,
                log_callback=self.log_message,
                cleaning_options=cleaning_options
            )
            
            success = cleaner.clean_tmx_file(input_path, output_path)
            
            if success:
                # Show statistics
                stats_text = cleaner.get_statistics_text()
                self.log_message("\n" + stats_text)
                
                self.root.after(0, lambda: self.cleaning_completed(True, "TMX cleaning completed successfully!"))
            else:
                self.root.after(0, lambda: self.cleaning_completed(False, "TMX cleaning failed"))
                
        except Exception as e:
            error_msg = f"Error during cleaning: {str(e)}"
            self.log_message(error_msg)
            self.root.after(0, lambda: self.cleaning_completed(False, error_msg))
    
    def cleaning_completed(self, success, message):
        """Handle cleaning completion"""
        self.cleaning_in_progress = False
        self.clean_button.config(state='normal', text='Clean TMX File')
        
        if success:
            self.update_status("Cleaning completed successfully")
            messagebox.showinfo("Success", message)
        else:
            self.update_status("Cleaning failed")
            messagebox.showerror("Error", message)


def main():
    """Main function to run the desktop application"""
    root = tk.Tk()
    
    # Set application icon (if available)
    try:
        # You can add an icon file here
        # root.iconbitmap('tmx_cleaner.ico')
        pass
    except:
        pass
    
    app = TMXCleanerGUI(root)
    
    # Center window on screen
    root.update_idletasks()
    width = root.winfo_width()
    height = root.winfo_height()
    x = (root.winfo_screenwidth() // 2) - (width // 2)
    y = (root.winfo_screenheight() // 2) - (height // 2)
    root.geometry(f"{width}x{height}+{x}+{y}")
    
    root.mainloop()


if __name__ == '__main__':
    main()

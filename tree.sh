#!/bin/bash

# Define the starting directory (current directory by default)
START_DIR="${1:-.}"

# Function to display file content with a header
display_file_content() {
  local file="$1"
  
  # Get relative path from the starting directory
  local rel_path=$(realpath --relative-to="$START_DIR" "$file")
  
  # Print file header
  echo -e "\n=== File: $rel_path ==="
  echo -e "======================================================================"
  
  # Print file content
  cat "$file"
  
  # Print footer separator
  echo -e "\n======================================================================"
}

# Find all files recursively, excluding __pycache__ directories and common binary extensions
find "$START_DIR" -type f \
  -not -path "*/\.*" \
  -not -path "*/__pycache__/*" \
  -not -name "*.pyc" \
  -not -name "*.so" \
  -not -name "*.o" \
  -not -name "*.a" \
  -not -name "*.class" \
  -not -name "*.jar" \
  -not -name "*.war" \
  -not -name "*.ear" \
  -not -name "*.zip" \
  -not -name "*.tar" \
  -not -name "*.gz" \
  -not -name "*.bz2" \
  -not -name "*.xz" \
  -not -name "*.rar" \
  -not -name "*.7z" \
  -not -name "*.bin" \
  -not -name "*.exe" \
  -not -name "*.dll" \
  -not -name "*.dylib" \
  -not -name "*.iso" \
  -not -name "*.img" \
  -not -name "*.pdf" \
  -not -name "*.png" \
  -not -name "*.jpg" \
  -not -name "*.jpeg" \
  -not -name "*.gif" \
  -not -name "*.svg" \
  -not -name "*.mp3" \
  -not -name "*.mp4" \
  -not -name "*.wav" \
  -not -name "*.avi" \
  -not -name "*.html" \
  | sort | while read file; do
    display_file_content "$file"
done
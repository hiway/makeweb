#!/bin/bash

# Create icons directory if it doesn't exist
mkdir -p static/icons

# Base URL for Material Symbols rounded icons
BASE_URL="https://raw.githubusercontent.com/marella/material-symbols/refs/heads/main/svg/400/rounded"
LICENSE_URL="https://raw.githubusercontent.com/marella/material-symbols/refs/heads/main/svg/400/LICENSE"

# List of icons we need
icons=(
    "search"           # For search input
    "menu"             # For mobile menu toggle
    "settings"         # For preferences button
    "night_sight_auto" # For auto night mode
    "dark_mode"        # For theme toggle (initial state)
    "light_mode"       # For theme toggle (dark mode state)
    "notifications"    # For notifications button
)

# Define icon renaming map
declare -A rename_map=(
    ["night_sight_auto"]="auto_mode"
)

# Function to get final icon name
get_final_name() {
    local icon=$1
    echo "${rename_map[$icon]:-$icon}"
}

# Download each icon
for icon in "${icons[@]}"; do
    final_name=$(get_final_name "$icon")

    if [ -f "static/icons/${final_name}.svg" ]; then
        echo "Icon ${final_name}.svg already exists, skipping"
        continue
    fi

    if curl -s "$BASE_URL/${icon}.svg" -o "static/icons/${final_name}.svg"; then
        echo "Downloaded ${icon}.svg as ${final_name}.svg"
    else
        echo "Failed to download ${icon}.svg"
        rm -f "static/icons/${final_name}.svg" # Clean up partial download
    fi
done

# Download the license file
curl -s "$LICENSE_URL" -o "static/icons/LICENSE"

echo "Done."

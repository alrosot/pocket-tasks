# Proposal: Render Kid Icons on Home Screen

## Why

Currently, the home screen displays child names but lacks visual representations. Adding child icons improves user experience by providing quick visual identification of each child's dashboard section.

## What Changes

This proposal implements the following:

1. **Icon Loading:** Add a YAML configuration file to specify which icon file corresponds to each child
2. **Icon Display:** Update the home screen rendering to load and display icons in each child's section
3. **Error Handling:** Add graceful fallbacks when icons are missing or fail to load

The icons are located in the `/assets/images` directory and are loaded and displayed within each child's respective section on the home screen.

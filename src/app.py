"""
Pocket Tasks - A task management application for e-paper displays.
"""

import os
import sys
import yaml
from PIL import Image, ImageDraw
from luma.core.interface.serial import noop
from luma.core.render import canvas


def _patch_pygame_image_load():
    """Patch pygame.image.load to handle PNG files properly."""
    try:
        import pygame
        original_load = pygame.image.load

        def patched_load(filename):
            """Load image with fallback for PNG files."""
            try:
                return original_load(filename)
            except Exception as e:
                # If loading fails and it's a PNG, try opening with PIL
                if str(filename).endswith('.png'):
                    pil_image = Image.open(filename)
                    # Convert PIL image to pygame surface
                    mode = pil_image.mode
                    size = pil_image.size
                    data = pil_image.tobytes()
                    return pygame.image.fromstring(data, size, mode)
                raise e

        pygame.image.load = patched_load
    except Exception:
        pass


class EmulatorDeviceWrapper:
    """Wrapper around luma.emulator.device to fix display method compatibility."""

    def __init__(self, device):
        """Initialize wrapper with emulator device."""
        self._device = device
        self._last_image = None

    def display(self, image):
        """Display image (implements display method for canvas compatibility)."""
        self._last_image = image
        self._device.data(image.tobytes())
        self._device.show()

    def __getattr__(self, name):
        """Delegate all other attributes to the wrapped device."""
        return getattr(self._device, name)


def load_kids_config(config_path=None):
    """Load kids configuration from YAML file.

    Args:
        config_path: Path to the kids YAML configuration file. If None, uses default relative to project root.

    Returns:
        List of dictionaries containing kid name and icon path
    """
    if config_path is None:
        # Get the project root directory (parent of the src directory)
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        config_path = os.path.join(project_root, "config", "kids.yaml")

    try:
        with open(config_path, 'r') as file:
            config = yaml.safe_load(file)
            kids = config.get('kids', [])
            # Transform 'icon' key to 'icon_path' for consistency with existing code
            # Also resolve icon paths relative to project root
            project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            return [
                {
                    "name": kid["name"],
                    "icon_path": os.path.join(project_root, kid["icon"])
                }
                for kid in kids
            ]
    except FileNotFoundError:
        print(f"Warning: Configuration file not found at {config_path}, using defaults")
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        return [
            {"name": "Child 1", "icon_path": os.path.join(project_root, "assets/images/child1.png")},
            {"name": "Child 2", "icon_path": os.path.join(project_root, "assets/images/child2.png")},
        ]
    except Exception as e:
        print(f"Warning: Error loading configuration: {e}, using defaults")
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        return [
            {"name": "Child 1", "icon_path": os.path.join(project_root, "assets/images/child1.png")},
            {"name": "Child 2", "icon_path": os.path.join(project_root, "assets/images/child2.png")},
        ]


def get_device(width=240, height=320):
    """Initialize the appropriate device for rendering.

    Args:
        width: Device width in pixels
        height: Device height in pixels

    Returns:
        Device instance (emulator, hardware, or dummy)
    """
    # Check if we should use the emulator
    if os.environ.get("LUMA_EMULATOR") == "1":
        try:
            # Patch pygame before importing emulator
            _patch_pygame_image_load()

            # Try to import and initialize the emulator
            from luma.emulator.device import emulator
            device = emulator(width=width, height=height, rotate=0, mode="1",
                            transform="identity", scale=1)
            # Wrap the emulator device to fix display method compatibility
            return EmulatorDeviceWrapper(device)
        except Exception as e:
            # Fallback to dummy if emulator fails
            print(f"Warning: Emulator initialization failed ({e}), using dummy device",
                  file=sys.stderr)
            from luma.core.device import dummy
            return dummy(width=width, height=height)
    else:
        # Try to initialize actual hardware device (for RaspberryPi)
        try:
            # Uncomment and configure based on your e-paper display model:
            # from waveshare_epd import epd2in13_V4  # For 2.13" e-paper
            # device = epd2in13_V4.EPD()
            # device.init()
            # device.clear()
            # return device
            raise ImportError("Hardware device not configured. See comments above.")
        except ImportError:
            # Fallback to dummy device for development
            from luma.core.device import dummy
            return dummy(width=width, height=height)


class HomeScreen:
    """Home screen displaying two children's dashboards."""

    def __init__(self, device):
        """Initialize the home screen with a device."""
        self.device = device
        self.children = load_kids_config()
        self.selected_child = None

    def render(self):
        """Render the home screen with two child dashboard sections."""
        with canvas(self.device) as draw:
            width = self.device.width
            height = self.device.height
            mid_x = width // 2

            # Fill background with white (e-paper displays need white background)
            draw.rectangle([0, 0, width - 1, height - 1], fill="white")

            # Draw vertical divider
            draw.line([(mid_x, 0), (mid_x, height)], fill="black", width=2)

            # Left child dashboard (Child 1)
            self._draw_child_section(
                draw, 0, 0, mid_x, height, self.children[0], 0
            )

            # Right child dashboard (Child 2)
            self._draw_child_section(
                draw, mid_x, 0, width, height, self.children[1], 1
            )

    def _draw_child_section(self, draw, x1, y1, x2, y2, child_data, index):
        """Draw a child's dashboard section.

        Args:
            draw: PIL ImageDraw object
            x1: Left x coordinate
            y1: Top y coordinate
            x2: Right x coordinate
            y2: Bottom y coordinate
            child_data: Dictionary containing child's name and icon_path
            index: Child index (0 or 1)
        """
        # Draw border around section
        border_width = 2
        draw.rectangle([x1, y1, x2 - 1, y2 - 1], outline="black", width=border_width)

        # Load and draw child icon
        icon_path = child_data["icon_path"]
        try:
            icon = Image.open(icon_path).convert("1")  # Convert to 1-bit for e-paper
            icon = icon.resize((60, 60))  # Resize icon
            icon_x = x1 + (x2 - x1 - icon.width) // 2
            icon_y = y1 + 20
            draw.bitmap((icon_x, icon_y), icon, fill="black")
        except FileNotFoundError:
            print(f"Warning: Icon not found for {child_data['name']} at {icon_path}", file=sys.stderr)
        except Exception as e:
            print(f"Warning: Failed to load icon for {child_data['name']} at {icon_path}: {e}", file=sys.stderr)

        # Draw child name below icon
        text_y = y1 + 20 + 60 + 10  # Below icon, with some padding
        text_x = x1 + (x2 - x1) // 2
        draw.text(
            (text_x, text_y),
            child_data["name"],
            fill="black",
            anchor="mm",
        )

    def handle_touch(self, x, y):
        """Handle touch events on the home screen.

        Args:
            x: X coordinate of touch
            y: Y coordinate of touch

        Returns:
            int: Index of child (0 or 1) if touched, None otherwise
        """
        mid_x = self.device.width // 2

        if x < mid_x:
            self.selected_child = 0
            return 0
        else:
            self.selected_child = 1
            return 1


def main():
    """Main entry point for the application."""
    # Initialize device in landscape mode
    device = get_device(width=320, height=240)

    # Create home screen
    home_screen = HomeScreen(device)

    # Render initial screen
    home_screen.render()

    print("Home screen rendered successfully")

    # Keep emulator window open for interaction
    if os.environ.get("LUMA_EMULATOR") == "1":
        try:
            import pygame
            # Check if we have a wrapper device
            if hasattr(device, '_device'):
                # We're using the wrapper, get the actual emulator
                emulator_device = device._device
                if hasattr(emulator_device, '_pygame'):
                    pygame_module = emulator_device._pygame

                    # Ensure display is initialized by showing it
                    emulator_device.show()

                    # Now initialize pygame and create display
                    pygame_module.init()
                    display = pygame_module.display.get_surface()

                    if display is None:
                        # Create display manually if not created
                        display = pygame_module.display.set_mode(
                            (device.width, device.height)
                        )
                        pygame_module.display.set_caption("Pocket Tasks - Home Screen")

                    # Draw the home screen image to the pygame surface
                    if hasattr(device, '_last_image') and device._last_image:
                        # Convert PIL image to pygame surface and draw it
                        pil_image = device._last_image
                        # Convert mode "1" (1-bit) to "RGB" for pygame compatibility
                        if pil_image.mode == "1":
                            pil_image = pil_image.convert("RGB")
                        # Create a pygame surface from the PIL image
                        mode = pil_image.mode
                        size = pil_image.size
                        data = pil_image.tobytes()
                        temp_surface = pygame_module.image.fromstring(data, size, mode)
                        display.blit(temp_surface, (0, 0))

                    pygame_module.display.flip()

                    clock = pygame_module.time.Clock()
                    running = True

                    print("Emulator window is running. Click on the screen to select a child.")
                    print("Close the window to exit.")

                    while running:
                        for event in pygame_module.event.get():
                            if event.type == pygame_module.QUIT:
                                running = False
                            elif event.type == pygame_module.MOUSEBUTTONDOWN:
                                # Handle mouse clicks for touch emulation
                                x, y = pygame_module.mouse.get_pos()
                                # Scale coordinates if needed
                                child_index = home_screen.handle_touch(x, y)
                                if child_index is not None:
                                    child_name = home_screen.children[child_index]['name']
                                    print(f"Selected {child_name}")
                                    # Re-render to show selection
                                    home_screen.render()
                                    # Update the display with the new image
                                    if hasattr(device, '_last_image') and device._last_image:
                                        pil_image = device._last_image
                                        # Convert mode "1" (1-bit) to "RGB" for pygame compatibility
                                        if pil_image.mode == "1":
                                            pil_image = pil_image.convert("RGB")
                                        mode = pil_image.mode
                                        size = pil_image.size
                                        data = pil_image.tobytes()
                                        temp_surface = pygame_module.image.fromstring(data, size, mode)
                                        display.blit(temp_surface, (0, 0))
                                        pygame_module.display.flip()

                        clock.tick(30)  # 30 FPS
        except Exception as e:
            # If emulator display fails, just exit gracefully
            print(f"Emulator display error: {e}", file=sys.stderr)


if __name__ == "__main__":
    main()

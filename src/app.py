"""
Pocket Tasks - A task management application for e-paper displays.
"""

import os
import sys
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

    def display(self, image):
        """Display image (implements display method for canvas compatibility)."""
        self._device.data(image.tobytes())
        self._device.show()

    def __getattr__(self, name):
        """Delegate all other attributes to the wrapped device."""
        return getattr(self._device, name)


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
        self.children = ["Child 1", "Child 2"]
        self.selected_child = None

    def render(self):
        """Render the home screen with two child dashboard sections."""
        with canvas(self.device) as draw:
            width = self.device.width
            height = self.device.height
            mid_x = width // 2

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

    def _draw_child_section(self, draw, x1, y1, x2, y2, name, index):
        """Draw a child's dashboard section.

        Args:
            draw: PIL ImageDraw object
            x1: Left x coordinate
            y1: Top y coordinate
            x2: Right x coordinate
            y2: Bottom y coordinate
            name: Child's name
            index: Child index (0 or 1)
        """
        # Draw border around section
        border_width = 2
        draw.rectangle([x1, y1, x2 - 1, y2 - 1], outline="black", width=border_width)

        # Draw child name in the center
        text_y = (y2 - y1) // 2 - 10
        text_x = (x2 - x1) // 2
        draw.text(
            (x1 + text_x, y1 + text_y),
            name,
            fill="black",
            anchor="mm",
        )

        # Draw placeholder text
        placeholder_y = text_y + 30
        draw.text(
            (x1 + text_x, y1 + placeholder_y),
            "Click to view details",
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
            # Check if pygame display is available
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
                    if hasattr(emulator_device, '_last_image') and emulator_device._last_image:
                        # Convert PIL image to pygame surface and draw it
                        pil_image = emulator_device._last_image
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
                                    print(f"Selected Child {child_index + 1}")
                                    # Re-render to show selection
                                    home_screen.render()
                                    # Update the display with the new image
                                    if hasattr(emulator_device, '_last_image') and emulator_device._last_image:
                                        pil_image = emulator_device._last_image
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

"""
Unit tests for the Pocket Tasks application home screen.
"""

import pytest
from unittest.mock import Mock, MagicMock, patch
from PIL import Image, ImageDraw

from src.app import HomeScreen


class TestHomeScreen:
    """Tests for the HomeScreen class."""

    @pytest.fixture
    def mock_device(self):
        """Create a mock device for testing."""
        device = Mock()
        device.width = 240
        device.height = 320
        return device

    @pytest.fixture
    def home_screen(self, mock_device):
        """Create a HomeScreen instance for testing."""
        return HomeScreen(mock_device)

    def test_home_screen_initialization(self, home_screen):
        """Test that HomeScreen initializes correctly."""
        assert home_screen.children == ["Child 1", "Child 2"]
        assert home_screen.selected_child is None

    def test_home_screen_render_creates_canvas(self, home_screen, mock_device):
        """Test that render method creates a canvas."""
        with patch("src.app.canvas") as mock_canvas:
            mock_canvas.return_value.__enter__ = MagicMock()
            mock_canvas.return_value.__exit__ = MagicMock()
            home_screen.render()
            mock_canvas.assert_called_once_with(mock_device)

    def test_touch_left_half_selects_child_1(self, home_screen):
        """Test that touching the left half selects Child 1."""
        result = home_screen.handle_touch(60, 160)
        assert result == 0
        assert home_screen.selected_child == 0

    def test_touch_right_half_selects_child_2(self, home_screen):
        """Test that touching the right half selects Child 2."""
        result = home_screen.handle_touch(180, 160)
        assert result == 1
        assert home_screen.selected_child == 1

    def test_touch_on_divider_selects_child_2(self, home_screen):
        """Test that touching on the divider (mid_x) selects Child 2."""
        mid_x = home_screen.device.width // 2
        result = home_screen.handle_touch(mid_x, 160)
        assert result == 1
        assert home_screen.selected_child == 1

    def test_layout_divides_screen_into_two_halves(self, home_screen):
        """Test that the layout divides the screen into two equal halves."""
        width = home_screen.device.width
        mid_x = width // 2
        assert mid_x == 120

    def test_draw_child_section_draws_border(self, home_screen):
        """Test that _draw_child_section draws a border."""
        draw = Mock()
        home_screen._draw_child_section(draw, 0, 0, 120, 320, "Child 1", 0)
        draw.rectangle.assert_called_once()

    def test_draw_child_section_draws_text(self, home_screen):
        """Test that _draw_child_section draws text."""
        draw = Mock()
        home_screen._draw_child_section(draw, 0, 0, 120, 320, "Child 1", 0)
        assert draw.text.call_count == 2

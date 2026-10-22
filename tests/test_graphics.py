"""Tests for graphics rendering system."""

import pytest
from ui.graphics import GraphicsRenderer, TilesheetManager, SonarDisplay


class TestGraphicsRenderer:
    """Test the graphics renderer."""
    
    def test_renderer_creation(self):
        renderer = GraphicsRenderer()
        assert renderer is not None
    
    def test_get_render_backend(self):
        renderer = GraphicsRenderer()
        backend = renderer.get_render_backend()
        assert backend in ["tilesheet", "tcod_fallback", "ascii_console"]
    
    def test_has_tilesheet(self):
        renderer = GraphicsRenderer()
        result = renderer.has_tilesheet()
        assert isinstance(result, bool)
    
    def test_get_graphics_info(self):
        renderer = GraphicsRenderer()
        info = renderer.get_graphics_info()
        
        assert 'backend' in info
        assert 'tcod_available' in info
        assert 'tileset_loaded' in info
        assert 'features' in info
        assert 'ascii_rendering' in info['features']


class TestTilesheetManager:
    """Test tileset asset management."""
    
    def test_tileset_manager_creation(self):
        manager = TilesheetManager()
        assert manager is not None
    
    def test_get_all_tiles(self):
        manager = TilesheetManager()
        tiles = manager.get_all_tiles()
        
        # Should have tiles defined (or empty dict if atlas missing)
        assert isinstance(tiles, dict)
    
    def test_get_tile_code(self):
        manager = TilesheetManager()
        
        # Test known tiles
        if manager.atlas:
            # Codes come from atlas.json; assert the lookup agrees with the atlas
            # instead of hardcoding numbers that change whenever tiles are added.
            mapping = manager.atlas['map']
            for name in ('sonar_ping', 'sonar_active', 'sonar_passive'):
                assert name in mapping
                assert manager.get_tile_code(name) == mapping[name]
            assert manager.get_tile_code('no_such_tile') is None
    
    def test_list_tiles_by_prefix(self):
        manager = TilesheetManager()
        
        if manager.atlas:
            ui_tiles = manager.list_tiles_by_prefix('ui_')
            assert len(ui_tiles) > 0
            assert all(t.startswith('ui_') for t in ui_tiles)
    
    def test_get_tile_categories(self):
        manager = TilesheetManager()
        
        if manager.atlas:
            categories = manager.get_tile_categories()
            assert isinstance(categories, dict)
            # Should have various categories
            assert len(categories) > 0


class TestSonarDisplay:
    """Test sonar display rendering."""
    
    def test_sonar_display_creation(self):
        display = SonarDisplay()
        assert display is not None
    
    def test_render_contact_ascii(self):
        display = SonarDisplay()
        
        contact = {'type': 'submarine', 'bearing': 0, 'range': 5000}
        char = display.render_contact(contact, use_tiles=False)
        assert isinstance(char, str)
        assert len(char) >= 1
    
    def test_render_contact_types(self):
        display = SonarDisplay()
        
        contact_types = [
            'submarine', 'ship', 'destroyer', 'convoy', 'contact'
        ]
        
        for ctype in contact_types:
            contact = {'type': ctype}
            char = display.render_contact(contact, use_tiles=False)
            assert isinstance(char, str)
    
    def test_render_sonar_screen(self):
        display = SonarDisplay()
        
        sonar_data = {
            'contacts': [
                {'type': 'submarine', 'bearing': 0, 'range': 5000},
                {'type': 'ship', 'bearing': 90, 'range': 8000},
                {'type': 'contact', 'bearing': 180, 'range': 3000},
            ]
        }
        
        screen = display.render_sonar_screen(sonar_data, width=40, height=20)
        assert isinstance(screen, str)
        assert len(screen) > 0
        # Should have the center contact marker
        assert '⊙' in screen or '.' in screen


class TestGraphicsIntegration:
    """Test graphics system integration."""
    
    def test_graphics_with_game(self):
        from engine.game import Game
        
        game = Game()
        renderer = GraphicsRenderer()
        
        # Should not raise errors
        backend = renderer.get_render_backend()
        assert backend is not None
        
        # Should have graphics info
        info = renderer.get_graphics_info()
        assert info is not None
    
    def test_tileset_availability(self):
        manager = TilesheetManager()
        info = manager.get_all_tiles()
        
        # Should have submarine-themed tiles
        if info:
            # Check for core submarine tiles
            expected_tiles = ['sonar_ping', 'sub_silhouette', 'ship_silhouette']
            actual_names = set(info.keys())
            
            # At least some expected tiles should be present
            found = sum(1 for t in expected_tiles if t in actual_names)
            assert found > 0

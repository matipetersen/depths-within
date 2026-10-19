"""
Day/Night Cycle and Time System.
Manages in-game time, sun position, moon phase, and time-based visibility.
"""

import math
from enum import Enum
from typing import Dict, Tuple


class TimeOfDay(Enum):
    """Time of day periods."""
    NIGHT = 'night'           # 00:00 - 05:59
    DAWN = 'dawn'             # 06:00 - 07:59
    MORNING = 'morning'       # 08:00 - 11:59
    NOON = 'noon'             # 12:00 - 13:59
    AFTERNOON = 'afternoon'   # 14:00 - 17:59
    DUSK = 'dusk'             # 18:00 - 19:59
    EVENING = 'evening'       # 20:00 - 23:59


class MoonPhase(Enum):
    """Moon phase."""
    NEW_MOON = 'new_moon'             # 0% illumination
    WAXING_CRESCENT = 'waxing_crescent'  # 25%
    FIRST_QUARTER = 'first_quarter'   # 50%
    WAXING_GIBBOUS = 'waxing_gibbous'   # 75%
    FULL_MOON = 'full_moon'           # 100%
    WANING_GIBBOUS = 'waning_gibbous'   # 75%
    LAST_QUARTER = 'last_quarter'     # 50%
    WANING_CRESCENT = 'waning_crescent' # 25%


class Season(Enum):
    """Season (affects day length)."""
    WINTER = 'winter'
    SPRING = 'spring'
    SUMMER = 'summer'
    AUTUMN = 'autumn'


class TimeSystem:
    """Manages game time and day/night cycle."""
    
    def __init__(self, start_hour: int = 6, start_minute: int = 0, 
                 start_day: int = 1, season: Season = Season.SUMMER):
        """Initialize time system."""
        # Current time
        self.hour = start_hour  # 0-23
        self.minute = start_minute  # 0-59
        self.day = start_day  # Day counter
        self.season = season
        
        # Tick rate (minutes per game tick)
        self.minutes_per_tick = 5  # Default: 5 minutes per tick
        
        # Sun/moon
        self.sun_position = self._calculate_sun_position()
        self.moon_phase = MoonPhase.FIRST_QUARTER  # Starting phase
        self.moon_age = 7  # Days since new moon (0-29)
        
        # Time tracking
        self.total_ticks = 0
        self.time_scale = 1.0  # Time multiplier (1.0 = normal)
    
    def tick(self):
        """Advance time by one tick."""
        self.total_ticks += 1
        
        # Advance time
        minutes_to_advance = int(self.minutes_per_tick * self.time_scale)
        self.minute += minutes_to_advance
        
        # Handle minute overflow
        while self.minute >= 60:
            self.minute -= 60
            self.hour += 1
        
        # Handle hour overflow
        if self.hour >= 24:
            self.hour -= 24
            self.day += 1
            self.moon_age = (self.moon_age + 1) % 30
            self._update_moon_phase()
        
        # Update sun position
        self.sun_position = self._calculate_sun_position()
    
    def _calculate_sun_position(self) -> float:
        """Calculate sun position (0.0 = midnight, 1.0 = noon)."""
        # Convert time to decimal hours
        decimal_hour = self.hour + (self.minute / 60.0)
        
        # Noon is at 12:00, midnight at 0:00/24:00
        # Position: 0.0 (midnight) -> 1.0 (noon) -> 0.0 (midnight)
        if decimal_hour <= 12:
            position = decimal_hour / 12.0
        else:
            position = 2.0 - (decimal_hour / 12.0)
        
        return position
    
    def _update_moon_phase(self):
        """Update moon phase based on moon age."""
        age = self.moon_age
        
        if age < 2:
            self.moon_phase = MoonPhase.NEW_MOON
        elif age < 6:
            self.moon_phase = MoonPhase.WAXING_CRESCENT
        elif age < 9:
            self.moon_phase = MoonPhase.FIRST_QUARTER
        elif age < 13:
            self.moon_phase = MoonPhase.WAXING_GIBBOUS
        elif age < 17:
            self.moon_phase = MoonPhase.FULL_MOON
        elif age < 21:
            self.moon_phase = MoonPhase.WANING_GIBBOUS
        elif age < 24:
            self.moon_phase = MoonPhase.LAST_QUARTER
        else:
            self.moon_phase = MoonPhase.WANING_CRESCENT
    
    def get_time_of_day(self) -> TimeOfDay:
        """Get current time of day period."""
        if 0 <= self.hour < 6:
            return TimeOfDay.NIGHT
        elif 6 <= self.hour < 8:
            return TimeOfDay.DAWN
        elif 8 <= self.hour < 12:
            return TimeOfDay.MORNING
        elif 12 <= self.hour < 14:
            return TimeOfDay.NOON
        elif 14 <= self.hour < 18:
            return TimeOfDay.AFTERNOON
        elif 18 <= self.hour < 20:
            return TimeOfDay.DUSK
        else:
            return TimeOfDay.EVENING
    
    def is_daylight(self) -> bool:
        """Check if it's daylight."""
        return self.get_time_of_day() in [TimeOfDay.MORNING, TimeOfDay.NOON, 
                                          TimeOfDay.AFTERNOON]
    
    def is_night(self) -> bool:
        """Check if it's night."""
        return self.get_time_of_day() in [TimeOfDay.NIGHT, TimeOfDay.EVENING]
    
    def get_moon_illumination(self) -> float:
        """Get moon illumination percentage (0.0-1.0)."""
        illumination_map = {
            MoonPhase.NEW_MOON: 0.0,
            MoonPhase.WAXING_CRESCENT: 0.25,
            MoonPhase.FIRST_QUARTER: 0.5,
            MoonPhase.WAXING_GIBBOUS: 0.75,
            MoonPhase.FULL_MOON: 1.0,
            MoonPhase.WANING_GIBBOUS: 0.75,
            MoonPhase.LAST_QUARTER: 0.5,
            MoonPhase.WANING_CRESCENT: 0.25,
        }
        return illumination_map.get(self.moon_phase, 0.5)
    
    def get_visibility_modifier(self, include_moon: bool = True) -> float:
        """
        Get visibility modifier based on time of day (0.0-1.0).
        1.0 = full daylight, 0.0 = pitch black.
        """
        time_of_day = self.get_time_of_day()
        
        # Base visibility by time
        base_visibility = {
            TimeOfDay.NIGHT: 0.05,
            TimeOfDay.DAWN: 0.5,
            TimeOfDay.MORNING: 1.0,
            TimeOfDay.NOON: 1.0,
            TimeOfDay.AFTERNOON: 1.0,
            TimeOfDay.DUSK: 0.5,
            TimeOfDay.EVENING: 0.15,
        }
        
        visibility = base_visibility.get(time_of_day, 0.5)
        
        # Moon illumination at night
        if include_moon and self.is_night():
            moon_bonus = self.get_moon_illumination() * 0.3  # Max 30% bonus
            visibility = min(1.0, visibility + moon_bonus)
        
        return visibility
    
    def get_detection_risk_modifier(self, on_surface: bool = True) -> float:
        """
        Get detection risk modifier (0.0-1.0).
        Higher = more likely to be detected.
        """
        if not on_surface:
            return 0.1  # Very low risk submerged
        
        # Surface detection varies greatly by time
        time_of_day = self.get_time_of_day()
        
        detection_risk = {
            TimeOfDay.NIGHT: 0.2,
            TimeOfDay.DAWN: 0.5,
            TimeOfDay.MORNING: 0.9,
            TimeOfDay.NOON: 1.0,
            TimeOfDay.AFTERNOON: 0.9,
            TimeOfDay.DUSK: 0.5,
            TimeOfDay.EVENING: 0.3,
        }
        
        risk = detection_risk.get(time_of_day, 0.5)
        
        # Full moon increases night detection risk
        if self.is_night():
            moon_penalty = self.get_moon_illumination() * 0.3
            risk = min(1.0, risk + moon_penalty)
        
        return risk
    
    def get_periscope_range(self, weather: str = 'clear') -> float:
        """
        Get periscope visual range in km.
        Affected by time of day and weather.
        """
        # Base range by time
        base_range = self.get_visibility_modifier() * 10.0  # 0-10km
        
        # Weather modifier
        weather_modifiers = {
            'clear': 1.0,
            'fog': 0.3,
            'rain': 0.6,
            'storm': 0.4,
            'snow': 0.5,
            'overcast': 0.8,
        }
        
        weather_mod = weather_modifiers.get(weather.lower(), 1.0)
        
        return base_range * weather_mod
    
    def get_time_string(self, format: str = '24h') -> str:
        """Get formatted time string."""
        if format == '24h':
            return f"{self.hour:02d}:{self.minute:02d}"
        else:  # 12h format
            hour_12 = self.hour % 12
            if hour_12 == 0:
                hour_12 = 12
            period = 'AM' if self.hour < 12 else 'PM'
            return f"{hour_12:02d}:{self.minute:02d} {period}"
    
    def get_date_string(self) -> str:
        """Get formatted date string."""
        return f"Day {self.day}"
    
    def get_full_datetime_string(self) -> str:
        """Get full date and time string."""
        return f"{self.get_date_string()}, {self.get_time_string()}"
    
    def get_time_info(self) -> Dict:
        """Get comprehensive time information."""
        return {
            'time': self.get_time_string(),
            'date': self.get_date_string(),
            'time_of_day': self.get_time_of_day().value,
            'is_daylight': self.is_daylight(),
            'is_night': self.is_night(),
            'sun_position': self.sun_position,
            'moon_phase': self.moon_phase.value,
            'moon_illumination': self.get_moon_illumination(),
            'visibility': self.get_visibility_modifier(),
            'detection_risk': self.get_detection_risk_modifier(),
        }
    
    def set_time(self, hour: int, minute: int = 0):
        """Set specific time."""
        self.hour = max(0, min(23, hour))
        self.minute = max(0, min(59, minute))
        self.sun_position = self._calculate_sun_position()
    
    def advance_to_time(self, target_hour: int):
        """Advance time to specific hour."""
        while self.hour != target_hour:
            self.tick()
    
    def advance_to_night(self):
        """Advance time to nightfall (20:00)."""
        self.advance_to_time(20)
    
    def advance_to_dawn(self):
        """Advance time to dawn (06:00)."""
        self.advance_to_time(6)
    
    def get_ui_display(self) -> str:
        """Get formatted display for UI."""
        time_str = self.get_time_string()
        tod = self.get_time_of_day().value.upper()
        moon = self.moon_phase.value.replace('_', ' ').title()
        
        # Time of day icon
        tod_icons = {
            TimeOfDay.NIGHT: '🌙',
            TimeOfDay.DAWN: '🌅',
            TimeOfDay.MORNING: '☀️',
            TimeOfDay.NOON: '☀️',
            TimeOfDay.AFTERNOON: '☀️',
            TimeOfDay.DUSK: '🌇',
            TimeOfDay.EVENING: '🌙',
        }
        icon = tod_icons.get(self.get_time_of_day(), '⏰')
        
        display = f"{icon} {time_str} - Day {self.day}\n"
        display += f"   {tod}\n"
        display += f"   Moon: {moon} ({self.get_moon_illumination():.0%})\n"
        display += f"   Visibility: {self.get_visibility_modifier():.0%}\n"
        
        return display
    
    def is_good_time_for_surface(self) -> Tuple[bool, str]:
        """Check if it's a good time to surface."""
        detection_risk = self.get_detection_risk_modifier(on_surface=True)
        
        if detection_risk < 0.3:
            return True, "Low detection risk (night)"
        elif detection_risk < 0.6:
            return True, "Moderate detection risk"
        else:
            return False, "High detection risk (daylight)"


class TimeAwareEntity:
    """Base class for entities affected by time."""
    
    def __init__(self, time_system: TimeSystem):
        """Initialize with time system reference."""
        self.time_system = time_system
    
    def get_current_visibility(self, weather: str = 'clear') -> float:
        """Get current visibility considering time and weather."""
        base_visibility = self.time_system.get_visibility_modifier()
        
        weather_modifiers = {
            'clear': 1.0,
            'fog': 0.3,
            'rain': 0.6,
            'storm': 0.4,
        }
        
        weather_mod = weather_modifiers.get(weather, 1.0)
        return base_visibility * weather_mod
    
    def should_use_lights(self) -> bool:
        """Check if lights should be used."""
        return self.time_system.get_visibility_modifier() < 0.3
    
    def is_good_time_for_surface(self) -> Tuple[bool, str]:
        """Check if it's a good time to surface."""
        detection_risk = self.time_system.get_detection_risk_modifier(on_surface=True)
        
        if detection_risk < 0.3:
            return True, "Low detection risk (night)"
        elif detection_risk < 0.6:
            return True, "Moderate detection risk"
        else:
            return False, "High detection risk (daylight)"

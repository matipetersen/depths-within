"""
Supply and resource rationing system for submarines.
Manages oxygen, power, food, water, and ammunition.
"""
from enum import Enum
from typing import Dict, Optional
from dataclasses import dataclass, field


class ResourceType(Enum):
    """Types of submarine resources"""
    OXYGEN = "oxygen"              # Breathable air (percentage 0-100)
    POWER = "power"                # Electrical power (percentage 0-100)
    FOOD = "food"                  # Crew provisions (units)
    WATER = "water"                # Fresh water (units)
    AMMUNITION = "ammunition"      # Torpedo ammunition (units)
    FUEL = "fuel"                  # Diesel fuel (units)
    MEDICAL = "medical"            # Medical supplies (units)
    REPAIR_MATERIALS = "repair"    # Hull and equipment materials (units)


class RationLevel(Enum):
    """Rationing strictness levels"""
    NORMAL = 1.0                   # Full consumption
    REDUCED = 0.75                 # 25% reduction
    STRICT = 0.5                   # 50% reduction
    EMERGENCY = 0.25               # 75% reduction
    CRITICAL = 0.1                 # 90% reduction


@dataclass
class Resource:
    """Individual resource tracking"""
    resource_type: ResourceType
    current: float                  # Current amount
    maximum: float                  # Maximum capacity
    consumption_rate: float         # Units consumed per turn (affected by crew size)
    
    def get_percentage(self) -> float:
        """Get current percentage (0-100)"""
        if self.maximum == 0:
            return 100.0
        return (self.current / self.maximum) * 100.0
    
    def consume(self, amount: float, efficiency: float = 1.0) -> float:
        """Consume resource. Returns actual amount consumed. Efficiency affects consumption."""
        actual_consumption = amount * efficiency
        consumed = min(actual_consumption, self.current)
        self.current = max(0.0, self.current - consumed)
        return consumed
    
    def replenish(self, amount: float) -> float:
        """Replenish resource. Returns actual amount added."""
        added = min(amount, self.maximum - self.current)
        self.current = min(self.maximum, self.current + added)
        return added
    
    def get_status(self) -> str:
        """Get human-readable status"""
        pct = self.get_percentage()
        if pct > 75:
            return "EXCELLENT"
        elif pct > 50:
            return "GOOD"
        elif pct > 25:
            return "LOW"
        elif pct > 10:
            return "CRITICAL"
        else:
            return "DEPLETED"


@dataclass
class SupplyInventory:
    """Tracks all submarine supplies"""
    oxygen: Resource = field(default_factory=lambda: Resource(ResourceType.OXYGEN, 100.0, 100.0, 0.5))
    power: Resource = field(default_factory=lambda: Resource(ResourceType.POWER, 100.0, 100.0, 0.3))
    food: Resource = field(default_factory=lambda: Resource(ResourceType.FOOD, 500, 500, 5.0))
    water: Resource = field(default_factory=lambda: Resource(ResourceType.WATER, 300, 300, 2.0))
    ammunition: Resource = field(default_factory=lambda: Resource(ResourceType.AMMUNITION, 24, 24, 0.0))
    fuel: Resource = field(default_factory=lambda: Resource(ResourceType.FUEL, 1000, 1000, 2.0))
    medical: Resource = field(default_factory=lambda: Resource(ResourceType.MEDICAL, 50, 50, 0.1))
    repair_materials: Resource = field(default_factory=lambda: Resource(ResourceType.REPAIR_MATERIALS, 100, 100, 0.0))
    
    # Tracking
    ration_level: RationLevel = RationLevel.NORMAL
    oxygen_warning_issued: bool = False
    power_warning_issued: bool = False
    food_warning_issued: bool = False
    total_food_consumed: int = 0
    total_water_consumed: int = 0
    
    def get_all_resources(self) -> Dict[str, Resource]:
        """Get all resources as dict"""
        return {
            "oxygen": self.oxygen,
            "power": self.power,
            "food": self.food,
            "water": self.water,
            "ammunition": self.ammunition,
            "fuel": self.fuel,
            "medical": self.medical,
            "repair_materials": self.repair_materials,
        }
    
    def get_resource(self, resource_type: ResourceType) -> Optional[Resource]:
        """Get specific resource"""
        resource_map = {
            ResourceType.OXYGEN: self.oxygen,
            ResourceType.POWER: self.power,
            ResourceType.FOOD: self.food,
            ResourceType.WATER: self.water,
            ResourceType.AMMUNITION: self.ammunition,
            ResourceType.FUEL: self.fuel,
            ResourceType.MEDICAL: self.medical,
            ResourceType.REPAIR_MATERIALS: self.repair_materials,
        }
        return resource_map.get(resource_type)
    
    def tick(self, crew_count: int, depth: int, in_combat: bool = False) -> Dict[str, str]:
        """Update supplies each turn. Returns warnings."""
        warnings = {}
        
        # Oxygen consumption increases with depth (pressure)
        depth_factor = 1.0 + (depth / 300.0) * 0.5  # Deeper = more consumption
        oxygen_consumption = self.oxygen.consumption_rate * crew_count * depth_factor * self.ration_level.value
        
        # Power consumption increases with sonar use and combat
        combat_multiplier = 2.0 if in_combat else 1.0
        power_consumption = self.power.consumption_rate * crew_count * combat_multiplier * self.ration_level.value
        
        # Food/water consumption
        food_consumption = self.food.consumption_rate * crew_count * self.ration_level.value
        water_consumption = self.water.consumption_rate * crew_count * self.ration_level.value
        
        # Fuel consumption (engines)
        fuel_consumption = self.fuel.consumption_rate * self.ration_level.value
        
        # Apply consumption
        self.oxygen.consume(oxygen_consumption)
        self.power.consume(power_consumption)
        food_consumed = self.food.consume(food_consumption)
        water_consumed = self.water.consume(water_consumption)
        self.fuel.consume(fuel_consumption)
        
        # Track consumption
        self.total_food_consumed += int(food_consumed)
        self.total_water_consumed += int(water_consumed)
        
        # Generate warnings
        if self.oxygen.get_percentage() < 30 and not self.oxygen_warning_issued:
            warnings['oxygen'] = f"OXYGEN CRITICAL: {self.oxygen.get_percentage():.1f}%"
            self.oxygen_warning_issued = True
        elif self.oxygen.get_percentage() >= 40:
            self.oxygen_warning_issued = False
        
        if self.power.get_percentage() < 20 and not self.power_warning_issued:
            warnings['power'] = f"POWER LOW: {self.power.get_percentage():.1f}%"
            self.power_warning_issued = True
        elif self.power.get_percentage() >= 35:
            self.power_warning_issued = False
        
        if self.food.current < self.food.maximum * 0.25 and not self.food_warning_issued:
            warnings['food'] = f"FOOD SUPPLIES LOW: {self.food.current:.0f} units"
            self.food_warning_issued = True
        elif self.food.current >= self.food.maximum * 0.4:
            self.food_warning_issued = False
        
        return warnings
    
    def set_ration_level(self, level: RationLevel):
        """Change rationing level (affects consumption rates)"""
        self.ration_level = level
    
    def use_ammunition(self, count: int = 1) -> bool:
        """Use torpedoes. Returns whether successful."""
        if self.ammunition.current >= count:
            self.ammunition.consume(count)
            return True
        return False
    
    def repair_damage(self, amount: float) -> float:
        """Use repair materials. Returns amount actually used."""
        return self.repair_materials.consume(amount)
    
    def use_medical(self, amount: float) -> float:
        """Use medical supplies. Returns amount actually used."""
        return self.medical.consume(amount)
    
    def get_status_report(self) -> str:
        """Generate supply status report"""
        lines = [
            "═" * 50,
            "SUPPLY STATUS REPORT",
            "═" * 50,
            f"Oxygen:         {self.oxygen.get_percentage():6.1f}% [{self.oxygen.get_status()}]",
            f"Power:          {self.power.get_percentage():6.1f}% [{self.power.get_status()}]",
            f"Food:           {self.food.current:6.0f}/{self.food.maximum:.0f} [{self.food.get_status()}]",
            f"Water:          {self.water.current:6.0f}/{self.water.maximum:.0f} [{self.water.get_status()}]",
            f"Ammunition:     {self.ammunition.current:6.0f}/{self.ammunition.maximum:.0f}",
            f"Fuel:           {self.fuel.current:6.0f}/{self.fuel.maximum:.0f} [{self.fuel.get_status()}]",
            f"Medical:        {self.medical.current:6.0f}/{self.medical.maximum:.0f}",
            f"Repair Mats:    {self.repair_materials.current:6.0f}/{self.repair_materials.maximum:.0f}",
            f"\nRation Level:   {self.ration_level.name}",
            f"Food Consumed:  {self.total_food_consumed} total units",
            f"Water Consumed: {self.total_water_consumed} total units",
            "═" * 50,
        ]
        return "\n".join(lines)
    
    def get_critical_resources(self) -> list:
        """Get list of resources below critical thresholds"""
        critical = []
        if self.oxygen.get_percentage() < 25:
            critical.append(f"Oxygen: {self.oxygen.get_percentage():.1f}%")
        if self.power.get_percentage() < 15:
            critical.append(f"Power: {self.power.get_percentage():.1f}%")
        if self.food.current < 50:
            critical.append(f"Food: {self.food.current:.0f} units")
        if self.water.current < 30:
            critical.append(f"Water: {self.water.current:.0f} units")
        if self.fuel.current < 100:
            critical.append(f"Fuel: {self.fuel.current:.0f} units")
        return critical
    
    def get_summary(self) -> Dict[str, float]:
        """Get summary percentages for all resources"""
        return {
            "oxygen": self.oxygen.get_percentage(),
            "power": self.power.get_percentage(),
            "food": self.food.get_percentage(),
            "water": self.water.get_percentage(),
            "ammunition": (self.ammunition.current / self.ammunition.maximum * 100),
            "fuel": self.fuel.get_percentage(),
        }

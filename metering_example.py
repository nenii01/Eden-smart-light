"""
Complete Integration Example: Power Metering System
Shows how to use all power metering components together
"""

from power_metering import (
    PowerMeteringMixin, PowerMeteringSystemMixin, 
    EnergyTariff, PowerUsageRecord
)
from datetime import datetime, timedelta
import json


# ==================== ENHANCED SMART BULB WITH METERING ====================

class SmartBulbWithMetering(PowerMeteringMixin):
    """Smart bulb with integrated power metering capabilities."""
    
    def __init__(self, bulb_id: str, name: str, rated_power: float = 12.0, max_brightness: int = 100):
        # Initialize parent metering attributes
        self.bulb_id = bulb_id
        self.name = name
        self.max_brightness = max_brightness
        self._is_on = False
        self._brightness = 100
        self._color_mode = "white"
        self._color_temperature = 6500
        self._rgb_color = (255, 255, 255)
        self._last_update = datetime.now()
        
        # Initialize metering mixin
        super().__init__(rated_power=rated_power)
    
    def set_brightness(self, level: int) -> None:
        """Set brightness and automatically turn on/off."""
        if not 0 <= level <= self.max_brightness:
            raise ValueError(f"Brightness must be between 0 and {self.max_brightness}")
        
        self._brightness = level
        if level > 0 and not self._is_on:
            self.turn_on_metered()
        elif level == 0:
            self.turn_off_metered()
        
        self._last_update = datetime.now()
    
    def get_status(self) -> dict:
        """Get current bulb status."""
        return {
            "id": self.bulb_id,
            "name": self.name,
            "is_on": self._is_on,
            "brightness": self._brightness,
            "color_mode": self._color_mode,
            "rgb_color": self._rgb_color,
            "color_temperature": self._color_temperature,
            "current_power_draw": self.get_current_power_draw(),
            "last_update": self._last_update.isoformat()
        }


# ==================== ENHANCED ROOM WITH METERING ====================

class RoomWithMetering:
    """Room containing smart bulbs with power metering."""
    
    def __init__(self, room_id: str, name: str, room_type: str = "living_room"):
        self.room_id = room_id
        self.name = name
        self.room_type = room_type
        self.bulbs = {}
    
    def add_bulb(self, bulb: SmartBulbWithMetering) -> None:
        """Add a metered bulb to the room."""
        self.bulbs[bulb.bulb_id] = bulb
    
    def get_bulb(self, bulb_id: str) -> SmartBulbWithMetering:
        """Get a bulb by ID."""
        return self.bulbs.get(bulb_id)
    
    def get_status(self) -> dict:
        """Get room status."""
        return {
            "room_id": self.room_id,
            "name": self.name,
            "room_type": self.room_type,
            "bulbs": {bid: b.get_status() for bid, b in self.bulbs.items()},
            "bulb_count": len(self.bulbs)
        }


# ==================== ENHANCED SMART HOME WITH METERING ====================

class SmartHomeWithMetering(PowerMeteringSystemMixin):
    """Smart home system with integrated power metering and analytics."""
    
    def __init__(self):
        self.rooms = {}
        self.users = {}
        self.guest_passes = {}
        self.active_sessions = {}
    
    def add_room(self, room: RoomWithMetering) -> None:
        """Add a room to the system."""
        self.rooms[room.room_id] = room
        print(f"✅ Room added: {room.name}")
    
    def get_home_status(self) -> dict:
        """Get overall home status."""
        return {
            "rooms": {rid: r.get_status() for rid, r in self.rooms.items()},
            "total_rooms": len(self.rooms),
            "total_bulbs": sum(len(r.bulbs) for r in self.rooms.values())
        }


# ==================== DEMONSTRATION & TESTING ====================

def demonstrate_power_metering():
    """Complete demonstration of the power metering system."""
    
    print("=" * 70)
    print("🏠 SMART HOME WITH POWER METERING SYSTEM DEMO")
    print("=" * 70)
    
    # Initialize system
    home = SmartHomeWithMetering()
    
    # Create rooms
    print("\n📍 Setting up rooms and bulbs...")
    
    living_room = RoomWithMetering("room_living", "Living Room", "living_room")
    living_room.add_bulb(SmartBulbWithMetering("bulb_lr_1", "Main Light", rated_power=15.0))
    living_room.add_bulb(SmartBulbWithMetering("bulb_lr_2", "Accent Light", rated_power=9.0))
    home.add_room(living_room)
    
    bedroom = RoomWithMetering("room_bed", "Bedroom", "bedroom")
    bedroom.add_bulb(SmartBulbWithMetering("bulb_bed_1", "Ceiling Light", rated_power=12.0))
    bedroom.add_bulb(SmartBulbWithMetering("bulb_bed_2", "Bedside Light", rated_power=6.0))
    home.add_room(bedroom)
    
    kitchen = RoomWithMetering("room_kitchen", "Kitchen", "kitchen")
    kitchen.add_bulb(SmartBulbWithMetering("bulb_k_1", "Overhead Light", rated_power=20.0))
    home.add_room(kitchen)
    
    print("\n✅ System initialized with 3 rooms and 5 bulbs")
    
    # Simulate usage
    print("\n" + "=" * 70)
    print("⚡ SIMULATING DAILY USAGE PATTERNS")
    print("=" * 70)
    
    # Living room usage
    print("\n🌅 Morning - Living Room (7-9 AM)")
    living_main = living_room.get_bulb("bulb_lr_1")
    living_main.turn_on_metered()
    living_main.set_brightness(100)
    print(f"   {living_main.name}: ON @ 100% ({living_main.get_current_power_draw():.2f}W)")
    
    # Simulate time passage (normally this would be real time)
    import time
    print("   [Simulating 2 hour usage...]")
    
    living_main.turn_off_metered()
    print(f"   {living_main.name}: OFF")
    
    # Evening usage
    print("\n🌆 Evening - Multiple Rooms (6-10 PM)")
    
    # Living room evening
    living_main.turn_on_metered()
    living_main.set_brightness(80)
    living_accent = living_room.get_bulb("bulb_lr_2")
    living_accent.turn_on_metered()
    living_accent.set_brightness(50)
    
    print(f"   Living Room:")
    print(f"     - {living_main.name}: ON @ 80% ({living_main.get_current_power_draw():.2f}W)")
    print(f"     - {living_accent.name}: ON @ 50% ({living_accent.get_current_power_draw():.2f}W)")
    
    # Bedroom evening
    bed_ceiling = bedroom.get_bulb("bulb_bed_1")
    bed_side = bedroom.get_bulb("bulb_bed_2")
    bed_ceiling.turn_on_metered()
    bed_ceiling.set_brightness(60)
    bed_side.turn_on_metered()
    bed_side.set_brightness(30)
    
    print(f"   Bedroom:")
    print(f"     - {bed_ceiling.name}: ON @ 60% ({bed_ceiling.get_current_power_draw():.2f}W)")
    print(f"     - {bed_side.name}: ON @ 30% ({bed_side.get_current_power_draw():.2f}W)")
    
    # Kitchen evening
    kitchen_light = kitchen.get_bulb("bulb_k_1")
    kitchen_light.turn_on_metered()
    kitchen_light.set_brightness(100)
    
    print(f"   Kitchen:")
    print(f"     - {kitchen_light.name}: ON @ 100% ({kitchen_light.get_current_power_draw():.2f}W)")
    
    print("   [Simulating 4 hour usage...]")
    
    living_main.turn_off_metered()
    living_accent.turn_off_metered()
    bed_ceiling.turn_off_metered()
    bed_side.turn_off_metered()
    kitchen_light.turn_off_metered()
    
    print("   All lights turned off for the night")
    
    # Display metrics
    print("\n" + "=" * 70)
    print("📊 POWER CONSUMPTION METRICS")
    print("=" * 70)
    
    # Individual bulb metrics
    print("\n🔍 Individual Bulb Metrics (7-day average):")
    for bulb in living_room.bulbs.values():
        stats = bulb.get_usage_stats(days=7)
        print(f"\n   {bulb.name}:")
        print(f"     Total Energy: {stats['total_energy_kwh']:.4f} kWh")
        print(f"     On Time: {stats['on_time_hours']:.2f} hours")
        print(f"     Avg Power: {stats['avg_power_watts']:.2f} W")
        print(f"     Peak Power: {stats['peak_power_watts']:.2f} W")
        print(f"     Est. Monthly: ${stats['estimated_monthly_cost']:.2f}")
        print(f"     Est. Yearly: ${stats['estimated_yearly_cost']:.2f}")
    
    # Room summary
    print("\n📍 Room Energy Summary:")
    room_summary = home.get_room_energy_summary("room_living", days=7)
    print(f"\n   {room_summary['room_name']}:")
    print(f"     Total Energy: {room_summary['total_energy_kwh']:.4f} kWh")
    print(f"     Total On-Time: {room_summary['total_on_hours']:.2f} hours")
    print(f"     Est. Monthly Cost: ${room_summary['estimated_monthly_cost']:.2f}")
    print(f"     Bulbs: {room_summary['bulb_count']}")
    
    # Home summary
    print("\n🏠 Home Energy Summary:")
    home_summary = home.get_home_energy_summary(days=7)
    print(f"   Total Energy: {home_summary['total_energy_kwh']:.4f} kWh")
    print(f"   Total On-Time: {home_summary['total_on_hours']:.2f} hours")
    print(f"   Total Rooms: {home_summary['total_rooms']}")
    print(f"   Total Bulbs: {home_summary['total_bulbs']}")
    print(f"   Est. Monthly Cost: ${home_summary['estimated_monthly_cost']:.2f}")
    print(f"   Est. Yearly Cost: ${home_summary['estimated_yearly_cost']:.2f}")
    
    # Top consumers
    print("\n🔥 Top Energy Consumers:")
    top_consumers = home.get_top_energy_consumers(days=7, limit=5)
    for consumer in top_consumers:
        print(f"\n   #{consumer['rank']} - {consumer['bulb_name']} ({consumer['room_name']})")
        print(f"       Energy: {consumer['energy_kwh']:.4f} kWh")
        print(f"       On Time: {consumer['on_hours']:.2f} hours")
        print(f"       Est. Cost: ${consumer['cost']:.2f}")
    
    # Energy trends
    print("\n📈 Energy Trends (30-day):")
    trends = home.get_energy_trends(days=30)
    print(f"   Total Energy: {trends['total_kwh']:.4f} kWh")
    print(f"   Avg Daily: {trends['avg_daily_kwh']:.4f} kWh")
    print(f"   Max Daily: {trends['max_daily_kwh']:.4f} kWh")
    print(f"   Min Daily: {trends['min_daily_kwh']:.4f} kWh")
    
    # Export functionality
    print("\n" + "=" * 70)
    print("💾 EXPORT FUNCTIONALITY")
    print("=" * 70)
    
    # CSV Export
    print("\n📥 Exporting bulb data to CSV...")
    csv_data = living_main.export_usage_csv(days=30)
    print("   CSV Header:")
    print(f"   {csv_data.split(chr(10))[0]}")
    
    print("\n" + "=" * 70)
    print("✅ DEMO COMPLETE")
    print("=" * 70)


# ==================== CONFIGURATION EXAMPLE ====================

def example_flask_integration():
    """Example of how to integrate with Flask."""
    
    code = '''
from flask import Flask
from power_metering_api import register_metering_api
from metering_example import SmartHomeWithMetering, RoomWithMetering, SmartBulbWithMetering

# Initialize Flask
app = Flask(__name__)

# Create smart home system
home = SmartHomeWithMetering()

# Setup rooms and bulbs
living_room = RoomWithMetering("room_living", "Living Room")
living_room.add_bulb(SmartBulbWithMetering("bulb_lr_1", "Main Light", rated_power=15.0))
home.add_room(living_room)

# Register metering API
register_metering_api(app, home)

# API Endpoints Available:
# GET  /api/bulb-metrics/<room_id>/<bulb_id>?days=7
# GET  /api/room-energy-summary/<room_id>?days=7
# GET  /api/home-energy-summary?days=7
# GET  /api/top-energy-consumers?days=7&limit=10
# GET  /api/energy-trends?days=30
# GET  /api/daily-stats/<room_id>/<bulb_id>?days=7
# GET  /api/hourly-consumption/<room_id>/<bulb_id>?hours=24
# GET  /api/historical-data/<room_id>/<bulb_id>?hours=168
# GET  /api/export-csv/<room_id>/<bulb_id>?days=30
# GET  /api/energy-report/<room_id>/<bulb_id>?days=30
# GET  /api/bulb-settings/<room_id>/<bulb_id>
# PUT  /api/bulb-settings/<room_id>/<bulb_id>

if __name__ == "__main__":
    app.run(debug=True, port=5000)
    '''
    
    print("Flask Integration Example:")
    print(code)


if __name__ == "__main__":
    # Run the demonstration
    demonstrate_power_metering()
    
    print("\n" + "=" * 70)
    print("📚 DOCUMENTATION")
    print("=" * 70)
    
    print("""
POWER METERING SYSTEM - KEY FEATURES:

1. ⚡ Individual Bulb Metering
   - Per-bulb power consumption tracking
   - Brightness-aware power calculation
   - Session-based usage recording

2. 📊 Analytics & Reporting
   - Daily, hourly, and historical data
   - Cost estimation (configurable tariffs)
   - Energy trends and analysis

3. 💰 Cost Tracking
   - Real-time cost calculation
   - Monthly and yearly projections
   - Configurable energy tariffs

4. 📈 Data Visualization (React Dashboard)
   - Line charts for consumption trends
   - Bar charts for daily/hourly breakdown
   - Pie charts for power distribution
   - Detailed metrics cards

5. 🔌 REST API
   - 12+ endpoints for data access
   - CSV export functionality
   - Comprehensive reporting

6. 🎯 Smart Analytics
   - Top energy consumers ranking
   - Energy trend analysis
   - Peak usage identification

CONFIGURATION:

Default Energy Tariff: $0.12 per kWh (configurable)

Bulb Power Ratings (examples):
- LED Bulb: 9-12W
- Standard Incandescent: 60W
- Smart Bulb: 6-15W
- Accent Lighting: 4-6W

TIME RANGES:
- Hourly data: up to 30 days
- Daily data: up to 365 days
- Historical export: up to 365 days

NEXT STEPS:
1. Integrate SmartBulbWithMetering into your existing SmartBulb class
2. Add PowerMeteringSystemMixin to SmartHomeSystem
3. Register Flask API blueprint with your app
4. Deploy React dashboard component
5. Configure energy tariff for your region
    """)

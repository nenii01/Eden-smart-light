"""
Power Metering System for Smart Bulbs
Tracks power consumption, energy usage, and provides analytics.
"""

from enum import Enum
from datetime import datetime, timedelta
from typing import Optional, List, Dict
import json
from dataclasses import dataclass, asdict
from collections import defaultdict


@dataclass
class PowerUsageRecord:
    """Individual power consumption record."""
    timestamp: str  # ISO format
    power_watts: float
    duration_seconds: int
    energy_kwh: float  # Calculated: (power_watts * duration_seconds) / 3600 / 1000
    brightness_level: int


@dataclass
class DailyEnergyStats:
    """Daily aggregated energy statistics."""
    date: str  # YYYY-MM-DD
    total_energy_kwh: float
    total_on_hours: float
    avg_power_watts: float
    peak_power_watts: float
    min_power_watts: float
    estimated_cost: float


class EnergyTariff:
    """Represents energy pricing model."""
    
    def __init__(self, rate_per_kwh: float = 0.12, currency: str = "USD"):
        self.rate_per_kwh = rate_per_kwh
        self.currency = currency
    
    def calculate_cost(self, energy_kwh: float) -> float:
        return energy_kwh * self.rate_per_kwh


class PowerMeteringMixin:
    """
    Mixin to add power metering capabilities to SmartBulb.
    Include this in your SmartBulb class.
    """
    
    def __init__(self, *args, rated_power: float = 12.0, **kwargs):
        super().__init__(*args, **kwargs)
        self.rated_power = rated_power  # Watts (e.g., 12W LED bulb)
        self.usage_history: List[PowerUsageRecord] = []
        self.session_start: Optional[datetime] = None
        self.energy_tariff = EnergyTariff()
    
    def get_current_power_draw(self) -> float:
        """Calculate current power draw based on state (brightness affects consumption)."""
        if not self._is_on:
            return 0.0
        # Power scales with brightness (simplified linear model)
        return self.rated_power * (self._brightness / 100)
    
    def _record_usage_session(self) -> None:
        """Record power usage session when bulb turns off."""
        if self._is_on or not self.session_start:
            return
        
        duration = (datetime.now() - self.session_start).total_seconds()
        avg_power = self.rated_power * (self._brightness / 100)
        energy_kwh = (avg_power * duration) / 3600 / 1000
        
        record = PowerUsageRecord(
            timestamp=self.session_start.isoformat(),
            power_watts=avg_power,
            duration_seconds=int(duration),
            energy_kwh=energy_kwh,
            brightness_level=self._brightness
        )
        self.usage_history.append(record)
        self.session_start = None
    
    def turn_on_metered(self) -> None:
        """Turn on bulb and start metering session."""
        if not self._is_on:
            self.session_start = datetime.now()
        self._is_on = True
        self._last_update = datetime.now()
    
    def turn_off_metered(self) -> None:
        """Turn off bulb and record usage."""
        if self._is_on:
            self._record_usage_session()
        self._is_on = False
        self._last_update = datetime.now()
    
    def get_energy_kwh(self, days: int = 7) -> float:
        """Get total energy consumed in the last N days (kWh)."""
        cutoff = datetime.now() - timedelta(days=days)
        return sum(
            r.energy_kwh 
            for r in self.usage_history 
            if datetime.fromisoformat(r.timestamp) > cutoff
        )
    
    def get_on_time_hours(self, days: int = 7) -> float:
        """Get total ON time in the last N days (hours)."""
        cutoff = datetime.now() - timedelta(days=days)
        return sum(
            r.duration_seconds / 3600
            for r in self.usage_history
            if datetime.fromisoformat(r.timestamp) > cutoff
        )
    
    def get_daily_stats(self, days: int = 7) -> List[DailyEnergyStats]:
        """Get daily aggregated statistics."""
        cutoff = datetime.now() - timedelta(days=days)
        daily_data = defaultdict(list)
        
        for record in self.usage_history:
            record_date = datetime.fromisoformat(record.timestamp)
            if record_date > cutoff:
                date_key = record_date.strftime("%Y-%m-%d")
                daily_data[date_key].append(record)
        
        stats = []
        for date_key in sorted(daily_data.keys()):
            records = daily_data[date_key]
            total_energy = sum(r.energy_kwh for r in records)
            total_seconds = sum(r.duration_seconds for r in records)
            powers = [r.power_watts for r in records]
            
            daily_stat = DailyEnergyStats(
                date=date_key,
                total_energy_kwh=round(total_energy, 4),
                total_on_hours=round(total_seconds / 3600, 2),
                avg_power_watts=round(sum(powers) / len(powers), 2) if powers else 0,
                peak_power_watts=round(max(powers), 2) if powers else 0,
                min_power_watts=round(min(powers), 2) if powers else 0,
                estimated_cost=round(self.energy_tariff.calculate_cost(total_energy), 4)
            )
            stats.append(daily_stat)
        
        return stats
    
    def get_usage_stats(self, days: int = 7) -> Dict:
        """Get comprehensive usage statistics."""
        energy_kwh = self.get_energy_kwh(days)
        on_time_hours = self.get_on_time_hours(days)
        
        cutoff = datetime.now() - timedelta(days=days)
        relevant = [
            r for r in self.usage_history
            if datetime.fromisoformat(r.timestamp) > cutoff
        ]
        
        powers = [r.power_watts for r in relevant]
        
        return {
            "period_days": days,
            "total_energy_kwh": round(energy_kwh, 4),
            "on_time_hours": round(on_time_hours, 2),
            "avg_power_watts": round(sum(powers) / len(powers), 2) if powers else 0,
            "peak_power_watts": round(max(powers), 2) if powers else 0,
            "min_power_watts": round(min(powers), 2) if powers else 0,
            "estimated_monthly_cost": round(
                self.energy_tariff.calculate_cost(energy_kwh * (30 / days)), 4
            ),
            "estimated_yearly_cost": round(
                self.energy_tariff.calculate_cost(energy_kwh * (365 / days)), 4
            ),
            "session_count": len(relevant),
            "rated_power_watts": self.rated_power
        }
    
    def get_hourly_consumption(self, hours: int = 24) -> List[Dict]:
        """Get hourly consumption breakdown."""
        cutoff = datetime.now() - timedelta(hours=hours)
        hourly_data = defaultdict(list)
        
        for record in self.usage_history:
            record_date = datetime.fromisoformat(record.timestamp)
            if record_date > cutoff:
                hour_key = record_date.strftime("%Y-%m-%d %H:00")
                hourly_data[hour_key].append(record)
        
        result = []
        for hour_key in sorted(hourly_data.keys()):
            records = hourly_data[hour_key]
            total_energy = sum(r.energy_kwh for r in records)
            avg_power = sum(r.power_watts for r in records) / len(records)
            
            result.append({
                "hour": hour_key,
                "energy_kwh": round(total_energy, 4),
                "avg_power_watts": round(avg_power, 2),
                "sessions": len(records)
            })
        
        return result
    
    def get_historical_data(self, hours: int = 168) -> List[Dict]:
        """Get detailed historical power consumption data (for charting)."""
        cutoff = datetime.now() - timedelta(hours=hours)
        
        data = []
        for record in sorted(
            self.usage_history,
            key=lambda r: r.timestamp
        ):
            if datetime.fromisoformat(record.timestamp) > cutoff:
                data.append({
                    "timestamp": record.timestamp,
                    "power_watts": record.power_watts,
                    "energy_kwh": record.energy_kwh,
                    "duration_minutes": round(record.duration_seconds / 60, 1),
                    "brightness": record.brightness_level
                })
        
        return data[-100:]  # Return last 100 records for frontend charting
    
    def reset_usage_history(self) -> None:
        """Clear all usage history (careful with this!)."""
        self.usage_history = []
        self.session_start = None
    
    def export_usage_csv(self, days: int = 30) -> str:
        """Export usage history as CSV."""
        cutoff = datetime.now() - timedelta(days=days)
        
        csv = "timestamp,power_watts,duration_seconds,energy_kwh,brightness_level\\n"
        for record in self.usage_history:
            if datetime.fromisoformat(record.timestamp) > cutoff:
                csv += f"{record.timestamp},{record.power_watts},{record.duration_seconds},{record.energy_kwh},{record.brightness_level}\\n"
        
        return csv


# ==================== ENHANCED SMART HOME SYSTEM METHODS ====================

class PowerMeteringSystemMixin:
    """
    Mixin for SmartHomeSystem to add power metering API methods.
    """
    
    def get_bulb_metrics(self, room_id: str, bulb_id: str, days: int = 7) -> Dict:
        """Get comprehensive metrics for a specific bulb."""
        room = self.rooms.get(room_id)
        if not room:
            raise ValueError(f"Room {room_id} not found")
        
        bulb = room.get_bulb(bulb_id)
        if not bulb:
            raise ValueError(f"Bulb {bulb_id} not found in room")
        
        if not hasattr(bulb, 'get_usage_stats'):
            raise AttributeError("Bulb does not support power metering")
        
        return {
            "bulb_id": bulb_id,
            "bulb_name": bulb.name,
            "room_id": room_id,
            "room_name": room.name,
            "current_status": bulb.get_status(),
            "usage_stats": bulb.get_usage_stats(days),
            "daily_stats": [asdict(s) for s in bulb.get_daily_stats(days)],
            "hourly_consumption": bulb.get_hourly_consumption(24),
            "timestamp": datetime.now().isoformat()
        }
    
    def get_room_energy_summary(self, room_id: str, days: int = 7) -> Dict:
        """Get aggregated energy metrics for all bulbs in a room."""
        room = self.rooms.get(room_id)
        if not room:
            raise ValueError(f"Room {room_id} not found")
        
        total_energy = 0.0
        total_cost = 0.0
        total_on_hours = 0.0
        bulb_metrics = []
        
        for bulb_id, bulb in room.bulbs.items():
            if hasattr(bulb, 'get_usage_stats'):
                stats = bulb.get_usage_stats(days)
                total_energy += stats['total_energy_kwh']
                total_cost += stats['estimated_monthly_cost']
                total_on_hours += stats['on_time_hours']
                
                bulb_metrics.append({
                    "bulb_id": bulb_id,
                    "bulb_name": bulb.name,
                    "energy_kwh": stats['total_energy_kwh'],
                    "cost": stats['estimated_monthly_cost']
                })
        
        return {
            "room_id": room_id,
            "room_name": room.name,
            "period_days": days,
            "total_energy_kwh": round(total_energy, 4),
            "total_on_hours": round(total_on_hours, 2),
            "estimated_monthly_cost": round(total_cost, 4),
            "bulb_breakdown": bulb_metrics,
            "bulb_count": len(bulb_metrics),
            "timestamp": datetime.now().isoformat()
        }
    
    def get_home_energy_summary(self, days: int = 7) -> Dict:
        """Get aggregated energy metrics for entire home."""
        total_energy = 0.0
        total_cost = 0.0
        total_on_hours = 0.0
        room_summaries = []
        
        for room_id, room in self.rooms.items():
            try:
                room_summary = self.get_room_energy_summary(room_id, days)
                total_energy += room_summary['total_energy_kwh']
                total_cost += room_summary['estimated_monthly_cost']
                total_on_hours += room_summary['total_on_hours']
                room_summaries.append(room_summary)
            except Exception as e:
                print(f"Error processing room {room_id}: {e}")
        
        return {
            "period_days": days,
            "total_rooms": len(self.rooms),
            "total_bulbs": sum(len(room.bulbs) for room in self.rooms.values()),
            "total_energy_kwh": round(total_energy, 4),
            "total_on_hours": round(total_on_hours, 2),
            "estimated_monthly_cost": round(total_cost, 4),
            "estimated_yearly_cost": round(total_cost * 12, 4),
            "room_summaries": room_summaries,
            "timestamp": datetime.now().isoformat()
        }
    
    def get_top_energy_consumers(self, days: int = 7, limit: int = 10) -> List[Dict]:
        """Get bulbs sorted by energy consumption."""
        bulb_stats = []
        
        for room_id, room in self.rooms.items():
            for bulb_id, bulb in room.bulbs.items():
                if hasattr(bulb, 'get_usage_stats'):
                    stats = bulb.get_usage_stats(days)
                    bulb_stats.append({
                        "rank": 0,
                        "bulb_id": bulb_id,
                        "bulb_name": bulb.name,
                        "room_id": room_id,
                        "room_name": room.name,
                        "energy_kwh": stats['total_energy_kwh'],
                        "on_hours": stats['on_time_hours'],
                        "cost": stats['estimated_monthly_cost']
                    })
        
        # Sort by energy consumption
        bulb_stats.sort(key=lambda x: x['energy_kwh'], reverse=True)
        
        # Add rankings
        for i, stat in enumerate(bulb_stats[:limit], 1):
            stat['rank'] = i
        
        return bulb_stats[:limit]
    
    def get_energy_trends(self, days: int = 30) -> Dict:
        """Analyze energy consumption trends over time."""
        daily_totals = defaultdict(float)
        
        for room in self.rooms.values():
            for bulb in room.bulbs.values():
                if hasattr(bulb, 'usage_history'):
                    cutoff = datetime.now() - timedelta(days=days)
                    for record in bulb.usage_history:
                        record_date = datetime.fromisoformat(record.timestamp)
                        if record_date > cutoff:
                            date_key = record_date.strftime("%Y-%m-%d")
                            daily_totals[date_key] += record.energy_kwh
        
        trend_data = [
            {"date": date, "energy_kwh": round(energy, 4)}
            for date, energy in sorted(daily_totals.items())
        ]
        
        energies = [t['energy_kwh'] for t in trend_data]
        
        return {
            "period_days": days,
            "trend_data": trend_data,
            "avg_daily_kwh": round(sum(energies) / len(energies), 4) if energies else 0,
            "max_daily_kwh": round(max(energies), 4) if energies else 0,
            "min_daily_kwh": round(min(energies), 4) if energies else 0,
            "total_kwh": round(sum(energies), 4)
        }

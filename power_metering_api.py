"""
Flask API endpoints for Power Metering System
Provides REST API for accessing bulb power metrics and analytics
"""

from flask import Flask, jsonify, request, Blueprint
from datetime import datetime, timedelta
from typing import Dict, List
import json

# Create Blueprint for metering API
metering_api = Blueprint('metering_api', __name__, url_prefix='/api')


# ==================== BULB METRICS ENDPOINTS ====================

@metering_api.route('/bulb-metrics/<room_id>/<bulb_id>', methods=['GET'])
def get_bulb_metrics(room_id: str, bulb_id: str):
    """
    Get comprehensive metrics for a specific bulb.
    
    Query Parameters:
    - days: Number of days to analyze (default: 7)
    
    Returns:
        {
            "bulb_id": str,
            "bulb_name": str,
            "room_id": str,
            "room_name": str,
            "current_status": {...},
            "usage_stats": {...},
            "daily_stats": [...],
            "hourly_consumption": [...],
            "timestamp": str
        }
    """
    try:
        days = request.args.get('days', 7, type=int)
        
        # Validate days parameter
        if days < 1 or days > 365:
            return jsonify({"error": "Days must be between 1 and 365"}), 400
        
        # Get metrics from system (assuming 'home' is global SmartHomeSystem instance)
        metrics = home.get_bulb_metrics(room_id, bulb_id, days)
        
        return jsonify(metrics), 200
    
    except ValueError as e:
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500


@metering_api.route('/room-energy-summary/<room_id>', methods=['GET'])
def get_room_energy_summary(room_id: str):
    """
    Get aggregated energy metrics for all bulbs in a room.
    
    Query Parameters:
    - days: Number of days to analyze (default: 7)
    
    Returns:
        {
            "room_id": str,
            "room_name": str,
            "period_days": int,
            "total_energy_kwh": float,
            "total_on_hours": float,
            "estimated_monthly_cost": float,
            "bulb_breakdown": [...],
            "bulb_count": int,
            "timestamp": str
        }
    """
    try:
        days = request.args.get('days', 7, type=int)
        
        if days < 1 or days > 365:
            return jsonify({"error": "Days must be between 1 and 365"}), 400
        
        summary = home.get_room_energy_summary(room_id, days)
        return jsonify(summary), 200
    
    except ValueError as e:
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500


@metering_api.route('/home-energy-summary', methods=['GET'])
def get_home_energy_summary():
    """
    Get aggregated energy metrics for entire home.
    
    Query Parameters:
    - days: Number of days to analyze (default: 7)
    
    Returns:
        {
            "period_days": int,
            "total_rooms": int,
            "total_bulbs": int,
            "total_energy_kwh": float,
            "total_on_hours": float,
            "estimated_monthly_cost": float,
            "estimated_yearly_cost": float,
            "room_summaries": [...],
            "timestamp": str
        }
    """
    try:
        days = request.args.get('days', 7, type=int)
        
        if days < 1 or days > 365:
            return jsonify({"error": "Days must be between 1 and 365"}), 400
        
        summary = home.get_home_energy_summary(days)
        return jsonify(summary), 200
    
    except Exception as e:
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500


# ==================== ANALYTICS ENDPOINTS ====================

@metering_api.route('/top-energy-consumers', methods=['GET'])
def get_top_energy_consumers():
    """
    Get bulbs sorted by energy consumption (top energy consumers).
    
    Query Parameters:
    - days: Number of days to analyze (default: 7)
    - limit: Number of results to return (default: 10, max: 50)
    
    Returns:
        [
            {
                "rank": int,
                "bulb_id": str,
                "bulb_name": str,
                "room_id": str,
                "room_name": str,
                "energy_kwh": float,
                "on_hours": float,
                "cost": float
            },
            ...
        ]
    """
    try:
        days = request.args.get('days', 7, type=int)
        limit = request.args.get('limit', 10, type=int)
        
        if days < 1 or days > 365:
            return jsonify({"error": "Days must be between 1 and 365"}), 400
        if limit < 1 or limit > 50:
            return jsonify({"error": "Limit must be between 1 and 50"}), 400
        
        consumers = home.get_top_energy_consumers(days, limit)
        return jsonify(consumers), 200
    
    except Exception as e:
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500


@metering_api.route('/energy-trends', methods=['GET'])
def get_energy_trends():
    """
    Analyze energy consumption trends over time.
    
    Query Parameters:
    - days: Number of days to analyze (default: 30)
    
    Returns:
        {
            "period_days": int,
            "trend_data": [
                {"date": str (YYYY-MM-DD), "energy_kwh": float},
                ...
            ],
            "avg_daily_kwh": float,
            "max_daily_kwh": float,
            "min_daily_kwh": float,
            "total_kwh": float
        }
    """
    try:
        days = request.args.get('days', 30, type=int)
        
        if days < 1 or days > 365:
            return jsonify({"error": "Days must be between 1 and 365"}), 400
        
        trends = home.get_energy_trends(days)
        return jsonify(trends), 200
    
    except Exception as e:
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500


@metering_api.route('/daily-stats/<room_id>/<bulb_id>', methods=['GET'])
def get_daily_stats(room_id: str, bulb_id: str):
    """
    Get daily aggregated statistics for a bulb.
    
    Query Parameters:
    - days: Number of days to analyze (default: 7)
    
    Returns:
        [
            {
                "date": str (YYYY-MM-DD),
                "total_energy_kwh": float,
                "total_on_hours": float,
                "avg_power_watts": float,
                "peak_power_watts": float,
                "min_power_watts": float,
                "estimated_cost": float
            },
            ...
        ]
    """
    try:
        days = request.args.get('days', 7, type=int)
        
        if days < 1 or days > 365:
            return jsonify({"error": "Days must be between 1 and 365"}), 400
        
        room = home.rooms.get(room_id)
        if not room:
            return jsonify({"error": f"Room {room_id} not found"}), 404
        
        bulb = room.get_bulb(bulb_id)
        if not bulb:
            return jsonify({"error": f"Bulb {bulb_id} not found"}), 404
        
        if not hasattr(bulb, 'get_daily_stats'):
            return jsonify({"error": "Bulb does not support power metering"}), 400
        
        from dataclasses import asdict
        daily_stats = bulb.get_daily_stats(days)
        return jsonify([asdict(stat) for stat in daily_stats]), 200
    
    except Exception as e:
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500


@metering_api.route('/hourly-consumption/<room_id>/<bulb_id>', methods=['GET'])
def get_hourly_consumption(room_id: str, bulb_id: str):
    """
    Get hourly consumption breakdown for a bulb.
    
    Query Parameters:
    - hours: Number of hours to analyze (default: 24)
    
    Returns:
        [
            {
                "hour": str (YYYY-MM-DD HH:00),
                "energy_kwh": float,
                "avg_power_watts": float,
                "sessions": int
            },
            ...
        ]
    """
    try:
        hours = request.args.get('hours', 24, type=int)
        
        if hours < 1 or hours > 720:  # Max 30 days
            return jsonify({"error": "Hours must be between 1 and 720"}), 400
        
        room = home.rooms.get(room_id)
        if not room:
            return jsonify({"error": f"Room {room_id} not found"}), 404
        
        bulb = room.get_bulb(bulb_id)
        if not bulb:
            return jsonify({"error": f"Bulb {bulb_id} not found"}), 404
        
        if not hasattr(bulb, 'get_hourly_consumption'):
            return jsonify({"error": "Bulb does not support power metering"}), 400
        
        hourly_data = bulb.get_hourly_consumption(hours)
        return jsonify(hourly_data), 200
    
    except Exception as e:
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500


@metering_api.route('/historical-data/<room_id>/<bulb_id>', methods=['GET'])
def get_historical_data(room_id: str, bulb_id: str):
    """
    Get detailed historical power consumption data (for charting).
    
    Query Parameters:
    - hours: Number of hours to analyze (default: 168 = 1 week)
    
    Returns:
        [
            {
                "timestamp": str (ISO format),
                "power_watts": float,
                "energy_kwh": float,
                "duration_minutes": float,
                "brightness": int
            },
            ...
        ]
    """
    try:
        hours = request.args.get('hours', 168, type=int)
        
        if hours < 1 or hours > 8760:  # Max 1 year
            return jsonify({"error": "Hours must be between 1 and 8760"}), 400
        
        room = home.rooms.get(room_id)
        if not room:
            return jsonify({"error": f"Room {room_id} not found"}), 404
        
        bulb = room.get_bulb(bulb_id)
        if not bulb:
            return jsonify({"error": f"Bulb {bulb_id} not found"}), 404
        
        if not hasattr(bulb, 'get_historical_data'):
            return jsonify({"error": "Bulb does not support power metering"}), 400
        
        history = bulb.get_historical_data(hours)
        return jsonify(history), 200
    
    except Exception as e:
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500


# ==================== EXPORT ENDPOINTS ====================

@metering_api.route('/export-csv/<room_id>/<bulb_id>', methods=['GET'])
def export_csv(room_id: str, bulb_id: str):
    """
    Export bulb usage history as CSV file.
    
    Query Parameters:
    - days: Number of days to export (default: 30)
    
    Returns:
        CSV file with columns: timestamp, power_watts, duration_seconds, energy_kwh, brightness_level
    """
    try:
        days = request.args.get('days', 30, type=int)
        
        if days < 1 or days > 365:
            return jsonify({"error": "Days must be between 1 and 365"}), 400
        
        room = home.rooms.get(room_id)
        if not room:
            return jsonify({"error": f"Room {room_id} not found"}), 404
        
        bulb = room.get_bulb(bulb_id)
        if not bulb:
            return jsonify({"error": f"Bulb {bulb_id} not found"}), 404
        
        if not hasattr(bulb, 'export_usage_csv'):
            return jsonify({"error": "Bulb does not support power metering"}), 400
        
        csv_data = bulb.export_usage_csv(days)
        
        return csv_data, 200, {
            'Content-Type': 'text/csv',
            'Content-Disposition': f'attachment; filename="{bulb_id}_usage_{datetime.now().strftime("%Y%m%d")}.csv"'
        }
    
    except Exception as e:
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500


# ==================== REPORT GENERATION ENDPOINTS ====================

@metering_api.route('/energy-report/<room_id>/<bulb_id>', methods=['GET'])
def generate_energy_report(room_id: str, bulb_id: str):
    """
    Generate comprehensive energy report for a bulb.
    
    Query Parameters:
    - days: Number of days to include in report (default: 30)
    
    Returns:
        Comprehensive JSON report with all metrics and analysis
    """
    try:
        days = request.args.get('days', 30, type=int)
        
        if days < 1 or days > 365:
            return jsonify({"error": "Days must be between 1 and 365"}), 400
        
        room = home.rooms.get(room_id)
        if not room:
            return jsonify({"error": f"Room {room_id} not found"}), 404
        
        bulb = room.get_bulb(bulb_id)
        if not bulb:
            return jsonify({"error": f"Bulb {bulb_id} not found"}), 404
        
        if not hasattr(bulb, 'get_usage_stats'):
            return jsonify({"error": "Bulb does not support power metering"}), 400
        
        from dataclasses import asdict
        
        # Compile comprehensive report
        report = {
            "report_generated": datetime.now().isoformat(),
            "bulb_info": {
                "bulb_id": bulb_id,
                "bulb_name": bulb.name,
                "room_id": room_id,
                "room_name": room.name,
                "rated_power": bulb.rated_power if hasattr(bulb, 'rated_power') else "N/A"
            },
            "period": {
                "days": days,
                "start_date": (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d"),
                "end_date": datetime.now().strftime("%Y-%m-%d")
            },
            "summary": bulb.get_usage_stats(days) if hasattr(bulb, 'get_usage_stats') else {},
            "daily_breakdown": [asdict(stat) for stat in bulb.get_daily_stats(days)] if hasattr(bulb, 'get_daily_stats') else [],
            "current_status": bulb.get_status() if hasattr(bulb, 'get_status') else {}
        }
        
        return jsonify(report), 200
    
    except Exception as e:
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500


# ==================== SETTINGS ENDPOINTS ====================

@metering_api.route('/bulb-settings/<room_id>/<bulb_id>', methods=['GET', 'PUT'])
def bulb_metering_settings(room_id: str, bulb_id: str):
    """
    Get or update power metering settings for a bulb.
    
    GET Returns:
        {
            "rated_power_watts": float,
            "energy_tariff": {
                "rate_per_kwh": float,
                "currency": str
            }
        }
    
    PUT Payload:
        {
            "rated_power_watts": float (optional),
            "rate_per_kwh": float (optional),
            "currency": str (optional)
        }
    """
    try:
        room = home.rooms.get(room_id)
        if not room:
            return jsonify({"error": f"Room {room_id} not found"}), 404
        
        bulb = room.get_bulb(bulb_id)
        if not bulb:
            return jsonify({"error": f"Bulb {bulb_id} not found"}), 404
        
        if request.method == 'GET':
            settings = {
                "rated_power_watts": bulb.rated_power if hasattr(bulb, 'rated_power') else "N/A",
                "energy_tariff": {
                    "rate_per_kwh": bulb.energy_tariff.rate_per_kwh if hasattr(bulb, 'energy_tariff') else "N/A",
                    "currency": bulb.energy_tariff.currency if hasattr(bulb, 'energy_tariff') else "N/A"
                }
            }
            return jsonify(settings), 200
        
        elif request.method == 'PUT':
            data = request.get_json()
            
            if 'rated_power_watts' in data and hasattr(bulb, 'rated_power'):
                bulb.rated_power = float(data['rated_power_watts'])
            
            if 'rate_per_kwh' in data and hasattr(bulb, 'energy_tariff'):
                bulb.energy_tariff.rate_per_kwh = float(data['rate_per_kwh'])
            
            if 'currency' in data and hasattr(bulb, 'energy_tariff'):
                bulb.energy_tariff.currency = data['currency']
            
            return jsonify({
                "message": "Settings updated successfully",
                "settings": {
                    "rated_power_watts": bulb.rated_power if hasattr(bulb, 'rated_power') else "N/A",
                    "energy_tariff": {
                        "rate_per_kwh": bulb.energy_tariff.rate_per_kwh if hasattr(bulb, 'energy_tariff') else "N/A",
                        "currency": bulb.energy_tariff.currency if hasattr(bulb, 'energy_tariff') else "N/A"
                    }
                }
            }), 200
    
    except ValueError as e:
        return jsonify({"error": f"Invalid parameter: {str(e)}"}), 400
    except Exception as e:
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500


# ==================== HEALTH CHECK ====================

@metering_api.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint for metering API."""
    return jsonify({
        "status": "healthy",
        "service": "power-metering-api",
        "timestamp": datetime.now().isoformat()
    }), 200


# ==================== REGISTRATION FUNCTION ====================

def register_metering_api(app: Flask, smart_home_system):
    """
    Register metering API blueprint with Flask app.
    
    Args:
        app: Flask application instance
        smart_home_system: SmartHomeSystem instance
    """
    global home
    home = smart_home_system
    app.register_blueprint(metering_api)
    print("✅ Power Metering API registered successfully!")


# Example usage in main Flask app:
"""
from flask import Flask
from power_metering_api import register_metering_api

app = Flask(__name__)

# ... setup your smart home system ...
home_system = SmartHomeSystem()

# Register metering API
register_metering_api(app, home_system)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
"""

import React, { useState, useEffect } from 'react';
import {
  LineChart, Line, BarChart, Bar, PieChart, Pie, Cell,
  XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer
} from 'recharts';
import './BulbMeteringDashboard.css';

const BulbMeteringDashboard = ({ roomId, bulbId, apiBaseUrl = 'http://localhost:5000' }) => {
  const [metrics, setMetrics] = useState(null);
  const [timeRange, setTimeRange] = useState(7); // days
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchBulbMetrics();
    const interval = setInterval(fetchBulbMetrics, 60000); // Refresh every minute
    return () => clearInterval(interval);
  }, [roomId, bulbId, timeRange]);

  const fetchBulbMetrics = async () => {
    try {
      setLoading(true);
      const response = await fetch(
        `${apiBaseUrl}/api/bulb-metrics/${roomId}/${bulbId}?days=${timeRange}`
      );
      if (!response.ok) throw new Error('Failed to fetch metrics');
      const data = await response.json();
      setMetrics(data);
      setError(null);
    } catch (err) {
      setError(err.message);
      console.error('Error fetching metrics:', err);
    } finally {
      setLoading(false);
    }
  };

  if (loading && !metrics) {
    return <div className="metering-dashboard loading">Loading metrics...</div>;
  }

  if (error) {
    return <div className="metering-dashboard error">Error: {error}</div>;
  }

  if (!metrics) {
    return <div className="metering-dashboard">No data available</div>;
  }

  const stats = metrics.usage_stats;
  const dailyStats = metrics.daily_stats || [];
  const hourlyData = metrics.hourly_consumption || [];

  // Format data for charts
  const dailyChartData = dailyStats.map(day => ({
    date: day.date.slice(-5), // MM-DD format
    energy: parseFloat(day.total_energy_kwh),
    cost: parseFloat(day.estimated_cost)
  }));

  const hourlyChartData = hourlyData.map(hour => ({
    time: hour.hour.slice(-5), // HH:00 format
    power: parseFloat(hour.avg_power_watts)
  }));

  const pieData = [
    { name: 'Current Usage', value: stats.avg_power_watts },
    { name: 'Available Capacity', value: Math.max(0, stats.rated_power_watts - stats.avg_power_watts) }
  ];

  const COLORS = ['#ff9800', '#e0e0e0'];

  return (
    <div className="metering-dashboard">
      <div className="dashboard-header">
        <div className="header-title">
          <h2>{metrics.bulb_name}</h2>
          <p className="room-info">{metrics.room_name}</p>
        </div>
        <div className="time-range-selector">
          {[1, 7, 14, 30].map(days => (
            <button
              key={days}
              className={`range-btn ${timeRange === days ? 'active' : ''}`}
              onClick={() => setTimeRange(days)}
            >
              {days}d
            </button>
          ))}
        </div>
      </div>

      {/* Current Status Card */}
      <div className="status-card">
        <div className="status-item">
          <label>Current Status</label>
          <div className={`status-value ${metrics.current_status.is_on ? 'on' : 'off'}`}>
            {metrics.current_status.is_on ? '🟢 ON' : '⚫ OFF'}
          </div>
        </div>
        <div className="status-item">
          <label>Brightness</label>
          <div className="status-value">{metrics.current_status.brightness}%</div>
        </div>
        <div className="status-item">
          <label>Current Power Draw</label>
          <div className="status-value">{stats.avg_power_watts.toFixed(2)} W</div>
        </div>
      </div>

      {/* Key Metrics Grid */}
      <div className="metrics-grid">
        <div className="metric-card energy">
          <div className="metric-icon">⚡</div>
          <div className="metric-content">
            <p className="metric-label">Total Energy</p>
            <p className="metric-value">{stats.total_energy_kwh.toFixed(4)} kWh</p>
            <p className="metric-period">{stats.period_days} days</p>
          </div>
        </div>

        <div className="metric-card time">
          <div className="metric-icon">⏱️</div>
          <div className="metric-content">
            <p className="metric-label">On Time</p>
            <p className="metric-value">{stats.on_time_hours.toFixed(1)} hrs</p>
            <p className="metric-period">Total usage</p>
          </div>
        </div>

        <div className="metric-card cost">
          <div className="metric-icon">💰</div>
          <div className="metric-content">
            <p className="metric-label">Est. Monthly Cost</p>
            <p className="metric-value">${stats.estimated_monthly_cost.toFixed(2)}</p>
            <p className="metric-period">Yearly: ${stats.estimated_yearly_cost.toFixed(2)}</p>
          </div>
        </div>

        <div className="metric-card power">
          <div className="metric-icon">📊</div>
          <div className="metric-content">
            <p className="metric-label">Power Stats</p>
            <p className="metric-value">
              {stats.peak_power_watts.toFixed(1)}W
              <span className="separator">•</span>
              {stats.min_power_watts.toFixed(1)}W
            </p>
            <p className="metric-period">Peak • Min</p>
          </div>
        </div>
      </div>

      {/* Charts Section */}
      <div className="charts-container">
        {/* Daily Energy Consumption */}
        <div className="chart-card">
          <h3>Daily Energy Consumption</h3>
          {dailyChartData.length > 0 ? (
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={dailyChartData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="date" />
                <YAxis label={{ value: 'Energy (kWh)', angle: -90, position: 'insideLeft' }} />
                <Tooltip formatter={(value) => value.toFixed(4)} />
                <Bar dataKey="energy" fill="#ff9800" name="Energy (kWh)" />
              </BarChart>
            </ResponsiveContainer>
          ) : (
            <p className="no-data">No daily data available</p>
          )}
        </div>

        {/* Hourly Power Consumption */}
        <div className="chart-card">
          <h3>Hourly Power Consumption (24h)</h3>
          {hourlyChartData.length > 0 ? (
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={hourlyChartData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="time" />
                <YAxis label={{ value: 'Power (W)', angle: -90, position: 'insideLeft' }} />
                <Tooltip formatter={(value) => value.toFixed(2)} />
                <Line type="monotone" dataKey="power" stroke="#2196F3" dot={false} />
              </LineChart>
            </ResponsiveContainer>
          ) : (
            <p className="no-data">No hourly data available</p>
          )}
        </div>

        {/* Power Consumption Gauge */}
        <div className="chart-card">
          <h3>Current Load</h3>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={pieData}
                cx="50%"
                cy="50%"
                innerRadius={60}
                outerRadius={100}
                dataKey="value"
              >
                {pieData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={COLORS[index]} />
                ))}
              </Pie>
              <Tooltip formatter={(value) => value.toFixed(2)} />
            </PieChart>
          </ResponsiveContainer>
          <div className="gauge-legend">
            <div className="gauge-item">
              <span className="gauge-color" style={{ backgroundColor: '#ff9800' }}></span>
              <span>{stats.avg_power_watts.toFixed(2)}W (Current)</span>
            </div>
            <div className="gauge-item">
              <span className="gauge-color" style={{ backgroundColor: '#e0e0e0' }}></span>
              <span>{Math.max(0, stats.rated_power_watts - stats.avg_power_watts).toFixed(2)}W (Available)</span>
            </div>
          </div>
        </div>

        {/* Daily Cost Breakdown */}
        <div className="chart-card">
          <h3>Daily Cost Breakdown</h3>
          {dailyChartData.length > 0 ? (
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={dailyChartData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="date" />
                <YAxis label={{ value: 'Cost ($)', angle: -90, position: 'insideLeft' }} />
                <Tooltip formatter={(value) => `$${value.toFixed(4)}`} />
                <Bar dataKey="cost" fill="#4CAF50" name="Cost ($)" />
              </BarChart>
            </ResponsiveContainer>
          ) : (
            <p className="no-data">No cost data available</p>
          )}
        </div>
      </div>

      {/* Details Table */}
      <div className="details-table">
        <h3>Detailed Statistics</h3>
        <table>
          <tbody>
            <tr>
              <td>Rated Power Capacity</td>
              <td className="value">{stats.rated_power_watts}W</td>
            </tr>
            <tr>
              <td>Total Sessions</td>
              <td className="value">{stats.session_count}</td>
            </tr>
            <tr>
              <td>Average Power</td>
              <td className="value">{stats.avg_power_watts.toFixed(2)}W</td>
            </tr>
            <tr>
              <td>Peak Power Draw</td>
              <td className="value">{stats.peak_power_watts.toFixed(2)}W</td>
            </tr>
            <tr>
              <td>Minimum Power Draw</td>
              <td className="value">{stats.min_power_watts.toFixed(2)}W</td>
            </tr>
            <tr>
              <td>On Time (Last {stats.period_days}d)</td>
              <td className="value">{stats.on_time_hours.toFixed(1)} hours</td>
            </tr>
          </tbody>
        </table>
      </div>

      {/* Export Button */}
      <div className="action-buttons">
        <button className="btn btn-export" onClick={() => {
          // Implement CSV export
          console.log('Export CSV');
        }}>
          📥 Export CSV
        </button>
        <button className="btn btn-refresh" onClick={fetchBulbMetrics}>
          🔄 Refresh
        </button>
      </div>
    </div>
  );
};

export default BulbMeteringDashboard;

import React from 'react';
import { Cloud, Sun, CloudRain, Wind, Eye, Droplets, Thermometer, Gauge, MapPin } from 'lucide-react';

function WeatherCard({ port, onWeatherQuery, loading, data }) {
  // If data is provided, render as weather display
  if (data) {
    if (data.error) {
      return (
        <div className="p-6 rounded-lg border bg-red-50 border-red-200">
          <p className="text-red-700">{data.error || 'No weather data available'}</p>
        </div>
      );
    }

    const getWeatherIcon = (condition) => {
      const lower = condition?.toLowerCase() || '';
      if (lower.includes('rain') || lower.includes('shower')) {
        return <CloudRain className="h-8 w-8 text-blue-500" />;
      } else if (lower.includes('cloud')) {
        return <Cloud className="h-8 w-8 text-gray-500" />;
      } else if (lower.includes('sun') || lower.includes('clear')) {
        return <Sun className="h-8 w-8 text-yellow-500" />;
      } else {
        return <Cloud className="h-8 w-8 text-gray-500" />;
      }
    };

    const formatTemperature = (temp) => {
      if (typeof temp === 'number') {
        return `${Math.round(temp)}°C`;
      }
      return temp;
    };

    const formatSpeed = (speed) => {
      if (typeof speed === 'number') {
        return `${Math.round(speed)} km/h`;
      }
      return speed;
    };

    const formatDistance = (distance) => {
      if (typeof distance === 'number') {
        return distance >= 1000 ? `${(distance / 1000).toFixed(1)} km` : `${Math.round(distance)} m`;
      }
      return distance;
    };

    const formatPressure = (pressure) => {
      if (typeof pressure === 'number') {
        return `${Math.round(pressure)} hPa`;
      }
      return pressure;
    };

    const formatHumidity = (humidity) => {
      if (typeof humidity === 'number') {
        return `${Math.round(humidity)}%`;
      }
      return humidity;
    };

    return (
      <div className="bg-gradient-to-br from-blue-50 to-indigo-100 rounded-xl p-6 border border-blue-200 shadow-lg">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Main Weather Info */}
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-2xl font-bold text-gray-800">
                  {data.location || 'Current Location'}
                </h3>
                <p className="text-sm text-gray-600">
                  {data.coordinates ? `${data.coordinates.lat}, ${data.coordinates.lon}` : 'Weather Data'}
                </p>
              </div>
              {getWeatherIcon(data.condition || data.weather?.main)}
            </div>

            <div className="bg-white bg-opacity-70 rounded-lg p-4">
              <div className="flex items-center justify-between mb-2">
                <span className="text-4xl font-bold text-gray-800">
                  {formatTemperature(data.temperature || data.main?.temp)}
                </span>
                <div className="text-right">
                  <p className="text-lg font-medium text-gray-700 capitalize">
                    {data.condition || data.weather?.[0]?.description || 'N/A'}
                  </p>
                  <p className="text-sm text-gray-500">
                    Feels like {formatTemperature(data.feels_like || data.main?.feels_like)}
                  </p>
                </div>
              </div>
              
              {(data.temp_min || data.temp_max || data.main?.temp_min || data.main?.temp_max) && (
                <div className="flex justify-between text-sm text-gray-600">
                  <span>Low: {formatTemperature(data.temp_min || data.main?.temp_min)}</span>
                  <span>High: {formatTemperature(data.temp_max || data.main?.temp_max)}</span>
                </div>
              )}
            </div>
          </div>

          {/* Detailed Info Grid */}
          <div className="grid grid-cols-2 gap-4">
            {(data.wind_speed || data.wind?.speed) && (
              <div className="bg-white bg-opacity-70 rounded-lg p-4">
                <div className="flex items-center space-x-2 mb-2">
                  <Wind className="h-5 w-5 text-blue-600" />
                  <span className="font-medium text-gray-700">Wind</span>
                </div>
                <p className="text-lg font-semibold">
                  {formatSpeed(data.wind_speed || data.wind?.speed)}
                </p>
                {(data.wind_direction || data.wind?.deg) && (
                  <p className="text-sm text-gray-600">
                    {data.wind_direction || `${data.wind.deg}°`}
                  </p>
                )}
              </div>
            )}

            {(data.humidity || data.main?.humidity) && (
              <div className="bg-white bg-opacity-70 rounded-lg p-4">
                <div className="flex items-center space-x-2 mb-2">
                  <Droplets className="h-5 w-5 text-blue-600" />
                  <span className="font-medium text-gray-700">Humidity</span>
                </div>
                <p className="text-lg font-semibold">
                  {formatHumidity(data.humidity || data.main?.humidity)}
                </p>
              </div>
            )}

            {(data.visibility || data.visibility !== undefined) && (
              <div className="bg-white bg-opacity-70 rounded-lg p-4">
                <div className="flex items-center space-x-2 mb-2">
                  <Eye className="h-5 w-5 text-blue-600" />
                  <span className="font-medium text-gray-700">Visibility</span>
                </div>
                <p className="text-lg font-semibold">
                  {formatDistance(data.visibility)}
                </p>
              </div>
            )}

            {(data.pressure || data.main?.pressure) && (
              <div className="bg-white bg-opacity-70 rounded-lg p-4">
                <div className="flex items-center space-x-2 mb-2">
                  <Gauge className="h-5 w-5 text-blue-600" />
                  <span className="font-medium text-gray-700">Pressure</span>
                </div>
                <p className="text-lg font-semibold">
                  {formatPressure(data.pressure || data.main?.pressure)}
                </p>
              </div>
            )}
          </div>
        </div>

        {/* Maritime Specific Info */}
        {(data.sea_conditions || data.wave_height || data.sea_temperature) && (
          <div className="mt-6 pt-6 border-t border-blue-200">
            <h4 className="font-semibold text-gray-800 mb-4 flex items-center space-x-2">
              <span>🌊</span>
              <span>Maritime Conditions</span>
            </h4>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              {data.sea_conditions && (
                <div className="bg-white bg-opacity-70 rounded-lg p-3">
                  <p className="text-sm text-gray-600 mb-1">Sea Conditions</p>
                  <p className="font-medium">{data.sea_conditions}</p>
                </div>
              )}
              {data.wave_height && (
                <div className="bg-white bg-opacity-70 rounded-lg p-3">
                  <p className="text-sm text-gray-600 mb-1">Wave Height</p>
                  <p className="font-medium">{data.wave_height}</p>
                </div>
              )}
              {data.sea_temperature && (
                <div className="bg-white bg-opacity-70 rounded-lg p-3">
                  <p className="text-sm text-gray-600 mb-1">Sea Temperature</p>
                  <p className="font-medium">{formatTemperature(data.sea_temperature)}</p>
                </div>
              )}
            </div>
          </div>
        )}

        {/* Timestamp */}
        {data.timestamp && (
          <div className="mt-4 pt-4 border-t border-blue-200 text-center">
            <p className="text-sm text-gray-600">
              Last updated: {new Date(data.timestamp).toLocaleString()}
            </p>
          </div>
        )}
      </div>
    );
  }

  // If no data, render as clickable port card
  if (!port) return null;

  return (
    <button
      onClick={() => onWeatherQuery(port.lat, port.lon, port.name)}
      disabled={loading}
      className="w-full p-4 border border-slate-200 rounded-lg hover:border-sky-300 hover:bg-sky-50 transition-all duration-200 text-left disabled:opacity-50 disabled:cursor-not-allowed"
    >
      <div className="flex items-center justify-between mb-2">
        <div className="flex items-center space-x-2">
          <span className="text-lg">{port.flag}</span>
          <div>
            <h4 className="font-medium text-slate-800">{port.name}</h4>
            <p className="text-sm text-slate-600">{port.lat}, {port.lon}</p>
          </div>
        </div>
        <MapPin className="h-5 w-5 text-sky-600" />
      </div>
      <div className="text-center text-sm text-sky-600 font-medium">
        {loading ? 'Loading...' : 'Get Weather'}
      </div>
    </button>
  );
}

export default WeatherCard;
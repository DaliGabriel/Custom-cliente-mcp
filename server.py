from mcp.server.fastmcp import FastMCP
import httpx

# Initialize FastMCP server
mcp = FastMCP("weather")
@mcp.tool()

async def get_weather(latitude: float, longitude: float) -> str:
    """
    Get current weather for a location.
    Args:
        latitude: Location latitude (e.g., 40.7128 for New York)
        longitude: Location longitude (e.g., -74.0060 for New York)
    """
    try:
        # Get forecast URL for the coordinates
        points_url = f"https://api.weather.gov/points/{latitude},{longitude}"
        async with httpx.AsyncClient() as client:
            points = await client.get(points_url, headers={"User-Agent": "MyWeatherApp"})
            forecast_url = points.json()["properties"]["forecast"]
            
            # Get forecast data
            forecast = await client.get(forecast_url)
            current = forecast.json()["properties"]["periods"][0]
            
            return (
                f"Temperature: {current['temperature']}°{current['temperatureUnit']}\n"
                f"Wind: {current['windSpeed']} from {current['windDirection']}\n"
                f"Forecast: {current['shortForecast']}"
            )
    except Exception as e:
        return f"Couldn't get weather: {str(e)}"


if __name__ == "__main__":
    mcp.run(transport='stdio')
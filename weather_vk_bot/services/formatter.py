"""Форматирование погодных данных для красивого отображения."""


def format_current_weather(data: dict, extended: bool = False) -> str:
    """Форматирует текущую погоду."""
    name = data.get("name", "Неизвестный город")
    sys = data.get("sys", {})
    country = sys.get("country", "")
    country_str = f" ({country})" if country else ""
    
    main = data.get("main", {})
    weather = data.get("weather", [{}])[0]
    wind = data.get("wind", {})
    visibility = data.get("visibility", 0)
    
    temp = main.get("temp", 0)
    feels_like = main.get("feels_like", temp)
    humidity = main.get("humidity", 0)
    pressure = main.get("pressure", 0)
    temp_min = main.get("temp_min", temp)
    temp_max = main.get("temp_max", temp)
    
    weather_desc = weather.get("description", "нет данных").capitalize()
    wind_speed = wind.get("speed", 0)
    wind_deg = wind.get("deg", 0)
    
    visibility_km = visibility / 1000 if visibility else 0
    
    # Определение направления ветра
    wind_dirs = ["С", "СВ", "В", "ЮВ", "Ю", "ЮЗ", "З", "СЗ"]
    wind_dir = wind_dirs[int(wind_deg / 45) % 8]
    
    # Преобразование давления из гПа в мм рт. ст.
    pressure_mmhg = round(pressure * 0.750062)
    
    lines = [
        f"{'─' * 30}",
        f"🌍 Город: {name}{country_str}",
        f"🌤 Погода: {weather_desc}",
        f"🌡 Температура: {temp:+.0f}°C",
        f"   Ощущается как: {feels_like:+.0f}°C",
        f"📊 Мин: {temp_min:+.0f}°C  /  Макс: {temp_max:+.0f}°C",
        f"💧 Влажность: {humidity}%",
        f"🌬 Давление: {pressure_mmhg} мм рт.ст.",
        f"💨 Ветер: {wind_speed} м/с ({wind_dir})",
    ]
    
    if visibility_km > 0:
        lines.append(f"👁 Видимость: {visibility_km:.1f} км")
    
    if extended:
        # Расширенная информация — данные о качестве воздуха
        try:
            from OpenWeatherAPI import OpenWeatherAPI
            coords = data.get("coord", {})
            air_data = OpenWeatherAPI.get_air_quality(coords.get("lat"), coords.get("lon"))
            lines.append(f"{'─' * 30}")
            lines.append(f"🌫 Воздух: {_aqi_description(air_data.get('main', {}).get('aqi', 0))}")
            
            components = air_data.get("components", {})
            pm25 = components.get("pm2_5", 0)
            pm10 = components.get("pm10", 0)
            o3 = components.get("o3", 0)
            
            lines.append(f"📊 PM2.5: {pm25:.1f} мкг/м³")
            lines.append(f"📊 PM10: {pm10:.1f} мкг/м³")
            lines.append(f"📊 O₃: {o3:.1f} мкг/м³")
            
            lines.append(f"💬 {_air_analysis(pm25, pm10, o3)}")
        except Exception:
            pass
    
    lines.append(f"{'─' * 30}")
    return "\n".join(lines)


def format_forecast(data: dict) -> str:
    """Форматирует прогноз на 5 дней."""
    name = data.get("city", {}).get("name", "Неизвестный город")
    country = data.get("city", {}).get("country", "")
    country_str = f" ({country})" if country else ""
    
    # Агрегация прогноза по дням
    daily = _aggregate_daily(data.get("list", []))
    
    lines = [
        f"{'─' * 30}",
        f"📅 Прогноз для {name}{country_str}",
        f"{'─' * 30}",
    ]
    
    for i, day_data in enumerate(daily):
        date_str = day_data["date"]
        if i == 0:
            date_str = "📌 Сегодня"
        elif i == 1:
            date_str = "📌 Завтра"
        
        temp_day = day_data["temp_day"]
        temp_min = day_data["temp_min"]
        temp_max = day_data["temp_max"]
        humidity = day_data["humidity"]
        wind = day_data["wind"]
        desc = day_data["desc"].capitalize()
        
        # Эмодзи по погоде
        weather_emoji = _get_weather_emoji(desc)
        
        lines.append(f"\n{date_str}")
        lines.append(f"   🌡 {temp_day:+.0f}°C  (мин: {temp_min:+.0f}°C, макс: {temp_max:+.0f}°C)")
        lines.append(f"   {weather_emoji} {desc}")
        lines.append(f"   💧 Влажность: {humidity:.0f}%  |  💨 Ветер: {wind:.1f} м/с")
    
    lines.append(f"\n{'─' * 30}")
    return "\n".join(lines)


def _aggregate_daily(forecast_list: list) -> list:
    """Агрегирует прогноз по дням (каждые 3 часа → 1 день)."""
    days = {}
    
    for item in forecast_list:
        # Извлекаем дату без времени
        dt = item.get("dt_txt", "")
        date_key = dt.split(" ")[0]  # "YYYY-MM-DD"
        
        if date_key not in days:
            days[date_key] = {
                "date": date_key,
                "temps": [],
                "min_temps": [],
                "max_temps": [],
                "humidities": [],
                "winds": [],
                "desc": "",
                "count": 0,
            }
        
        day = days[date_key]
        main = item.get("main", {})
        wind = item.get("wind", {})
        weather = item.get("weather", [{}])[0]
        
        temp = main.get("temp", 0)
        day["temps"].append(temp)
        day["min_temps"].append(main.get("temp_min", temp))
        day["max_temps"].append(main.get("temp_max", temp))
        day["humidities"].append(main.get("humidity", 0))
        day["winds"].append(wind.get("speed", 0))
        day["desc"] = weather.get("description", "ясно")
        day["count"] += 1
    
    # Формируем итоговый список
    result = []
    for date_key in sorted(days.keys()):
        d = days[date_key]
        result.append({
            "date": d["date"],
            "temp_day": sum(d["temps"]) / len(d["temps"]),
            "temp_min": min(d["min_temps"]),
            "temp_max": max(d["max_temps"]),
            "humidity": sum(d["humidities"]) / len(d["humidities"]),
            "wind": sum(d["winds"]) / len(d["winds"]),
            "desc": d["desc"],
        })
    
    return result


def _aqi_description(aqi: int) -> str:
    """Описание качества воздуха по AQI."""
    descriptions = {
        1: "Отличное 🟢",
        2: "Хорошее 🟡",
        3: "Умеренное 🟠",
        4: "Плохое 🔴",
        5: "Очень плохое ⚫️",
    }
    return descriptions.get(aqi, "Нет данных")


def _air_analysis(pm25: float, pm10: float, o3: float) -> str:
    """Анализ качества воздуха."""
    if pm25 < 12 and pm10 < 50 and o3 < 100:
        return "Качество воздуха хорошее ✅"
    elif pm25 < 35 and pm10 < 100 and o3 < 160:
        if pm25 > 12:
            return "PM2.5 слегка повышен, чувствительным группам стоит сократить прогулки у дорог."
        return "Умеренное качество воздуха, в целом безопасно."
    else:
        return "Загрязнение выше нормы. Рекомендуется ограничить время на улице 🏠"


def _get_weather_emoji(desc: str) -> str:
    """Эмодзи для описания погоды."""
    desc_lower = desc.lower()
    if "ясно" in desc_lower or "sky" in desc_lower:
        return "☀️"
    elif "обл" in desc_lower or "cloud" in desc_lower:
        return "☁️"
    elif "дождь" in desc_lower or "rain" in desc_lower:
        return "🌧"
    elif "град" in desc_lower or "drizzle" in desc_lower:
        return "🌦"
    elif "гроза" in desc_lower or "thunder" in desc_lower:
        return "⛈"
    elif "снег" in desc_lower or "snow" in desc_lower:
        return "❄️"
    elif "туман" in desc_lower or "mist" in desc_lower or "fog" in desc_lower:
        return "🌫"
    elif "небольш" in desc_lower or "light" in desc_lower:
        return "🌦"
    else:
        return "🌤"

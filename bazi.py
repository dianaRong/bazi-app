from datetime import datetime, timedelta
import math

from lunar_python import Solar
from geopy.geocoders import Nominatim
from geopy.adapters import RequestsAdapter


_geolocator = Nominatim(user_agent="bazi-app", adapter_factory=RequestsAdapter, timeout=15)


def get_longitude(city: str) -> float:
    location = _geolocator.geocode(city, timeout=15)
    if location is None:
        raise ValueError(f"找不到城市：{city}")
    return location.longitude


def equation_of_time_minutes(dt: datetime) -> float:
    n = dt.timetuple().tm_yday
    b = math.radians((360 / 365) * (n - 81))
    return 9.87 * math.sin(2 * b) - 7.53 * math.cos(b) - 1.5 * math.sin(b)


def true_solar_time(y, m, d, hour, minute, longitude, standard_meridian=120):
    clock_dt = datetime(y, m, d, hour, minute)
    longitude_correction = 4 * (longitude - standard_meridian)
    eot_correction = equation_of_time_minutes(clock_dt)
    total_correction = longitude_correction + eot_correction
    return clock_dt + timedelta(minutes=total_correction)


def get_bazi(y, m, d, hour, minute, gender, city):
    longitude = get_longitude(city)
    true_dt = true_solar_time(y, m, d, hour, minute, longitude)

    solar = Solar.fromYmdHms(
        true_dt.year, true_dt.month, true_dt.day,
        true_dt.hour, true_dt.minute, 0
    )
    ec = solar.getLunar().getEightChar()
    gender_code = 1 if gender == "男" else 0
    yun = ec.getYun(gender_code)

    return {
        "四柱": [ec.getYear(), ec.getMonth(), ec.getDay(), ec.getTime()],
        "日主": ec.getDayGan(),
        "五行": [ec.getYearWuXing(), ec.getMonthWuXing(),
                ec.getDayWuXing(), ec.getTimeWuXing()],
        "天干十神": [ec.getYearShiShenGan(), ec.getMonthShiShenGan(),
                  ec.getDayShiShenGan(), ec.getTimeShiShenGan()],
        "地支十神": [ec.getYearShiShenZhi(), ec.getMonthShiShenZhi(),
                  ec.getDayShiShenZhi(), ec.getTimeShiShenZhi()],
        "藏干": [ec.getYearHideGan(), ec.getMonthHideGan(),
               ec.getDayHideGan(), ec.getTimeHideGan()],
        "大运": [f"{yun_item.getStartYear()}年起 {yun_item.getGanZhi()}"
                for yun_item in yun.getDaYun()[:6]],
    }

import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()
_llm_client = Groq(api_key=os.getenv("GROQ_API_KEY"))

with open("ditiansui.txt", encoding="utf-8") as f:
    DITIANSUI_TEXT = f.read()

def interpret_bazi(bazi_data: dict) -> str:
    prompt = f"""你是一位精通子平法的命理师。以下是排好的八字命盘，
请根据数据分析日主强弱、天干地支关系，五行喜忌，并就性格、事业、感情给出详细解读。
只根据提供的数据分析，参考ditiansui.txt里面的内容。不要自行推算干支或编造数据中没有的信息。
不要预测死亡、重大疾病或具体医疗结果。

四柱：{bazi_data['四柱']}
日主：{bazi_data['日主']}
五行：{bazi_data['五行']}
天干十神：{bazi_data['天干十神']}
地支十神：{bazi_data['地支十神']}
藏干：{bazi_data['藏干']}
大运：{bazi_data['大运']}
"""
    response = _llm_client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
    )
    return response.choices[0].message.content

if __name__ == "__main__":
    result = get_bazi(2007, 8, 15, 21, 10, "女", city="Shenzhen")
    for key, value in result.items():
        print(key, ":", value)
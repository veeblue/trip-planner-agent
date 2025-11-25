export interface Location {
  longitude: number; // 经度
  latitude: number;  // 纬度
}

export interface Attraction {
  name: string;                // 景点名称
  address: string;             // 地址
  location: Location;          // 经纬度
  visit_duration: number;      // 建议游览时间(分钟)
  description: string;         // 景点描述
  category?: string;           // 景点类别
  rating?: number | null;      // 评分
  image_url?: string | null;   // 图片URL
  ticket_price: number;        // 门票价格(元)
}

export interface Meal {
  type: string;                 // breakfast / lunch / dinner / snack
  name: string;                 // 餐饮名称
  address?: string | null;      // 地址
  location?: Location | null;   // 经纬度
  description?: string | null;  // 描述
  estimated_cost: number;       // 预估费用(元)
}

export interface Hotel {
  name: string;                 // 酒店名称
  address: string;              // 酒店地址
  location?: Location | null;   // 酒店位置
  price_range: string;          // 价格范围
  rating: string;               // 评分
  distance: string;             // 距离景点距离
  type: string;                 // 酒店类型
  estimated_cost: number;       // 预估费用(元/晚)
}

export interface Budget {
  total_attractions: number;       // 景点门票总费用
  total_hotels: number;            // 酒店总费用
  total_meals: number;             // 餐饮总费用
  total_transportation: number;    // 交通总费用
  total: number;                   // 总费用
}

export interface DayPlan {
  date: string;                 // 日期
  day_index: number;            // 第几天(从0开始)
  description: string;          // 行程描述
  transportation: string;       // 交通方式
  accommodation: string;        // 住宿安排
  hotel?: Hotel | null;         // 酒店信息
  attractions: Attraction[];    // 景点列表
  meals: Meal[];                // 餐饮安排
}

export interface WeatherInfo {
  date: string;             // 日期
  day_weather: string;      // 白天天气
  night_weather: string;    // 夜间天气
  day_temp: number;         // 白天温度
  night_temp: number;       // 夜间温度
  wind_direction: string;   // 风向
  wind_power: string;       // 风力
}

export interface TripPlan {
  city: string;                // 目的地城市
  start_date: string;          // 开始日期
  end_date: string;            // 结束日期
  days: DayPlan[];             // 每日行程
  weather_info: WeatherInfo[]; // 天气信息
  overall_suggestions: string; // 总体建议
  budget?: Budget | null;      // 预算信息
}
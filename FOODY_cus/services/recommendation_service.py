from typing import Optional
import os
import getpass
from google import genai
from services.weather_service import WeatherService


os.environ["GOOGLE_API_KEY"] = "AIzaSyCI9Fzm4AEv3zPtzr5SVp1xmyOcfr1t830"


class RecommendationService:
    def __init__(self, api_key=None):
        # Use environment variable if api_key not provided
        self.api_key = api_key or os.environ.get("GOOGLE_API_KEY")
        if not self.api_key:
            self.api_key = getpass.getpass("Enter your Google API key: ")
        self.weather_service = WeatherService()
        self.client = genai.Client(api_key=self.api_key)
        self.model = self.client.chats.create(
            model="gemini-2.0-flash",
        )
        
    def get_weather_recommendations(self, menu_items, location : Optional[str] = None):
        """Get food recommendations based on current weather"""
        # Get current weather
        weather_data = self.weather_service.get_current_weather()
        
        # Format menu items for the prompt
        menu_items_str = "\n".join([f"- {item}" for item in menu_items])
        
        # Create prompt


        prompt = f"""
Dựa trên điều kiện thời tiết hiện tại: {weather_data['weather_description']}, 
nhiệt độ: {weather_data['temperature']}°C, 
độ ẩm: {weather_data['humidity']}%, và thời điểm trong ngày: {weather_data['time_of_day']},
hãy đề xuất 3-5 món ăn từ thực đơn của chúng ta kèm theo số lượng phù hợp. 

Đối với mỗi món, hãy giải thích tại sao nó phù hợp với thời tiết hiện tại và mang lại lợi ích gì.
Hãy làm cho lời giải thích của bạn hấp dẫn và cung cấp thông tin đầy đủ. 

Thực đơn các món có sẵn: 
{menu_items_str} 

Định dạng phản hồi như sau: 

    [Tên sản phẩm] - [Số lượng đề xuất]
    [Giải thích lý do vì sao món này phù hợp với thời tiết hiện tại] 

    [Tên sản phẩm] - [Số lượng đề xuất]
    [Giải thích lý do vì sao món này phù hợp với thời tiết hiện tại] 
     

... và tiếp tục theo thứ tự như vậy. 

Cuối cùng, hãy đưa ra phần tóm tắt ngắn gọn về thời tiết hiện tại và cách các món được đề xuất phù hợp với nó.
""" 
        
        try:
            response = self.model.send_message(prompt)
            return {
                'weather_data': weather_data,
                'recommendations': response.text,
                'success': True
            }
        except ValueError as e:
            print(f"Error generating recommendations: {e}")
            return {
                'weather_data': weather_data,
                'recommendations': "Sorry, I couldn't generate recommendations at this time.",
                'success': False,
                'error': str(e)
            } 
import sys
import os
from dotenv import load_dotenv

import requests
from PyQt5.QtWidgets import (QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QApplication)
from PyQt5.QtCore import Qt

# Load environment variables from .env file
load_dotenv()


class WeatherApp(QWidget):
    def __init__(self):
        super().__init__()
        self.city_label = QLabel("Enter city name: ", self)
        self.city_input = QLineEdit(self)
        self.get_weather_button = QPushButton("Get Weather", self)
        self.temperature_label = QLabel(self)
        self.emoji_label = QLabel(self)
        self.description_label = QLabel(self)
        self.toggle_button = QPushButton("Switch to °F", self)
        self.current_unit = "C"  # Track current unit
        self.current_temp_c = None  # Store current celsius temp
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Weather App")
        self.setFixedSize(400, 500)

        vbox = QVBoxLayout()

        vbox.addWidget(self.city_label)
        vbox.addWidget(self.city_input)
        vbox.addWidget(self.get_weather_button)
        vbox.addWidget(self.emoji_label)
        vbox.addWidget(self.temperature_label)
        vbox.addWidget(self.description_label)
        vbox.addWidget(self.toggle_button)
        self.setLayout(vbox)

        self.city_label.setAlignment(Qt.AlignCenter)
        self.city_input.setAlignment(Qt.AlignCenter)
        self.emoji_label.setAlignment(Qt.AlignCenter)
        self.temperature_label.setAlignment(Qt.AlignCenter)
        self.description_label.setAlignment(Qt.AlignCenter)

        self.city_label.setObjectName("city_label")
        self.city_input.setObjectName("city_input")
        self.get_weather_button.setObjectName("get_weather_button")
        self.emoji_label.setObjectName("emoji_label")
        self.temperature_label.setObjectName("temperature_label")
        self.description_label.setObjectName("description_label")
        self.toggle_button.setObjectName("toggle_button")

        # Hide toggle button until weather is displayed
        self.toggle_button.setVisible(False)

        self.setStyleSheet("""
            QLabel, QPushButton {
                font-family: Arial;
            }
            QLabel#city_label {
                font-size: 30px;
                font-style: italic;
            }
            QLineEdit#city_input {
                font-size: 20px;
                font-weight: bold;
                border-style: dashed;
                border-color: rgb(0, 0, 0);
                background-color: rgb(0, 0, 0);
                color: rgb(255, 255, 255);
            }
            QPushButton#get_weather_button {
                font-size: 30px;
            }
            QLabel#temperature_label {
                font-size: 35px;
            }
            QLabel#emoji_label {
                font-size: 100px;
                font-family: Apple Color Emoji;
            }
            QLabel#description_label {
                font-size: 30px;
            }
            QPushButton#toggle_button {
                font-size: 18px;
            }
        """)

        self.get_weather_button.clicked.connect(self.get_weather)
        self.toggle_button.clicked.connect(self.toggle_unit)

    def get_weather(self):
        # Guard: check if input is empty
        city = self.city_input.text().strip()
        if not city:
            self.display_error("Please enter a city name")
            return

        api_key = os.getenv("API_KEY")
        if not api_key:
            self.display_error("API key not found in .env file")
            return

        url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}"

        # Disable button while loading
        self.get_weather_button.setEnabled(False)
        self.get_weather_button.setText("Loading...")

        try:
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()
            if data["cod"] == 200:
                self.display_weather(data)

        except requests.exceptions.HTTPError:
            match response.status_code:
                case 400:
                    self.display_error("Bad Request: Check city name")
                case 401:
                    self.display_error("Unauthorized: Invalid API key")
                case 403:
                    self.display_error("Forbidden: Access denied")
                case 404:
                    self.display_error("City not found")
                case 500:
                    self.display_error("Server Error: Try again later")
                case 502:
                    self.display_error("Bad Gateway")
                case 503:
                    self.display_error("Service Unavailable")
                case 504:
                    self.display_error("Gateway Timeout")
                case _:
                    self.display_error("HTTP Error occurred")
        except requests.exceptions.ConnectionError:
            self.display_error("Connection Error: Check your internet")
        except requests.exceptions.Timeout:
            self.display_error("Timeout Error: Try again")
        except requests.exceptions.TooManyRedirects:
            self.display_error("Too Many Redirects")
        except requests.exceptions.RequestException as req_error:
            self.display_error(f"Request Error: {req_error}")
        finally:
            # Re-enable button after request finishes
            self.get_weather_button.setEnabled(True)
            self.get_weather_button.setText("Get Weather")

    def display_error(self, message):
        self.temperature_label.setStyleSheet("font-size: 30px;")
        self.temperature_label.setText(message)
        self.emoji_label.clear()
        self.description_label.clear()
        self.toggle_button.setVisible(False)
        self.current_temp_c = None

    def display_weather(self, data):
        temperature_k = data["main"]["temp"]
        temperature_c = temperature_k - 273.15

        self.current_temp_c = temperature_c  # Save for unit toggle
        self.current_unit = "C"
        self.toggle_button.setText("Switch to °F")

        weather_id = data["weather"][0]["id"]
        weather_description = data["weather"][0]["description"]

        self.description_label.setText(weather_description)
        self.temperature_label.setText(f"{temperature_c:.2f}°C")
        self.emoji_label.setText(self.get_weather_emoji(weather_id))
        self.toggle_button.setVisible(True)

    def toggle_unit(self):
        if self.current_temp_c is None:
            return

        if self.current_unit == "C":
            temperature_f = self.current_temp_c * 1.8 + 32
            self.temperature_label.setText(f"{temperature_f:.2f}°F")
            self.toggle_button.setText("Switch to °C")
            self.current_unit = "F"
        else:
            self.temperature_label.setText(f"{self.current_temp_c:.2f}°C")
            self.toggle_button.setText("Switch to °F")
            self.current_unit = "C"

    @staticmethod
    def get_weather_emoji(weather_id):
        if 200 <= weather_id <= 299:
            return "⛈️"
        elif 300 <= weather_id <= 321:
            return "🌦️"
        elif 500 <= weather_id <= 531:
            return "🌧️"
        elif 600 <= weather_id <= 622:
            return "❄️"
        elif 700 <= weather_id <= 743:
            return "🌫️"
        elif weather_id == 762:
            return "🌋"
        elif weather_id == 771:
            return "💨"
        elif weather_id == 781:
            return "🌪️"
        elif weather_id == 800:
            return "☀️"
        elif 801 <= weather_id <= 804:
            return "☁️"
        else:
            return ""


if __name__ == "__main__":
    app = QApplication(sys.argv)
    weather_app = WeatherApp()
    weather_app.show()
    sys.exit(app.exec_())
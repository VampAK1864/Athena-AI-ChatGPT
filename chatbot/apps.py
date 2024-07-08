from django.apps import AppConfig


class ChatbotConfig(AppConfig): # Create a new class called ChatbotConfig that inherits from AppConfig.
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'chatbot'

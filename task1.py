import argparse
import asyncio
import logging
import os
from aiopath import AsyncPath
from aioshutil import copyfile
from colorama import init, Fore, Style

# Ініціалізація Colorama
init(autoreset=True)

# Налаштування логування
logging.basicConfig(
    filename="task1.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

# Функція для очищення консолі перед запуском
def clear_console():
    os.system("cls" if os.name == "nt" else "clear")


# Функція для запиту параметрів за замовчуванням
def prompt_for_defaults():
    print(Fore.CYAN + "Бажаєте використовувати стандартні шляхи? (y/n)")
    choice = input().strip().lower()
    if choice == "y":
        return "unsorted files", "output folder"
    elif choice == "n":
        print(Fore.YELLOW + "Приклад використання:")
        print(
            Fore.YELLOW
            + "python task1.py --source /path/to/source --output /path/to/output"
        )
        exit()
    else:
        print(Fore.RED + "Невірний вибір. Завершення програми.")
        exit()


# Створення парсера аргументів
ArgumentParser = argparse.ArgumentParser(description="Файловий сортувальник")
ArgumentParser.add_argument("--source", "-s", help="Шлях до вихідної папки")
ArgumentParser.add_argument("--output", "-o", help="Шлях до папки призначення")
args = vars(ArgumentParser.parse_args())

if not args["source"]:
    args["source"], args["output"] = prompt_for_defaults()

if not args["output"]:
    args["output"] = "output folder"

source = AsyncPath(args["source"])
destination = AsyncPath(args["output"])

sorted_files = []


async def read_folder(path: AsyncPath):
    """Рекурсивно переглядає вміст папки та викликає сортування файлів."""
    if os.path.exists(path):
        async for item in path.iterdir():
            if await item.is_dir():
                await read_folder(item)
            else:
                await copy_file(item)
    else:
        print(Fore.RED + f"[!] Папка {path} не існує. " "Немає файлів для копіювання")
        logging.warning(f"Папка {path} не існує")


async def copy_file(file: AsyncPath):
    """Копіює файл у відповідну папку на основі його розширення."""
    folder = destination / file.suffix[1:]
    new_file = file
    if folder / file.name in sorted_files:
        base_name = file.stem
        new_file = AsyncPath(f"{base_name}_" + file.suffix)
    try:
        await folder.mkdir(exist_ok=True, parents=True)
        sorted_files.append(folder / file.name)
        await copyfile(file, folder / new_file.name)
        print(Fore.GREEN + f"[+] Файл {file.name} -> {folder}")
        logging.info(f"Файл {file} скопійовано у {folder}")
    except OSError as e:
        logging.error(f"Помилка при копіюванні {file}: {e}")


if __name__ == "__main__":
    clear_console()
    clear_console()

    print(
        Fore.YELLOW + f"[i] Початок сортування файлів у " f"{source} -> {destination}\n"
    )
    logging.info(f"Початок сортування файлів: {source} -> {destination}")

    asyncio.run(read_folder(source))

    print(Fore.YELLOW + f"\n[i] Усі файли з {source} переміщено до {destination}")
    logging.info(f"Сортування завершено: {source} -> {destination}")

import string
import asyncio
import httpx
import logging
import os
from collections import defaultdict, Counter
from matplotlib import pyplot as plt

# Налаштування логування
logging.basicConfig(
    filename="task2.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

# Функція для очищення консолі перед запуском
def clear_console():
    os.system("cls" if os.name == "nt" else "clear")


# Функція для отримання тексту з URL
async def fetch_text(url):
    """Асинхронно отримує текст за вказаною URL-адресою."""
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        if response.status_code == 200:
            logging.info(f"Успішно завантажено текст з {url}")
            return response.text
        else:
            logging.error(
                f"Помилка завантаження тексту з {url}: {response.status_code}"
            )
            return None


# Функція для видалення знаків пунктуації
def clean_text(text):
    """Видаляє всі знаки пунктуації з тексту."""
    return text.translate(str.maketrans("", "", string.punctuation))


# Функція для мапування даних
async def word_mapper(word):
    """Повертає пару (слово, 1) для підрахунку частоти."""
    return word.lower(), 1


# Функція для групування слів
def shuffle_words(mapped_values):
    """Групує слова по ключах."""
    shuffled = defaultdict(list)
    for key, value in mapped_values:
        shuffled[key].append(value)
    return shuffled.items()


# Функція для підрахунку частоти кожного слова
async def count_words(word_group):
    """Підраховує кількість появ слова."""
    word, occurrences = word_group
    return word, sum(occurrences)


# Головна функція обробки MapReduce
async def process_text(url):
    """Завантажує текст, обробляє MapReduce та повертає частоти слів."""
    text = await fetch_text(url)
    if text is None:
        return {}

    text = clean_text(text)
    words = text.split()

    # Виконуємо мапування асинхронно
    mapped_result = await asyncio.gather(*[word_mapper(word) for word in words])

    # Виконуємо групування слів
    shuffled_values = shuffle_words(mapped_result)

    # Виконуємо редукцію асинхронно
    reduced_result = await asyncio.gather(
        *[count_words(group) for group in shuffled_values]
    )

    logging.info("Обробка MapReduce завершена успішно")
    return dict(reduced_result)


# Функція для візуалізації результатів
def visualize_top_words(result, top_n=20):
    """Будує бар-чарт для топ-N найчастіших слів."""
    top_words = Counter(result).most_common(top_n)
    words, counts = zip(*top_words)

    plt.figure(figsize=(12, 8))
    plt.barh(words, counts, color="dodgerblue")
    plt.xlabel("Частота використання", fontsize=14, fontweight="bold", color="darkblue")
    plt.ylabel("Слова", fontsize=14, fontweight="bold", color="darkblue")
    plt.title(
        f"Топ {top_n} найбільш вживаних слів",
        fontsize=16,
        fontweight="bold",
        color="darkred",
    )
    plt.gca().invert_yaxis()
    plt.grid(axis="x", linestyle="--", alpha=0.7)
    plt.show()


if __name__ == "__main__":
    clear_console()
    url = "https://txt2html.sourceforge.net/sample.txt"
    result = asyncio.run(process_text(url))
    print(result)
    visualize_top_words(result)

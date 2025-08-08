from selenium import webdriver
from selenium.webdriver import Keys
from selenium.webdriver.common.by import By
import time


def setup_browser():
    browser = webdriver.Firefox()
    return browser


def search_wikipedia(browser, query):
    browser.get("https://ru.wikipedia.org/wiki/Заглавная_страница")
    search_box = browser.find_element(By.ID, "searchInput")
    search_box.send_keys(query)
    search_box.send_keys(Keys.RETURN)
    time.sleep(2)


def is_search_results_page(browser):
    try:
        h1 = browser.find_element(By.TAG_NAME, "h1")
        return h1.text == "Результаты поиска"
    except:
        return False


def is_disambiguation_page(browser):
    try:
        h1 = browser.find_element(By.TAG_NAME, "h1").text.lower()
        return "значения" in h1 or "неоднозначности" in h1
    except:
        return False


def is_article_page(browser):
    return not is_search_results_page(browser) and not is_disambiguation_page(browser)


def browse_paragraphs(browser):
    if not is_article_page(browser):
        print("\nЭта страница не является статьёй для чтения.")
        return

    paragraphs = browser.find_elements(By.CSS_SELECTOR, ".mw-parser-output p")
    found = False
    for i, paragraph in enumerate(paragraphs, 1):
        text = paragraph.text.strip()
        if text:
            print(f"\n=== Параграф {i} ===")
            print(text)
            input("\nНажмите Enter для продолжения...")
            found = True
    if not found:
        print("\nНе найдено текстового содержания.")
    print("\nКонец статьи.")


def get_links_for_page(browser):
    """Улучшенный поиск ссылок на всех типах страниц"""
    links = []

    # 1. Для страницы результатов поиска
    if is_search_results_page(browser):
        results = browser.find_elements(By.CSS_SELECTOR, ".mw-search-results .mw-search-result-heading a")
        return [(result.text, result.get_attribute("href")) for result in results]

    # 2. Для страницы значений
    if is_disambiguation_page(browser):
        items = browser.find_elements(By.CSS_SELECTOR, "#mw-content-text ul li a, #mw-content-text ol li a")
        return [(item.text, item.get_attribute("href")) for item in items if item.text.strip()]

    # 3. Для обычной статьи - более широкий поиск ссылок
    # Ищем в разделах "См. также", навигационных панелях и основном тексте
    selectors = [
        "#See_also ~ ul a",  # Ссылки в разделе "См. также"
        ".navbox a",  # Навигационные панели
        ".hatnote a",  # Примечания
        ".mw-parser-output a[href^='/wiki/']:not(.new)",  # Основные ссылки в тексте
        ".infobox a"  # Ссылки в инфобоксе
    ]

    seen_links = set()
    for selector in selectors:
        elements = browser.find_elements(By.CSS_SELECTOR, selector)
        for element in elements:
            href = element.get_attribute("href")
            text = element.text.strip()
            if href and text and href not in seen_links:
                links.append((text, href))
                seen_links.add(href)

    return links[:20]  # Ограничиваем количество ссылок для удобства


def show_menu(browser):
    if is_search_results_page(browser):
        print("\nВы находитесь на странице результатов поиска.")
        print("Выберите действие:")
        print("1. Перейти на одну из найденных страниц")
        print("2. Выйти из программы")
        return ["1", "2"]
    elif is_disambiguation_page(browser):
        print("\nВы находитесь на странице значений.")
        print("Выберите действие:")
        print("1. Перейти на одно из значений")
        print("2. Выйти из программы")
        return ["1", "2"]
    else:
        print("\nВы находитесь в статье.")
        print("Выберите действие:")
        print("1. Листать параграфы текущей статьи")
        print("2. Перейти на одну из связанных страниц")
        print("3. Выйти из программы")
        return ["1", "2", "3"]


def main():
    browser = setup_browser()

    query = input("Введите ваш запрос для поиска в Википедии: ")
    search_wikipedia(browser, query)

    while True:
        valid_choices = show_menu(browser)

        choice = input("Ваш выбор: ")

        if choice not in valid_choices:
            print("Неверный ввод. Попробуйте снова.")
            continue

        if choice == "1":
            if is_search_results_page(browser) or is_disambiguation_page(browser):
                links = get_links_for_page(browser)
                if not links:
                    print("Нет доступных статей для перехода.")
                    continue

                print("\nДоступные статьи:")
                for i, (title, _) in enumerate(links, 1):
                    print(f"{i}. {title}")

                link_choice = input("Выберите статью (номер) или 0 для отмены: ")
                if link_choice.isdigit() and 0 < int(link_choice) <= len(links):
                    browser.get(links[int(link_choice) - 1][1])
                    time.sleep(2)
            else:
                browse_paragraphs(browser)

        elif choice == "2" and "2" in valid_choices:
            links = get_links_for_page(browser)
            if not links:
                print("Нет доступных статей для перехода.")
                continue

            print("\nДоступные связанные статьи:")
            for i, (title, _) in enumerate(links, 1):
                print(f"{i}. {title}")

            link_choice = input("Выберите статью (номер) или 0 для отмены: ")
            if link_choice.isdigit() and 0 < int(link_choice) <= len(links):
                browser.get(links[int(link_choice) - 1][1])
                time.sleep(2)

        elif choice == "3":
            break

    browser.quit()
    print("Программа завершена.")


if __name__ == "__main__":
    main()

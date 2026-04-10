import streamlit as st
import json
import os
import segno
import io

# ========================================================
# 1. КОНФИГУРАЦИЯ И СТИЛИ
# ========================================================
st.set_page_config(page_title="ExamFlow | Final Build", layout="wide")

st.markdown("""
    <style>
    .topic-card { 
        padding: 20px; border-radius: 12px; background-color: #f8f9fa; 
        border-left: 5px solid #000; margin-bottom: 20px; box-shadow: 2px 2px 10px rgba(0,0,0,0.1);
    }
    .topic-card h3 { color: #1e1e1e !important; font-size: 18px; margin-bottom: 5px; }
    .topic-card p { color: #444 !important; font-size: 14px; }
    .stButton>button { width: 100%; border-radius: 8px; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

DB_FILE = "examflow_db.json"

# ========================================================
# 2. ПОЛНАЯ БАЗА ДАННЫХ (ВСЕ БЛОКИ)
# ========================================================
def get_initial_db():
    db = {"ОГЭ Информатика": [], "ЕГЭ Информатика": []}

    # ОГЭ (1-16)
    oge_raw = [
        (1, "Кодирование текста", "https://yandex.ru/video/search?text=огэ+информатика+задание+1"),
        (2, "Декодирование (Фано)", "https://yandex.ru/video/search?text=огэ+информатика+задание+2"),
        (3, "Логика", "https://yandex.ru/video/search?text=огэ+информатика+задание+3"),
        (4, "Пути в графах", "https://yandex.ru/video/search?text=огэ+информатика+задание+4"),
        (5, "Исполнитель", "https://yandex.ru/video/search?text=огэ+информатика+задание+5"),
        (6, "Анализ программ", "https://yandex.ru/video/search?text=огэ+информатика+задание+6"),
        (7, "Адресация в сети", "https://yandex.ru/video/search?text=огэ+информатика+задание+7"),
        (8, "Запросы (Круги Эйлера)", "https://yandex.ru/video/search?text=огэ+информатика+задание+8"),
        (9, "Количество путей", "https://yandex.ru/video/search?text=огэ+информатика+задание+9"),
        (10, "Системы счисления", "https://yandex.ru/video/search?text=огэ+информатика+задание+10"),
        (11, "Поиск в файлах", "https://yandex.ru/video/search?text=огэ+информатика+задание+11"),
        (12, "Свойства файлов", "https://yandex.ru/video/search?text=огэ+информатика+задание+12"),
        (13, "Презентация или Текст", "https://fipi.ru/oge/otkrytyy-bank-zadaniy-oge"),
        (14, "Таблицы (Excel)", "https://yandex.ru/video/search?text=огэ+информатика+задание+14"),
        (15, "Робот (Кумир)", "https://www.youtube.com/results?search_query=огэ+информатика+задание+15+робот"),
        (16, "Программирование (Python)", "https://www.youtube.com/results?search_query=огэ+информатика+задание+16+питон")
    ]

    # ЕГЭ (1-27)
    ege_raw = [
        (1, "Графы", "https://kompege.ru/"), (2, "Логика", "https://kompege.ru/"),
        (3, "Базы данных", "https://fipi.ru/"), (4, "Фано", "https://kompege.ru/"),
        (5, "Алгоритмы", "https://yandex.ru/video/search?text=егэ+информатика+задание+5"),
        (6, "Черепаха", "https://yandex.ru/video/search?text=егэ+информатика+задание+6"),
        (7, "Медиа", "https://kompege.ru/"), (8, "Комбинаторика", "https://kompege.ru/"),
        (9, "Excel Таблицы", "https://fipi.ru/"), (10, "Текстовый поиск", "https://fipi.ru/"),
        (11, "Объем памяти", "https://kompege.ru/"), (12, "Редактор", "https://kompege.ru/"),
        (13, "Сети (IP)", "https://yandex.ru/video/search?text=егэ+информатика+задание+13"),
        (14, "Системы счисления", "https://kompege.ru/"), (15, "Логика (Отрезки)", "https://kompege.ru/"),
        (16, "Рекурсия", "https://kompege.ru/"), (17, "Массивы", "https://kompege.ru/"),
        (18, "Робот в Excel", "https://fipi.ru/"), (19, "Теория игр-1", "https://kompege.ru/"),
        (20, "Теория игр-2", "https://kompege.ru/"), (21, "Теория игр-3", "https://kompege.ru/"),
        (22, "Процессы", "https://kompege.ru/"), (23, "Динамика", "https://kompege.ru/"),
        (24, "Строки", "https://kompege.ru/"), (25, "Числа (Маски)", "https://kompege.ru/"),
        (26, "Сортировка", "https://kompege.ru/"), (27, "Анализ данных", "https://kompege.ru/")
    ]

    for n, name, url in oge_raw:
        db["ОГЭ Информатика"].append({"id": f"o{n}", "name": f"{n}. {name}", "url": url, "done": False})
    for n, name, url in ege_raw:
        db["ЕГЭ Информатика"].append({"id": f"e{n}", "name": f"{n}. {name}", "url": url, "done": False})
    return db

# ========================================================
# 3. ФУНКЦИОНАЛЬНЫЕ БЛОКИ (ЛОГИКА)
# ========================================================
def load_data():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r", encoding="utf-8") as f: return json.load(f)
    return get_initial_db()

def save_data():
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(st.session_state.db, f, ensure_ascii=False, indent=4)

if 'db' not in st.session_state:
    st.session_state.db = load_data()

# ========================================================
# 4. ИНТЕРФЕЙС
# ========================================================
st.sidebar.title("🚀 ExamFlow")
st.sidebar.markdown("---")

# Генерация QR (чтобы комиссия зашла на сайт)
qr_url = "https://kirill-myexam.streamlit.app"
qr = segno.make(qr_url)
out = io.BytesIO()
qr.save(out, kind='png', scale=4)
st.sidebar.image(out.getvalue(), caption="QR-код проекта")

subj = st.sidebar.selectbox("Выберите экзамен:", list(st.session_state.db.keys()))
menu = st.sidebar.radio("Навигация:", ["📊 Прогресс", "📖 Обучение", "⚙️ Архитектура"])

current_list = st.session_state.db[subj]

# БЛОК 1: ПРОГРЕСС
if menu == "📊 Прогресс":
    st.title(f"Ваш успех: {subj}")
    done = sum(1 for t in current_list if t["done"])
    total = len(current_list)
    
    col1, col2 = st.columns(2)
    col1.metric("Темы", f"{done} / {total}")
    col2.metric("Готовность", f"{int(done/total*100)}%")
    st.progress(done / total)
    
    st.markdown("### Статус заданий")
    for t in current_list:
        st.write(f"{'✅' if t['done'] else '⬜'} {t['name']}")

# БЛОК 2: ОБУЧЕНИЕ
elif menu == "📖 Обучение":
    st.title("📚 База знаний")
    for t in current_list:
        with st.container():
            st.markdown(f'''
            <div class="topic-card">
                <h3>{t["name"]}</h3>
                <p><a href="{t["url"]}" target="_blank">🔗 Ссылка на видеоразбор или теорию</a></p>
            </div>
            ''', unsafe_allow_html=True)
            # Проверка ключа 'url' теперь безопасна, так как мы обновим базу
            if st.button(f"Выучено: {t['name']}", key=f"btn_{t['id']}"):
                t["done"] = not t["done"]
                save_data(); st.rerun()

# БЛОК 3: АРХИТЕКТУРА И АЛГОРИТМ (Для комиссии)
elif menu == "⚙️ Архитектура":
    st.title("🛠 Техническая реализация")
    st.info("Этот раздел предназначен для демонстрации логики работы приложения комиссии.")
    
    st.subheader("1. Стек технологий")
    st.write("- **Язык:** Python\n- **Интерфейс:** Streamlit\n- **База данных:** JSON (автономное хранение)")
    
    st.subheader("2. Алгоритм сохранения")
    st.code("""
# При нажатии кнопки:
1. Изменяется статус 'done' в st.session_state
2. Вызывается функция save_data()
3. Данные записываются в examflow_db.json
4. Интерфейс перерисовывается (st.rerun)
    """, language="python")

# Очистка (если опять вылезет KeyError)
if st.sidebar.button("⚠️ Сбросить и обновить базу"):
    if os.path.exists(DB_FILE): os.remove(DB_FILE)
    st.session_state.clear()
    st.rerun()

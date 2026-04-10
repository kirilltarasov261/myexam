import streamlit as st
import json
import os
import segno
import io

# ========================================================
# 1. НАСТРОЙКИ И ДИЗАЙН
# ========================================================
st.set_page_config(page_title="ExamFlow | Final Edition", layout="wide")

st.markdown("""
    <style>
    .topic-card { 
        padding: 25px; border-radius: 15px; background-color: #ffffff; 
        border: 2px solid #000; margin-bottom: 25px; box-shadow: 8px 8px 0px #000;
    }
    .topic-card h3, .topic-card p, .topic-card b, .topic-card span, .topic-card div { 
        color: #000000 !important; 
    }
    .stButton>button { background-color: #000; color: #fff; border-radius: 10px; font-weight: bold; }
    .stButton>button:hover { background-color: #333; }
    </style>
    """, unsafe_allow_html=True)

DB_FILE = "examflow_db.json"

# ========================================================
# 2. БАЗА ДАННЫХ С ТЕМАТИЧЕСКИМИ ВОПРОСАМИ
# ========================================================
def get_initial_db():
    db = {"ОГЭ Информатика": [], "ЕГЭ Информатика": []}
    
    oge_names = [
        "Кодирование текста", "Декодирование (Фано)", "Логика", "Пути в графах",
        "Исполнитель", "Анализ программ", "Адресация в сети", "Запросы (Круги Эйлера)",
        "Количество путей", "Системы счисления", "Поиск в файлах", "Маски файлов",
        "Презентация/Текст", "Таблицы (Excel)", "Робот (Кумир)", "Программирование (Python)"
    ]

    # Реальные вопросы для ОГЭ по темам
    oge_qs = {
        1: [{"q": "Сколько бит в 4 байтах?", "a": "32"}, {"q": "Символ весит 16 бит. Сколько байт весит слово из 5 букв?", "a": "10"}],
        2: [{"q": "От дедушки получена шифровка: 01100. Если 0-А, 11-Б, 10-В, то какое слово?", "a": "АБВ"}],
        3: [{"q": "Напишите наименьшее целое X, для которого истинно: (X > 5) И (X четное)", "a": "6"}],
        4: [{"q": "Между А и Б дорога 5 км, Б и В - 3 км. Какова длина пути А-Б-В?", "a": "8"}],
        5: [{"q": "У исполнителя две команды: +1 и *2. Как из 1 получить 4 за два шага?", "a": "*2*2"}],
        6: [{"q": "Программа: if s > 10 or k > 10. Были пуски: (1,1), (11,2), (1,12). Сколько 'YES'?", "a": "2"}],
        7: [{"q": "Доступ к файлу hello.txt на сервере ftp.ru. Что идет первым в адресе?", "a": "ftp"}],
        8: [{"q": "Запрос 'Кошки | Собаки' найдет больше или меньше страниц, чем просто 'Кошки'?", "a": "больше"}],
        9: [{"q": "Сколько путей из А в В, если из А в Б ведет 2 пути, а из Б в В - 3?", "a": "6"}],
        10: [{"q": "Переведите число 12 из десятичной в двоичную:", "a": "1100"}],
        11: [{"q": "В каком меню текстового редактора находится инструмент 'Найти'?", "a": "правка"}],
        12: [{"q": "Какое расширение обычно имеют файлы презентаций?", "a": "pptx"}],
        13: [{"q": "Как называется программа для создания слайдов?", "a": "powerpoint"}],
        14: [{"q": "Каким символом начинается любая формула в Excel?", "a": "="}],
        15: [{"q": "Как называется среда для управления Роботом?", "a": "кумир"}],
        16: [{"q": "Как называется команда вывода в Python?", "a": "print"}]
    }

    ege_names = [
        "Анализ моделей (Графы)", "Таблицы истинности", "Поиск в БД",
        "Условие Фано", "Анализ алгоритмов", "Циклы (Черепаха)", "Звук и фото",
        "Комбинаторика", "Excel", "Текстовый поиск", "Количество информации",
        "Редактор", "IP-адреса", "Системы счисления", "Логические выражения",
        "Рекурсия", "Массивы", "Робот (Динамика)", "Теория игр 1", "Теория игр 2",
        "Теория игр 3", "Процессы", "Количество путей", "Строки", "Маски",
        "Сортировка", "Сложный анализ"
    ]

    # База вопросов для ЕГЭ (те же, что были)
    ege_qs = {
        1: [{"q": "В таблице связи есть, в графе нет. Что делать?", "a": "анализ"}],
        2: [{"q": "Сколько строк в таблице для 3 переменных?", "a": "8"}],
        4: [{"q": "Соблюдается ли условие Фано, если код 0 является началом кода 01?", "a": "нет"}],
        7: [{"q": "Сколько бит на пиксель для 256 цветов?", "a": "8"}],
        13: [{"q": "Сколько бит в одном байте IP-адреса?", "a": "8"}],
        14: [{"q": "Основание системы счисления, где 10 - это 2?", "a": "2"}],
        24: [{"q": "Функция в Python для поиска длины строки?", "a": "len"}]
    }

    # Заполнение ОГЭ
    for i, name in enumerate(oge_names, 1):
        qs = oge_qs.get(i, [{"q": f"Тест ОГЭ {i}: Напиши 'ок'", "a": "ок"}])
        db["ОГЭ Информатика"].append({
            "id": f"o{i}", "name": f"{i}. {name}", "done": False,
            "theory": f"<b>Теория №{i}:</b> Подготовка к ОГЭ по информатике.",
            "yt": f"https://www.youtube.com/results?search_query=Умскул+ОГЭ+задание+{i}",
            "reshu": f"https://inf-oge.sdamgia.ru/search?search=задание+{i}",
            "questions": qs
        })

    # Заполнение ЕГЭ
    for i, name in enumerate(ege_names, 1):
        qs = ege_qs.get(i, [{"q": f"Тест ЕГЭ {i}: Напиши 'готово'", "a": "готово"}])
        db["ЕГЭ Информатика"].append({
            "id": f"e{i}", "name": f"{i}. {name}", "done": False,
            "theory": f"<b>Разбор задания №{i}:</b> Ключевые методы ЕГЭ.",
            "yt": f"https://www.youtube.com/results?search_query=Умскул+ЕГЭ+задание+{i}",
            "reshu": f"https://inf-ege.sdamgia.ru/search?search=задание+{i}",
            "questions": qs
        })
    return db

# --- ЛОГИКА ЗАГРУЗКИ ---
if 'db' not in st.session_state:
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r", encoding="utf-8") as f:
                st.session_state.db = json.load(f)
        except: st.session_state.db = get_initial_db()
    else: st.session_state.db = get_initial_db()

def save():
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(st.session_state.db, f, ensure_ascii=False, indent=4)

# --- ИНТЕРФЕЙС И QR-КОД ---
st.sidebar.title("🚀 ExamFlow")
qr_url = "https://myexam-rpxmihxm3ypamwdczibkkq.streamlit.app/" 
qr = segno.make(qr_url)
out = io.BytesIO()
qr.save(out, kind='png', scale=4)
st.sidebar.image(out.getvalue(), caption="Сканируй для мобильной версии")

subj = st.sidebar.selectbox("Экзамен:", list(st.session_state.db.keys()))
menu = st.sidebar.radio("Навигация:", ["📊 Прогресс", "📖 Обучение", "🧠 Тренажёр", "📅 Планировщик"])

current_list = st.session_state.db[subj]

if menu == "📊 Прогресс":
    st.title(f"Ваш путь: {subj}")
    done = sum(1 for t in current_list if t["done"])
    st.metric("Завершено заданий", f"{done} / {len(current_list)}")
    st.progress(done / len(current_list))
    for t in current_list: st.write(f"{'✅' if t['done'] else '⬜'} {t['name']}")

elif menu == "📖 Обучение":
    st.title("📚 Теория и ресурсы")
    for t in current_list:
        with st.container():
            st.markdown(f'<div class="topic-card"><h3>{t["name"]}</h3><p>{t["theory"]}</p></div>', unsafe_allow_html=True)
            c1, c2, c3 = st.columns(3)
            c1.link_button("📺 Видео", t["yt"], use_container_width=True)
            c2.link_button("📝 Практика", t["reshu"], use_container_width=True)
            if c3.button(f"{'✅' if t['done'] else '⬜'}", key=f"l_{t['id']}", use_container_width=True):
                t["done"] = not t["done"]; save(); st.rerun()

elif menu == "🧠 Тренажёр":
    st.title("⚡ Тематическая тренировка")
    topic_name = st.selectbox("Выберите тему:", [t['name'] for t in current_list])
    target = next(t for t in current_list if t['name'] == topic_name)
    q_key = f"step_{target['id']}"
    if q_key not in st.session_state: st.session_state[q_key] = 0
    idx = st.session_state[q_key]
    
    if idx < len(target['questions']):
        q = target['questions'][idx]
        st.info(f"Вопрос {idx + 1} из {len(target['questions'])}")
        st.subheader(q['q'])
        ans = st.text_input("Ответ:", key=f"a_{target['id']}_{idx}")
        if st.button("Проверить"):
            if ans.strip().lower() == q['a'].lower():
                st.session_state[q_key] += 1; st.success("Верно!"); st.rerun()
            else: st.error("Ошибка!")
    else:
        st.balloons(); st.success("Тема пройдена!"); target["done"] = True; save()
        if st.button("Сброс теста"): st.session_state[q_key] = 0; st.rerun()

elif menu == "📅 Планировщик":
    st.title("🗓 План подготовки")
    todo = [t for t in current_list if not t["done"]]
    site = "Решу ОГЭ" if "ОГЭ" in subj else "Решу ЕГЭ"
    if not todo: st.success("Всё выучено!")
    else:
        for t in todo[:3]:
            with st.expander(f"📌 План: {t['name']}"):
                st.write(f"1. Видео.\n2. Задания на **{site}**.")
                if st.button("Сделано!", key=f"p_{t['id']}"):
                    t["done"] = True; save(); st.rerun()

if st.sidebar.button("🗑 Сброс"):
    if os.path.exists(DB_FILE): os.remove(DB_FILE)
    st.session_state.clear(); st.rerun()

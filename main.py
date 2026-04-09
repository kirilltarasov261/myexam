import streamlit as st
import json
import os
import segno
import io

# ========================================================
# 1. НАСТРОЙКИ И ДИЗАЙН
# ========================================================
st.set_page_config(page_title="ExamFlow | Final Build", layout="wide")

st.markdown("""
    <style>
    .topic-card { 
        padding: 25px; border-radius: 15px; background-color: #ffffff; 
        border: 2px solid #000; margin-bottom: 25px; box-shadow: 8px 8px 0px #000;
    }
    .topic-card h3 { color: #000 !important; font-weight: 900; border-bottom: 2px solid #eee; }
    .topic-card p, .topic-card b { color: #000 !important; }
    .stButton>button { background-color: #000; color: #fff; border-radius: 10px; border: none; }
    .stButton>button:hover { background-color: #444; color: #fff; }
    </style>
    """, unsafe_allow_html=True)

DB_FILE = "examflow_db.json"

# ========================================================
# 2. ПОЛНАЯ БАЗА ДАННЫХ (ОГЭ + ЕГЭ)
# ========================================================
def get_initial_db():
    # Создаем структуру, где ключи - это точные названия для выпадающего списка
    db = {
        "ОГЭ Информатика": [], 
        "ЕГЭ Информатика": []
    }

    # Данные ОГЭ (1-15)
    oge_raw = [
        (1, "Кодирование текста", "I = K * i. 1 байт = 8 бит.", [{"q": "Бит в 2 байтах?", "a": "16"}]*5),
        (2, "Декодирование", "Условие Фано: коды не пересекаются.", [{"q": "А=0, Б=11. Код для В?", "a": "10"}]*5),
        (3, "Логика", "НЕ(>) это (<=). И - оба верны.", [{"q": "Мин X: НЕ(X < 5) И (X четное)", "a": "6"}]*5),
        (4, "Графы", "Кратчайший путь по таблице.", [{"q": "А-Б=2, Б-В=3. Путь А-В?", "a": "5"}]*5),
        (5, "Исполнитель", "Алгоритмы +1, *b.", [{"q": "Из 1 в 10 за (+1, *b). b?", "a": "9"}]*5),
        (6, "Условия", "Анализ If/Else.", [{"q": "s=5, t=10. s>4 and t>9?", "a": "да"}]*5),
        (7, "Сети", "Протокол://Сервер/Файл", [{"q": "Разделитель протокола?", "a": "://"}]*5),
        (8, "Запросы", "N(A|B) = N(A) + N(B) - N(A&B)", [{"q": "А=10, Б=10, А&Б=2. А|Б?", "a": "18"}]*5),
        (9, "Схемы дорог", "Сумма входящих стрелок.", [{"q": "В А=1. В Б из А. Б=?", "a": "1"}]*5),
        (10, "Системы счисления", "Перевод в 10-ю систему.", [{"q": "101(2) в 10-й?", "a": "5"}]*5),
        (11, "Поиск в тексте", "Ctrl+F в документах.", [{"q": "Кнопки поиска?", "a": "ctrl+f"}]*5),
        (12, "Маски файлов", "* - любая строка, ? - 1 знак.", [{"q": "Один любой символ?", "a": "?"}]*5),
        (13, "Документы", "Форматирование текста.", [{"q": "Шрифт в 13.2?", "a": "14"}]*5),
        (14, "Excel таблицы", "СУММЕСЛИ, СЧЁТЕСЛИ.", [{"q": "Среднее значение?", "a": "срзнач"}]*5),
        (15, "Программирование", "Python и циклы.", [{"q": "Цикл с условием?", "a": "while"}]*5)
    ]

    # Данные ЕГЭ (1-27)
    ege_raw = [
        (1, "Графы", "Степени вершин.", [{"q": "Вершина с 1 дорогой?", "a": "тупик"}]*5),
        (2, "Логика", "Таблицы истинности.", [{"q": "Импликация в Python?", "a": "<="}]*5),
        (13, "IP-адреса", "Адрес сети и маска.", [{"q": "Бит в IPv4?", "a": "32"}]*5),
        (14, "Системы", "Степени и остатки.", [{"q": "2**10?", "a": "1024"}]*5),
        (24, "Строки", "Обработка файлов .txt", [{"q": "Открыть файл?", "a": "open"}]*5),
        (27, "Анализ данных", "Эффективные алгоритмы.", [{"q": "Сложность O(N)?", "a": "да"}]*5)
    ]
    # Заполняем остальные задания ЕГЭ для структуры
    for i in range(1, 28):
        if not any(t[0] == i for t in ege_raw):
            ege_raw.append((i, f"Задание {i}", "Теория и методы решения.", [{"q": "Готовы?", "a": "да"}]*5))

    # Формируем итоговые списки
    for n, name, theory, qs in oge_raw:
        db["ОГЭ Информатика"].append({"id": f"o{n}", "name": f"{n}. {name}", "theory": theory, "done": False, "questions": qs})
    for n, name, theory, qs in sorted(ege_raw, key=lambda x: x[0]):
        db["ЕГЭ Информатика"].append({"id": f"e{n}", "name": f"{n}. {name}", "theory": theory, "done": False, "questions": qs})

    return db

# ========================================================
# 3. ФУНКЦИИ ДАННЫХ
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
# 4. ИНТЕРФЕЙС И ГЕНЕРАЦИЯ QR
# ========================================================
st.sidebar.title("🚀 ExamFlow")

# --- ГЕНЕРАЦИЯ QR-КОДА ---
st.sidebar.markdown("---")
url = "https://myexam-nhswaerosug3kbxpkjqcd2.streamlit.app/" # Твоя ссылка
qr = segno.make(url)
out = io.BytesIO()
qr.save(out, kind='png', scale=4)
st.sidebar.image(out.getvalue(), caption="Мобильная версия")

# --- НАВИГАЦИЯ ---
# Важно: subj берет названия ПРЯМО из ключей словаря, что убирает KeyError
subj = st.sidebar.selectbox("Выберите экзамен:", list(st.session_state.db.keys()))
menu = st.sidebar.radio("Меню:", ["📊 Прогресс", "📖 Обучение", "🧠 Тренажёр"])

current_list = st.session_state.db[subj]

if menu == "📊 Прогресс":
    st.title(f"Ваш успех в {subj}")
    done = sum(1 for t in current_list if t["done"])
    st.metric("Пройдено тем", f"{done} / {len(current_list)}")
    st.progress(done / len(current_list))
    for t in current_list:
        st.write(f"{'✅' if t['done'] else '⬜'} {t['name']}")

elif menu == "📖 Обучение":
    st.title("📚 Теория")
    for t in current_list:
        with st.container():
            st.markdown(f'<div class="topic-card"><h3>{t["name"]}</h3><p>{t["theory"]}</p></div>', unsafe_allow_html=True)
            if st.button(f"Изучено: {t['name']}", key=f"btn_{t['id']}"):
                t["done"] = not t["done"]
                save_data(); st.rerun()

elif menu == "🧠 Тренажёр":
    st.title("⚡ Проверка знаний")
    topic_name = st.selectbox("Тема:", [t['name'] for t in current_list])
    target = next(t for t in current_list if t['name'] == topic_name)
    
    q_idx = st.session_state.get(f"q_{target['id']}", 0)
    
    if q_idx < 5:
        q_data = target['questions'][q_idx]
        st.info(f"Вопрос {q_idx + 1} из 5")
        st.write(f"### {q_data['q']}")
        ans = st.text_input("Ответ:", key=f"input_{target['id']}_{q_idx}")
        if st.button("Проверить"):
            if ans.strip().lower() == q_data['a'].lower():
                st.session_state[f"q_{target['id']}"] = q_idx + 1
                st.success("Верно!")
                st.rerun()
            else:
                st.error("Ошибка, подумай еще.")
    else:
        st.balloons()
        st.success("Тема пройдена!")
        target["done"] = True
        save_data()
        if st.button("Сбросить тест"):
            st.session_state[f"q_{target['id']}"] = 0
            st.rerun()

if st.sidebar.button("🗑 Сбросить всё"):
    if os.path.exists(DB_FILE): os.remove(DB_FILE)
    st.rerun()

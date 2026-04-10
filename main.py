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
    .stButton>button { background-color: #000; color: #fff; border-radius: 10px; border: none; font-weight: bold; }
    .stButton>button:hover { background-color: #444; color: #fff; }
    </style>
    """, unsafe_allow_html=True)

DB_FILE = "examflow_db.json"

# ========================================================
# 2. ПОЛНАЯ БАЗА ДАННЫХ (ОГЭ 1-16 + ЕГЭ 1-27)
# ========================================================
def get_initial_db():
    db = {"ОГЭ Информатика": [], "ЕГЭ Информатика": []}

    # Названия всех 16 заданий ОГЭ
    oge_names = [
        "Кодирование текста", "Декодирование (Фано)", "Логика", "Пути в графах",
        "Исполнитель", "Анализ программ", "Адресация в сети", "Запросы (Круги Эйлера)",
        "Количество путей (Схемы)", "Системы счисления", "Поиск в файлах", "Свойства файлов / Маски",
        "Презентация или Текст", "Таблицы (Excel)", "Робот (Кумир)", "Программирование (Python)"
    ]

    # Названия всех 27 заданий ЕГЭ
    ege_names = [
        "Графы", "Логика", "Базы данных", "Условие Фано", "Алгоритмы", "Черепаха", 
        "Медиа", "Комбинаторика", "Excel Таблицы", "Текстовый поиск", 
        "Объем памяти", "Редактор", "Сети (IP)", "Системы счисления", "Логика (Отрезки)", 
        "Рекурсия", "Массивы", "Робот в Excel", "Теория игр-1", "Теория игр-2", 
        "Теория игр-3", "Процессы", "Динамика", "Строки", "Числа (Маски)", 
        "Сортировка", "Анализ данных"
    ]

    # Заполнение базы ОГЭ
    for i, name in enumerate(oge_names, 1):
        db["ОГЭ Информатика"].append({
            "id": f"o{i}",
            "name": f"{i}. {name}",
            "theory": f"Теоретическая база и алгоритм решения для задания №{i}.",
            "yt_url": f"https://www.youtube.com/results?search_query=Умскул+ОГЭ+информатика+задание+{i}",
            "reshu_url": f"https://inf-oge.sdamgia.ru/search?search=задание+{i}",
            "done": False,
            "questions": [{"q": f"Ты готов к заданию {i} (напиши 'да')?", "a": "да"}] * 5
        })

    # Заполнение базы ЕГЭ
    for i, name in enumerate(ege_names, 1):
        db["ЕГЭ Информатика"].append({
            "id": f"e{i}",
            "name": f"{i}. {name}",
            "theory": f"Теоретическая база и алгоритм решения для задания №{i}.",
            "yt_url": f"https://www.youtube.com/results?search_query=Умскул+ЕГЭ+информатика+задание+{i}",
            "reshu_url": f"https://inf-ege.sdamgia.ru/search?search=задание+{i}",
            "done": False,
            "questions": [{"q": f"Ты готов к заданию {i} (напиши 'да')?", "a": "да"}] * 5
        })

    return db

# ========================================================
# 3. ФУНКЦИИ ДАННЫХ И АВТО-ОБНОВЛЕНИЕ
# ========================================================
def load_data():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r", encoding="utf-8") as f: 
            data = json.load(f)
            # Проверка: если в старой базе нет ссылок yt_url, сбрасываем её
            if "ОГЭ Информатика" in data and len(data["ОГЭ Информатика"]) > 0:
                if "yt_url" not in data["ОГЭ Информатика"][0]:
                    return get_initial_db()
            return data
    return get_initial_db()

def save_data():
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(st.session_state.db, f, ensure_ascii=False, indent=4)

if 'db' not in st.session_state:
    st.session_state.db = load_data()
    save_data()

# ========================================================
# 4. ИНТЕРФЕЙС И ГЕНЕРАЦИЯ QR
# ========================================================
st.sidebar.title("🚀 ExamFlow")

# --- ГЕНЕРАЦИЯ СТАТИЧНОГО QR-КОДА ---
st.sidebar.markdown("---")
static_url = "https://kirill-myexam.streamlit.app" # Эта ссылка теперь не меняется
qr = segno.make(static_url)
out = io.BytesIO()
qr.save(out, kind='png', scale=4)
st.sidebar.image(out.getvalue(), caption="Отсканируй для входа")

# --- НАВИГАЦИЯ ---
subj = st.sidebar.selectbox("Выберите экзамен:", list(st.session_state.db.keys()))
menu = st.sidebar.radio("Меню:", ["📊 Прогресс", "📖 Обучение", "🧠 Тренажёр"])

current_list = st.session_state.db[subj]

# --- РАЗДЕЛ: ПРОГРЕСС ---
if menu == "📊 Прогресс":
    st.title(f"Ваш успех: {subj}")
    done = sum(1 for t in current_list if t["done"])
    total = len(current_list)
    
    col1, col2 = st.columns(2)
    col1.metric("Пройдено тем", f"{done} / {total}")
    col2.metric("Готовность", f"{int(done/total*100) if total > 0 else 0}%")
    st.progress(done / total if total > 0 else 0)
    
    st.markdown("### Статус заданий")
    for t in current_list:
        st.write(f"{'✅' if t['done'] else '⬜'} {t['name']}")

# --- РАЗДЕЛ: ОБУЧЕНИЕ ---
elif menu == "📖 Обучение":
    st.title("📚 Теория и Практика")
    for t in current_list:
        with st.container():
            st.markdown(f'<div class="topic-card"><h3>{t["name"]}</h3><p>{t["theory"]}</p></div>', unsafe_allow_html=True)
            
            # Три кнопки в один ряд
            col1, col2, col3 = st.columns(3)
            with col1:
                st.link_button("📺 Смотреть Умскул", t["yt_url"], use_container_width=True)
            with col2:
                st.link_button("📝 Практика (Решу)", t["reshu_url"], use_container_width=True)
            with col3:
                if st.button(f"{'✅ Изучено' if t['done'] else '⬜ Изучить'}", key=f"btn_{t['id']}", use_container_width=True):
                    t["done"] = not t["done"]
                    save_data()
                    st.rerun()

# --- РАЗДЕЛ: ТРЕНАЖЁР ---
elif menu == "🧠 Тренажёр":
    st.title("⚡ Проверка знаний")
    topic_name = st.selectbox("Тема:", [t['name'] for t in current_list])
    target = next(t for t in current_list if t['name'] == topic_name)
    
    q_idx = st.session_state.get(f"q_{target['id']}", 0)
    
    if q_idx < 5:
        q_data = target['questions'][q_idx]
        st.info(f"Вопрос {q_idx + 1} из 5")
        st.write(f"### {q_data['q']}")
        ans = st.text_input("Ваш ответ (напиши 'да'):", key=f"input_{target['id']}_{q_idx}")
        
        if st.button("Проверить"):
            if ans.strip().lower() == q_data['a'].lower():
                st.session_state[f"q_{target['id']}"] = q_idx + 1
                st.success("Верно!")
                st.rerun()
            else:
                st.error("Ошибка, подумай еще.")
    else:
        st.balloons()
        st.success("Тема успешно пройдена!")
        if not target["done"]:
            target["done"] = True
            save_data()
            
        if st.button("Сбросить тест"):
            st.session_state[f"q_{target['id']}"] = 0
            st.rerun()

# --- КНОПКА СБРОСА БАЗЫ ДАННЫХ ---
if st.sidebar.button("⚠️ Сбросить весь прогресс"):
    if os.path.exists(DB_FILE): 
        os.remove(DB_FILE)
    st.session_state.clear()
    st.rerun()

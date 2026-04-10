import streamlit as st
import json
import os
import segno
import io

# ========================================================
# 1. НАСТРОЙКИ И ДИЗАЙН (РФМЛИ СТИЛЬ)
# ========================================================
st.set_page_config(page_title="ExamFlow | Final Build", layout="wide")

st.markdown("""
    <style>
    .topic-card { 
        padding: 20px; border-radius: 12px; background-color: #f8f9fa; 
        border-left: 5px solid #000; margin-bottom: 20px; box-shadow: 2px 2px 10px rgba(0,0,0,0.1);
    }
    .topic-card h3 { color: #1e1e1e !important; font-size: 18px; margin-bottom: 5px; }
    .stButton>button { width: 100%; border-radius: 8px; font-weight: bold; background-color: #000; color: #fff;}
    .stButton>button:hover { background-color: #333; color: #fff;}
    </style>
    """, unsafe_allow_html=True)

DB_FILE = "examflow_db.json"

# ========================================================
# 2. ПОЛНАЯ БАЗА ДАННЫХ (АВТОГЕНЕРАЦИЯ ССЫЛОК)
# ========================================================
def get_initial_db():
    db = {"ОГЭ Информатика": [], "ЕГЭ Информатика": []}

    # Названия всех 16 заданий ОГЭ
    oge_names = [
        "Кодирование текста", "Декодирование (Фано)", "Логика", "Пути в графах",
        "Исполнитель", "Анализ программ", "Адресация в сети", "Запросы (Круги Эйлера)",
        "Количество путей", "Системы счисления", "Поиск в файлах", "Свойства файлов",
        "Презентация или Текст", "Таблицы (Excel)", "Робот (Кумир)", "Программирование (Python)"
    ]

    # Названия всех 27 заданий ЕГЭ
    ege_names = [
        "Графы", "Логика", "Базы данных", "Фано", "Алгоритмы", "Черепаха",
        "Медиа", "Комбинаторика", "Excel Таблицы", "Текстовый поиск",
        "Объем памяти", "Редактор", "Сети (IP)", "Системы счисления",
        "Логика (Отрезки)", "Рекурсия", "Массивы", "Робот в Excel",
        "Теория игр-1", "Теория игр-2", "Теория игр-3", "Процессы",
        "Динамика", "Строки", "Числа (Маски)", "Сортировка", "Анализ данных"
    ]

    # Генерация ОГЭ
    for i, name in enumerate(oge_names):
        task_num = i + 1
        db["ОГЭ Информатика"].append({
            "id": f"o{task_num}",
            "name": f"{task_num}. {name}",
            "yt_url": f"https://www.youtube.com/results?search_query=Умскул+ОГЭ+информатика+задание+{task_num}",
            "reshu_url": f"https://inf-oge.sdamgia.ru/search?search=задание+{task_num}",
            "done": False,
            "questions": [{"q": f"Ты готов сдать задание {task_num} на максимум?", "a": "да"}] * 3
        })

    # Генерация ЕГЭ
    for i, name in enumerate(ege_names):
        task_num = i + 1
        db["ЕГЭ Информатика"].append({
            "id": f"e{task_num}",
            "name": f"{task_num}. {name}",
            "yt_url": f"https://www.youtube.com/results?search_query=Умскул+ЕГЭ+информатика+задание+{task_num}",
            "reshu_url": f"https://inf-ege.sdamgia.ru/search?search=задание+{task_num}",
            "done": False,
            "questions": [{"q": f"Понятен ли алгоритм решения задания {task_num}?", "a": "да"}] * 3
        })

    return db

# ========================================================
# 3. ФУНКЦИИ СОХРАНЕНИЯ И ЗАГРУЗКИ
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
# 4. ИНТЕРФЕЙС И НАВИГАЦИЯ
# ========================================================
st.sidebar.title("🚀 ExamFlow")
st.sidebar.markdown("---")

# QR-код для комиссии
qr_url = "https://kirill-myexam.streamlit.app"
qr = segno.make(qr_url)
out = io.BytesIO()
qr.save(out, kind='png', scale=4)
st.sidebar.image(out.getvalue(), caption="Отсканируй для входа")

subj = st.sidebar.selectbox("Выберите экзамен:", list(st.session_state.db.keys()))
menu = st.sidebar.radio("Навигация:", ["📊 Прогресс", "📖 Обучение", "🧠 Тренажёр", "⚙️ Архитектура"])

current_list = st.session_state.db[subj]

# --------------------------------------------------------
# БЛОК 1: ПРОГРЕСС
# --------------------------------------------------------
if menu == "📊 Прогресс":
    st.title(f"Ваш успех: {subj}")
    done = sum(1 for t in current_list if t["done"])
    total = len(current_list)
    
    col1, col2 = st.columns(2)
    col1.metric("Темы", f"{done} / {total}")
    col2.metric("Готовность", f"{int(done/total*100) if total > 0 else 0}%")
    st.progress(done / total if total > 0 else 0)
    
    st.markdown("### Статус заданий")
    for t in current_list:
        st.write(f"{'✅' if t['done'] else '⬜'} {t['name']}")

# --------------------------------------------------------
# БЛОК 2: ОБУЧЕНИЕ (С ДВУМЯ КНОПКАМИ)
# --------------------------------------------------------
elif menu == "📖 Обучение":
    st.title("📚 База знаний и Практика")
    
    for t in current_list:
        with st.container():
            st.markdown(f'<div class="topic-card"><h3>{t["name"]}</h3></div>', unsafe_allow_html=True)
            
            # Две кнопки ссылок в ряд
            btn_col1, btn_col2 = st.columns(2)
            with btn_col1:
                st.link_button("📺 Смотреть Умскул (YouTube)", t["yt_url"], use_container_width=True)
            with btn_col2:
                # Меняем текст в зависимости от ОГЭ/ЕГЭ
                reshu_text = "📝 Решу ОГЭ" if "ОГЭ" in subj else "📝 Решу ЕГЭ"
                st.link_button(reshu_text, t["reshu_url"], use_container_width=True)
            
            # Кнопка отметки выполнения
            if st.button(f"Отметить как изученное: {t['name']}", key=f"btn_{t['id']}"):
                t["done"] = not t["done"]
                save_data()
                st.rerun()
            st.markdown("<br>", unsafe_allow_html=True)

# --------------------------------------------------------
# БЛОК 3: ТРЕНАЖЁР (ВОЗВРАЩЕН)
# --------------------------------------------------------
elif menu == "🧠 Тренажёр":
    st.title("⚡ Проверка знаний")
    topic_name = st.selectbox("Выберите тему для проверки:", [t['name'] for t in current_list])
    target = next(t for t in current_list if t['name'] == topic_name)
    
    q_idx = st.session_state.get(f"q_{target['id']}", 0)
    total_q = len(target['questions'])
    
    if q_idx < total_q:
        q_data = target['questions'][q_idx]
        st.info(f"Вопрос {q_idx + 1} из {total_q}")
        st.write(f"### {q_data['q']}")
        ans = st.text_input("Ваш ответ:", key=f"input_{target['id']}_{q_idx}")
        
        if st.button("Проверить"):
            if ans.strip().lower() == q_data['a'].lower():
                st.session_state[f"q_{target['id']}"] = q_idx + 1
                st.success("Верно!")
                st.rerun()
            else:
                st.error("Ошибка, попробуйте еще раз. (Подсказка: напишите 'да')")
    else:
        st.balloons()
        st.success("Тема успешно пройдена на тренажёре!")
        if not target["done"]:
            target["done"] = True
            save_data()
        
        if st.button("Сбросить тест"):
            st.session_state[f"q_{target['id']}"] = 0
            st.rerun()

# --------------------------------------------------------
# БЛОК 4: АРХИТЕКТУРА И АЛГОРИТМ (ДЛЯ КОМИССИИ)
# --------------------------------------------------------
elif menu == "⚙️ Архитектура":
    st.title("🛠 Техническая реализация")
    st.info("Этот раздел демонстрирует логику работы приложения для экспертной комиссии РФМЛИ.")
    
    col_tech1, col_tech2 = st.columns(2)
    with col_tech1:
        st.subheader("Стек технологий")
        st.write("1. **Язык:** Python 3.10+")
        st.write("2. **Frontend:** Streamlit Library (Реактивный UI)")
        st.write("3. **БД:** JSON (Локальное хранилище состояний)")
        st.write("4. **QR-генерация:** Библиотека Segno")
    
    with col_tech2:
        st.subheader("Логика сохранения (Session State)")
        st.code("""
# Алгоритм работы базы данных
def save_data():
    with open("examflow_db.json", "w") as f:
        # Сериализация словаря python в JSON
        json.dump(st.session_state.db, f)

# При клике на чекбокс происходит st.rerun()
# Интерфейс перерисовывается с новыми данными
        """, language="python")

# Кнопка сброса всей базы
st.sidebar.markdown("---")
if st.sidebar.button("⚠️ Сбросить историю"):
    if os.path.exists(DB_FILE): 
        os.remove(DB_FILE)
    st.session_state.clear()
    st.rerun()

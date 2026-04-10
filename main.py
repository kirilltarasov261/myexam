import streamlit as st
import json
import os
import segno
import io

# 1. ДИЗАЙН (как на твоих скриншотах)
st.set_page_config(page_title="ExamFlow | Final Build", layout="wide")

st.markdown("""
    <style>
    .topic-card { 
        padding: 25px; border-radius: 15px; background-color: #ffffff; 
        border: 2px solid #000; margin-bottom: 25px; box-shadow: 8px 8px 0px #000;
    }
    .topic-card h3 { color: #000 !important; font-weight: 900; }
    .stButton>button { background-color: #000; color: #fff; border-radius: 10px; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

DB_FILE = "examflow_db.json"

# 2. ГЕНЕРАЦИЯ ДАННЫХ (ОГЭ 1-16 и ЕГЭ 1-27)
def get_initial_db():
    db = {"ОГЭ Информатика": [], "ЕГЭ Информатика": []}
    
    oge_names = [
        "Кодирование текста", "Декодирование (Фано)", "Логика", "Пути в графах",
        "Исполнитель", "Анализ программ", "Адресация в сети", "Запросы (Круги Эйлера)",
        "Количество путей (Схемы)", "Системы счисления", "Поиск в файлах", "Свойства файлов / Маски",
        "Презентация или Текст", "Таблицы (Excel)", "Робот (Кумир)", "Программирование (Python)"
    ]

    ege_names = [
        "Графы", "Логика", "Базы данных", "Условие Фано", "Алгоритмы", "Черепаха", 
        "Медиа", "Комбинаторика", "Excel Таблицы", "Текстовый поиск", 
        "Объем памяти", "Редактор", "Сети (IP)", "Системы счисления", "Логика (Отрезки)", 
        "Рекурсия", "Массивы", "Робот в Excel", "Теория игр-1", "Теория игр-2", 
        "Теория игр-3", "Процессы", "Динамика", "Строки", "Числа (Маски)", 
        "Сортировка", "Анализ данных"
    ]

    for i, name in enumerate(oge_names, 1):
        db["ОГЭ Информатика"].append({
            "id": f"o{i}", "name": f"{i}. {name}", "done": False,
            "yt": f"https://www.youtube.com/results?search_query=Умскул+ОГЭ+информатика+задание+{i}",
            "reshu": f"https://inf-oge.sdamgia.ru/search?search=задание+{i}"
        })

    for i, name in enumerate(ege_names, 1):
        db["ЕГЭ Информатика"].append({
            "id": f"e{i}", "name": f"{i}. {name}", "done": False,
            "yt": f"https://www.youtube.com/results?search_query=Умскул+ЕГЭ+информатика+задание+{i}",
            "reshu": f"https://inf-ege.sdamgia.ru/search?search=задание+{i}"
        })
    return db

# 3. ЗАГРУЗКА И СОХРАНЕНИЕ
if 'db' not in st.session_state:
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r", encoding="utf-8") as f:
            st.session_state.db = json.load(f)
    else:
        st.session_state.db = get_initial_db()

def save():
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(st.session_state.db, f, ensure_ascii=False, indent=4)

# 4. ИНТЕРФЕЙС
st.sidebar.title("🚀 ExamFlow")

# Статичный QR-код
qr = segno.make("https://kirill-myexam.streamlit.app") # Ссылка для комиссии
out = io.BytesIO()
qr.save(out, kind='png', scale=4)
st.sidebar.image(out.getvalue(), caption="Версия для комиссии")

subj = st.sidebar.selectbox("Экзамен:", list(st.session_state.db.keys()))
menu = st.sidebar.radio("Навигация:", ["📊 Мой Прогресс", "📖 Обучение"])

current_list = st.session_state.db[subj]

if menu == "📊 Мой Прогресс":
    st.title(f"Прогресс по {subj}")
    done = sum(1 for t in current_list if t["done"])
    total = len(current_list)
    col1, col2 = st.columns(2)
    col1.metric("Пройдено тем", f"{done} / {total}")
    col2.metric("Готовность", f"{int(done/total*100) if total > 0 else 0}%")
    st.progress(done / total if total > 0 else 0)
    st.markdown("### Чек-лист заданий")
    for t in current_list:
        st.write(f"{'✅' if t['done'] else '⬜'} {t['name']}")

elif menu == "📖 Обучение":
    st.title("Материалы и ресурсы")
    for t in current_list:
        with st.container():
            st.markdown(f'<div class="topic-card"><h3>{t["name"]}</h3></div>', unsafe_allow_html=True)
            c1, c2, c3 = st.columns(3)
            c1.link_button("📺 Видеоразбор", t["yt"], use_container_width=True)
            c2.link_button("📝 Практика", t["reshu"], use_container_width=True)
            if c3.button(f"{'✅' if t['done'] else '⬜'} Готово", key=f"btn_{t['id']}", use_container_width=True):
                t["done"] = not t["done"]
                save()
                st.rerun()

if st.sidebar.button("🗑 Очистить историю"):
    if os.path.exists(DB_FILE): os.remove(DB_FILE)
    st.session_state.clear()
    st.rerun()

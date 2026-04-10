import streamlit as st
import json
import os
import segno
import io

# 1. ДИЗАЙН И КОНФИГУРАЦИЯ
st.set_page_config(page_title="ExamFlow | Full Edition", layout="wide")

st.markdown("""
    <style>
    .topic-card { 
        padding: 20px; border-radius: 15px; background-color: #ffffff; 
        border: 2px solid #000; margin-bottom: 20px; box-shadow: 5px 5px 0px #000;
    }
    .stButton>button { background-color: #000; color: #fff; border-radius: 8px; width: 100%; }
    </style>
    """, unsafe_allow_html=True)

DB_FILE = "examflow_db.json"

# 2. БАЗА ДАННЫХ С ВОПРОСАМИ
def get_initial_db():
    db = {"ОГЭ Информатика": [], "ЕГЭ Информатика": []}
    
    oge_names = ["Кодирование", "Логика", "Графы", "Робот", "Программирование"]
    ege_names = ["Логика", "Алгоритмы", "Сети", "Динамика", "Анализ данных"]

    # Генерация ОГЭ (для примера 5 тем, можно расширить до 16)
    for i, name in enumerate(oge_names, 1):
        db["ОГЭ Информатика"].append({
            "id": f"o{i}", "name": f"{i}. {name}", "done": False,
            "yt": f"https://www.youtube.com/results?search_query=ОГЭ+информатика+задание+{i}",
            "reshu": f"https://inf-oge.sdamgia.ru/search?search=задание+{i}",
            "questions": [
                {"q": f"Вопрос №1 по теме {name}: Готов начать?", "a": "да"},
                {"q": f"Вопрос №2 по теме {name}: 1 байт это сколько бит?", "a": "8"}
            ]
        })

    # Генерация ЕГЭ
    for i, name in enumerate(ege_names, 1):
        db["ЕГЭ Информатика"].append({
            "id": f"e{i}", "name": f"{i}. {name}", "done": False,
            "yt": f"https://www.youtube.com/results?search_query=ЕГЭ+информатика+задание+{i}",
            "reshu": f"https://inf-ege.sdamgia.ru/search?search=задание+{i}",
            "questions": [
                {"q": f"Сложный вопрос №1 по ЕГЭ {name}: Напиши 'ок'", "a": "ок"},
                {"q": "Импликация истинна всегда, кроме случая 1 -> 0?", "a": "да"}
            ]
        })
    return db

# 3. УПРАВЛЕНИЕ ДАННЫМИ
if 'db' not in st.session_state:
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r", encoding="utf-8") as f:
                st.session_state.db = json.load(f)
        except:
            st.session_state.db = get_initial_db()
    else:
        st.session_state.db = get_initial_db()

def save():
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(st.session_state.db, f, ensure_ascii=False, indent=4)

# 4. БОКОВАЯ ПАНЕЛЬ
st.sidebar.title("🚀 ExamFlow")
qr = segno.make("https://t.me/your_link")
out = io.BytesIO(); qr.save(out, kind='png', scale=3)
st.sidebar.image(out.getvalue(), caption="Твой QR")

subj = st.sidebar.selectbox("Выбор экзамена:", list(st.session_state.db.keys()))
menu = st.sidebar.radio("Разделы:", ["📊 Мой Прогресс", "📖 Обучение", "🧠 Тренажёр", "📅 Планировщик"])

current_list = st.session_state.db[subj]

# ========================================================
# БЛОК 1: МОЙ ПРОГРЕСС
# ========================================================
if menu == "📊 Мой Прогресс":
    st.title(f"Статистика: {subj}")
    done = sum(1 for t in current_list if t["done"])
    total = len(current_list)
    st.metric("Завершено", f"{done} / {total}", f"{int(done/total*100) if total > 0 else 0}%")
    st.progress(done / total if total > 0 else 0)

# ========================================================
# БЛОК 2: ОБУЧЕНИЕ
# ========================================================
elif menu == "📖 Обучение":
    st.title("📚 Материалы")
    for t in current_list:
        with st.container():
            st.markdown(f'<div class="topic-card"><h3>{t["name"]}</h3></div>', unsafe_allow_html=True)
            c1, c2, c3 = st.columns(3)
            c1.link_button("📺 Видео", t["yt"])
            c2.link_button("📝 Задачи", t["reshu"])
            if c3.button(f"{'✅' if t['done'] else '⬜'} Изучено", key=f"learn_{t['id']}"):
                t["done"] = not t["done"]
                save(); st.rerun()

# ========================================================
# БЛОК 3: ТРЕНАЖЁР (ПОЛНОСТЬЮ РАБОЧИЙ)
# ========================================================
elif menu == "🧠 Тренажёр":
    st.title("⚡ Экспресс-тест")
    topic = st.selectbox("Выбери тему для теста:", [t['name'] for t in current_list])
    target = next(t for t in current_list if t['name'] == topic)
    
    # Индекс текущего вопроса в сессии
    q_key = f"step_{target['id']}"
    if q_key not in st.session_state: st.session_state[q_key] = 0
    
    idx = st.session_state[q_key]
    
    if idx < len(target['questions']):
        q_data = target['questions'][idx]
        st.info(f"Вопрос {idx + 1} из {len(target['questions'])}")
        st.subheader(q_data['q'])
        user_ans = st.text_input("Твой ответ:", key=f"ans_{target['id']}_{idx}")
        
        if st.button("Проверить ответ"):
            if user_ans.strip().lower() == q_data['a'].lower():
                st.success("Верно! Идем дальше.")
                st.session_state[q_key] += 1
                st.rerun()
            else:
                st.error("Неправильно. Попробуй еще раз.")
    else:
        st.balloons()
        st.success("Тест пройден!")
        if st.button("Сбросить и повторить"):
            st.session_state[q_key] = 0
            st.rerun()

# ========================================================
# БЛОК 4: ПЛАНИРОВЩИК (РАБОЧИЙ)
# ========================================================
elif menu == "📅 Планировщик":
    st.title("🗓 План подготовки")
    todo = [t for t in current_list if not t["done"]]
    
    if not todo:
        st.balloons()
        st.success("Все темы изучены! Ты готов к экзамену.")
    else:
        st.warning(f"Осталось изучить тем: {len(todo)}")
        for i, task in enumerate(todo[:3]): # Показываем ближайшие 3 задачи
            with st.expander(f"📌 План на сегодня: {task['name']}"):
                st.write("1. Посмотреть разбор на YouTube.")
                st.write("2. Решить 5 задач на РешуЕГЭ.")
                st.write("3. Отметить тему как выполненную.")
                if st.button("Выполнил план!", key=f"plan_{task['id']}"):
                    task["done"] = True
                    save(); st.rerun()

if st.sidebar.button("🗑 Сбросить прогресс"):
    if os.path.exists(DB_FILE): os.remove(DB_FILE)
    st.session_state.clear(); st.rerun()

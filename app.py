import streamlit as st
import json
import os
import segno
import io

# ========================================================
# 1. НАСТРОЙКИ И ЧЕРНЫЙ ТЕКСТ
# ========================================================
st.set_page_config(page_title="ExamFlow | Final Build", layout="wide")

st.markdown("""
    <style>
    .topic-card { 
        padding: 25px; border-radius: 15px; background-color: #ffffff; 
        border: 2px solid #000; margin-bottom: 25px; box-shadow: 8px 8px 0px #000;
    }
    /* Делаем все тексты внутри карточки черными */
    .topic-card h3, .topic-card p, .topic-card b, .topic-card span { 
        color: #000000 !important; 
    }
    .stButton>button { background-color: #000; color: #fff; border-radius: 10px; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

DB_FILE = "examflow_db.json"

# ========================================================
# 2. БАЗА ДАННЫХ (16 ТЕМ ОГЭ + 27 ТЕМ ЕГЭ)
# ========================================================
def get_initial_db():
    db = {"ОГЭ Информатика": [], "ЕГЭ Информатика": []}
    
    oge_names = [
        "Кодирование текста", "Декодирование (Фано)", "Логика", "Пути в графах",
        "Исполнитель", "Анализ программ", "Адресация в сети", "Запросы (Круги Эйлера)",
        "Количество путей", "Системы счисления", "Поиск в файлах", "Маски файлов",
        "Презентация/Текст", "Таблицы (Excel)", "Робот (Кумир)", "Программирование (Python)"
    ]

    for i, name in enumerate(oge_names, 1):
        db["ОГЭ Информатика"].append({
            "id": f"o{i}", "name": f"{i}. {name}", "done": False,
            "theory": f"<b>Важное для задания {i}:</b> Изучите алгоритм и формулы.",
            "yt": f"https://www.youtube.com/results?search_query=Умскул+ОГЭ+информатика+задание+{i}",
            "reshu": f"https://inf-oge.sdamgia.ru/search?search=задание+{i}",
            "questions": [{"q": f"Вопрос по теме {name}: 2+2?", "a": "4"}] * 3
        })

    for i in range(1, 28):
        db["ЕГЭ Информатика"].append({
            "id": f"e{i}", "name": f"{i}. Задание ЕГЭ", "done": False,
            "theory": f"<b>Теория ЕГЭ №{i}:</b> Разбор эффективных алгоритмов.",
            "yt": f"https://www.youtube.com/results?search_query=Умскул+ЕГЭ+информатика+задание+{i}",
            "reshu": f"https://inf-ege.sdamgia.ru/search?search=задание+{i}",
            "questions": [{"q": "Напиши 'да'", "a": "да"}] * 3
        })
    return db

# ========================================================
# 3. УПРАВЛЕНИЕ ПАМЯТЬЮ
# ========================================================
def load_data():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            # Если база старая (нет вопросов или ссылок), сбрасываем её
            try:
                test_item = data["ОГЭ Информатика"][0]
                if "questions" not in test_item or "yt" not in test_item:
                    return get_initial_db()
                return data
            except:
                return get_initial_db()
    return get_initial_db()

if 'db' not in st.session_state:
    st.session_state.db = load_data()

def save():
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(st.session_state.db, f, ensure_ascii=False, indent=4)

# ========================================================
# 4. ИНТЕРФЕЙС
# ========================================================
st.sidebar.title("🚀 ExamFlow")
subj = st.sidebar.selectbox("Экзамен:", list(st.session_state.db.keys()))
menu = st.sidebar.radio("Разделы:", ["📊 Мой Прогресс", "📖 Обучение", "🧠 Тренажёр", "📅 Планировщик"])

current_list = st.session_state.db[subj]

if menu == "📊 Мой Прогресс":
    st.title(f"Прогресс: {subj}")
    done = sum(1 for t in current_list if t["done"])
    st.metric("Пройдено", f"{done} / {len(current_list)}")
    st.progress(done / len(current_list))
    for t in current_list: st.write(f"{'✅' if t['done'] else '⬜'} {t['name']}")

elif menu == "📖 Обучение":
    st.title("📚 Материалы")
    for t in current_list:
        with st.container():
            st.markdown(f'<div class="topic-card"><h3>{t["name"]}</h3><p>{t["theory"]}</p></div>', unsafe_allow_html=True)
            c1, c2, c3 = st.columns(3)
            c1.link_button("📺 Видео", t["yt"])
            c2.link_button("📝 Практика", t["reshu"])
            if c3.button(f"{'✅' if t['done'] else '⬜'}", key=f"l_{t['id']}"):
                t["done"] = not t["done"]; save(); st.rerun()

elif menu == "🧠 Тренажёр":
    st.title("⚡ Экспресс-тест")
    topic = st.selectbox("Тема:", [t['name'] for t in current_list])
    target = next(t for t in current_list if t['name'] == topic)
    
    q_key = f"step_{target['id']}"
    if q_key not in st.session_state: st.session_state[q_key] = 0
    idx = st.session_state[q_key]

    if idx < len(target['questions']):
        q = target['questions'][idx]
        st.subheader(q['q'])
        ans = st.text_input("Ответ:", key=f"a_{target['id']}_{idx}")
        if st.button("Проверить"):
            if ans.strip().lower() == q['a'].lower():
                st.session_state[q_key] += 1; st.success("Верно!"); st.rerun()
            else: st.error("Ошибка!")
    else:
        st.balloons(); st.success("Тема пройдена!"); target["done"] = True; save()
        if st.button("Сбросить тест"): st.session_state[q_key] = 0; st.rerun()

elif menu == "📅 Планировщик":
    st.title("🗓 План на день")
    todo = [t for t in current_list if not t["done"]]
    site_name = "Решу ОГЭ" if "ОГЭ" in subj else "Решу ЕГЭ"
    
    if not todo: st.success("Ты всё выучил!")
    else:
        for t in todo[:3]:
            with st.expander(f"📌 {t['name']}"):
                st.write(f"1. Посмотри видео.")
                st.write(f"2. Реши тест на **{site_name}**.")
                if st.button("Сделано!", key=f"p_{t['id']}"):
                    t["done"] = True; save(); st.rerun()

if st.sidebar.button("🗑 Сбросить всё"):
    if os.path.exists(DB_FILE): os.remove(DB_FILE)
    st.session_state.clear(); st.rerun()

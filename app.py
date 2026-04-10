import streamlit as st
import json
import os
import segno
import io

# ========================================================
# 1. НАСТРОЙКИ И ДИЗАЙН (ЧЕРНЫЙ ТЕКСТ ДЛЯ ЧИТАЕМОСТИ)
# ========================================================
st.set_page_config(page_title="ExamFlow | Final Edition", layout="wide")

st.markdown("""
    <style>
    .topic-card { 
        padding: 25px; border-radius: 15px; background-color: #ffffff; 
        border: 2px solid #000; margin-bottom: 25px; box-shadow: 8px 8px 0px #000;
    }
    /* Строго черный цвет для всех текстов в карточках теории */
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
        "Кодирование текста", "Декодирование (Фано)", "Логика", "Пути в грахах",
        "Исполнитель", "Анализ программ", "Адресация в сети", "Запросы (Круги Эйлера)",
        "Количество путей", "Системы счисления", "Поиск в файлах", "Маски файлов",
        "Презентация/Текст", "Таблицы (Excel)", "Робот (Кумир)", "Программирование (Python)"
    ]

    # Тематические вопросы для ОГЭ
    oge_questions = {
        1: [{"q": "Сколько бит в 2 байтах?", "a": "16"}, {"q": "Символ весит 8 бит. Сколько байт в слове из 10 букв?", "a": "10"}],
        2: [{"q": "Если 00-А, 01-Б, что такое '0100'?", "a": "БА"}],
        3: [{"q": "Истина или ложь: (5 > 2) И (1 > 3)?", "a": "ложь"}],
        10: [{"q": "10 в двоичной системе это:", "a": "1010"}]
    }

    for i, name in enumerate(oge_names, 1):
        qs = oge_questions.get(i, [{"q": f"Вопрос по теме {name}: Напиши 'ок'", "a": "ок"}])
        db["ОГЭ Информатика"].append({
            "id": f"o{i}", "name": f"{i}. {name}", "done": False,
            "theory": f"<b>Теория задания №{i}:</b> Основные правила и алгоритмы решения.",
            "yt": f"https://www.youtube.com/results?search_query=Умскул+ОГЭ+информатика+задание+{i}",
            "reshu": f"https://inf-oge.sdamgia.ru/search?search=задание+{i}",
            "questions": qs
        })

    for i in range(1, 28):
        db["ЕГЭ Информатика"].append({
            "id": f"e{i}", "name": f"{i}. Задание ЕГЭ", "done": False,
            "theory": f"<b>Разбор задания ЕГЭ №{i}:</b> Алгоритмы повышенной сложности.",
            "yt": f"https://www.youtube.com/results?search_query=Умскул+ЕГЭ+информатика+задание+{i}",
            "reshu": f"https://inf-ege.sdamgia.ru/search?search=задание+{i}",
            "questions": [{"q": f"Тест ЕГЭ №{i}: Напиши 'готово'", "a": "готово"}]
        })
    return db

# ========================================================
# 3. ЛОГИКА ЗАГРУЗКИ
# ========================================================
if 'db' not in st.session_state:
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                # Проверка структуры (сброс если нет вопросов)
                if "ОГЭ Информатика" in data and "questions" not in data["ОГЭ Информатика"][0]:
                    st.session_state.db = get_initial_db()
                else:
                    st.session_state.db = data
        except:
            st.session_state.db = get_initial_db()
    else:
        st.session_state.db = get_initial_db()

def save():
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(st.session_state.db, f, ensure_ascii=False, indent=4)

# ========================================================
# 4. ИНТЕРФЕЙС И QR-КОД
# ========================================================
st.sidebar.title("🚀 ExamFlow")

# БЛОК QR-КОДА
qr_url = "https://myexam-rpxmihxm3ypamwdczibkkq.streamlit.app/" # Сюда вставь свою ссылку
qr = segno.make(qr_url)
out = io.BytesIO()
qr.save(out, kind='png', scale=4)
st.sidebar.image(out.getvalue(), caption="Сканируй для мобильной версии")

subj = st.sidebar.selectbox("Экзамен:", list(st.session_state.db.keys()))
menu = st.sidebar.radio("Навигация:", ["📊 Прогресс", "📖 Обучение", "🧠 Тренажёр", "📅 Планировщик"])

current_list = st.session_state.db[subj]

# --- ОБУЧЕНИЕ (С КНОПКОЙ ПРАКТИКА) ---
if menu == "📖 Обучение":
    st.title("📚 Теория и ресурсы")
    for t in current_list:
        with st.container():
            st.markdown(f'<div class="topic-card"><h3>{t["name"]}</h3><p>{t["theory"]}</p></div>', unsafe_allow_html=True)
            c1, c2, c3 = st.columns(3)
            c1.link_button("📺 Видео", t["yt"], use_container_width=True)
            c2.link_button("📝 Практика", t["reshu"], use_container_width=True)
            if c3.button(f"{'✅ Готово' if t['done'] else '⬜ Изучить'}", key=f"l_{t['id']}", use_container_width=True):
                t["done"] = not t["done"]; save(); st.rerun()

# --- ТРЕНАЖЁР (ТЕМАТИЧЕСКИЕ ВОПРОСЫ) ---
elif menu == "🧠 Тренажёр":
    st.title("⚡ Экспресс-тренировка")
    topic_name = st.selectbox("Тема:", [t['name'] for t in current_list])
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
            else: st.error("Попробуй еще раз")
    else:
        st.balloons(); st.success("Тема пройдена!"); target["done"] = True; save()
        if st.button("Повторить тест"): st.session_state[q_key] = 0; st.rerun()

# --- ПРОГРЕСС ---
elif menu == "📊 Прогресс":
    st.title(f"Ваш путь: {subj}")
    done = sum(1 for t in current_list if t["done"])
    st.metric("Завершено заданий", f"{done} / {len(current_list)}")
    st.progress(done / len(current_list))
    for t in current_list: st.write(f"{'✅' if t['done'] else '⬜'} {t['name']}")

# --- ПЛАНИРОВЩИК ---
elif menu == "📅 Планировщик":
    st.title("🗓 План подготовки")
    todo = [t for t in current_list if not t["done"]]
    site = "Решу ОГЭ" if "ОГЭ" in subj else "Решу ЕГЭ"
    if not todo: st.success("Всё выучено!")
    else:
        for t in todo[:3]:
            with st.expander(f"📌 План: {t['name']}"):
                st.write(f"1. Посмотри теорию.\n2. Реши задания на **{site}**.")
                if st.button("Сделано!", key=f"p_{t['id']}"):
                    t["done"] = True; save(); st.rerun()

if st.sidebar.button("🗑 Сброс"):
    if os.path.exists(DB_FILE): os.remove(DB_FILE)
    st.session_state.clear(); st.rerun()

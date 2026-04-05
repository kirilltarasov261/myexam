import streamlit as st
import json
import os

# ==================== НАСТРОЙКИ СТРАНИЦЫ ====================
st.set_page_config(
    page_title="ExamFlow | Твой IT-наставник", 
    layout="wide", 
    page_icon="👨‍💻"
)

DB_FILE = "user_progress.json"

# ==================== БАЗА ДАННЫХ (ИНФОРМАТИКА) ====================

def load_data():
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except: pass

    return {
        "Информатика": [
            {
                "id": 1, "class": 9, "type": "ОГЭ", 
                "name": "Кодирование текста (№1)", 
                "theory": """**Суть задания:** Найти объём памяти, который занимает текст.
                
**Формула:** $I = k \cdot i$
- $k$ — количество символов (включая пробелы и знаки препинания).
- $i$ — вес одного символа (в битах).
- $I$ — общий информационный объём.

**Важно:** Если в условии сказано 'Unicode', то обычно 1 символ = 16 бит = 2 байта.""", 
                "link": "https://inf-oge.sdamgia.ru/test?theme=1",
                "video": "https://www.youtube.com/embed/R0_qNf6O6oM",
                "question": "Статья из 100 символов весит 800 бит. Сколько бит весит 1 символ?",
                "answer": "8",
                "done": False
            },
            {
                "id": 2, "class": 11, "type": "ЕГЭ", 
                "name": "Анализ графов (№1)", 
                "theory": """**Алгоритм решения:**
1. Посчитай количество дорог у каждой вершины в таблице и на схеме.
2. Найди 'уникальные' точки (например, единственная вершина, из которой ведут 3 дороги).
3. Постепенно восстанавливай соответствие между буквами на графе и номерами в таблице.""", 
                "link": "https://inf-ege.sdamgia.ru/test?theme=221",
                "video": "https://www.youtube.com/embed/mC1yI5qI7eE",
                "question": "Как называется вершина графа, в которую не ведет ни одно ребро?",
                "answer": "исток",
                "done": False
            },
            {
                "id": 3, "class": 11, "type": "ЕГЭ", 
                "name": "Логические выражения (№2)", 
                "theory": """**Таблица истинности:**
- **Конъюнкция (∧, И):** Истина (1) только когда оба выражения истинны.
- **Дизъюнкция (∨, ИЛИ):** Ложь (0) только когда оба ложны.
- **Импликация (→):** Ложна (0) только в одном случае: из 1 следует 0.""", 
                "link": "https://kpolyakov.spb.ru/school/ege/gen.php?action=viewAll&topicId=2",
                "video": "https://www.youtube.com/embed/SAn_C_yLp9Y",
                "question": "Какая операция ложна только тогда, когда из 1 следует 0?",
                "answer": "импликация",
                "done": False
            }
        ],
        "Математика": [
            {
                "id": 10, "class": 9, "type": "ОГЭ", 
                "name": "Квадратные уравнения", 
                "theory": "Уравнение вида $ax^2 + bx + c = 0$. \n\nСначала находим дискриминант: $D = b^2 - 4ac$. \n\nЗатем корни: $x = \\frac{-b \pm \sqrt{D}}{2a}$.", 
                "link": "https://math-oge.sdamgia.ru/test?theme=23",
                "video": "https://www.youtube.com/embed/7pZbeS2M-n4",
                "question": "Найдите D уравнения $x^2 - 6x + 9 = 0$",
                "answer": "0",
                "done": False
            }
        ]
    }

def save_data():
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(st.session_state.db, f, ensure_ascii=False, indent=4)

if 'db' not in st.session_state:
    st.session_state.db = load_data()

# ==================== ИНТЕРФЕЙС ====================

st.sidebar.title("🚀 ExamFlow")
menu = st.sidebar.radio("Разделы:", ["📊 Прогресс", "📅 Планировщик", "📚 Теория", "🧠 Тесты"])
selected_subject = st.sidebar.selectbox("Предмет:", list(st.session_state.db.keys()))

if menu == "📊 Прогресс":
    st.title("📈 Твой успех")
    all_t = [t for sub in st.session_state.db.values() for t in sub]
    total, done = len(all_t), sum(1 for t in all_t if t["done"])
    st.metric("Выполнено", f"{done} из {total}", f"{int(done/total*100)}%" if total > 0 else "0%")
    st.progress(done / total if total > 0 else 0)

elif menu == "📅 Планировщик":
    st.title(f"📅 План: {selected_subject}")
    for i, topic in enumerate(st.session_state.db[selected_subject]):
        c1, c2 = st.columns([4, 1])
        status = "✅" if topic["done"] else "⬜"
        c1.markdown(f"### {status} {topic['name']}")
        if c2.button("Изменить статус", key=f"check_{topic['id']}"):
            st.session_state.db[selected_subject][i]["done"] = not topic["done"]
            save_data()
            st.rerun()

elif menu == "📚 Теория":
    st.title(f"📚 База знаний: {selected_subject}")
    for topic in st.session_state.db[selected_subject]:
        with st.expander(f"📖 {topic['name']}"):
            st.markdown(topic["theory"])
            st.link_button("🌐 Открыть задачи по теме", topic["link"])
            if "video" in topic:
                st.write("---")
                # Используем iframe для стабильности видео
                st.components.v1.iframe(topic["video"], height=400)

elif menu == "🧠 Тесты":
    st.title(f"🧠 Проверка знаний: {selected_subject}")
    topics = st.session_state.db[selected_subject]
    target = st.selectbox("Тема вопроса:", [t["name"] for t in topics])
    current = next(t for t in topics if t["name"] == target)
    
    st.warning(f"**Вопрос:** {current['question']}")
    ans = st.text_input("Твой ответ:")
    if st.button("Проверить"):
        if ans.lower().strip() == current['answer'].lower():
            st.balloons()
            st.success("Верно!")
        else:
            st.error("Попробуй еще раз, заглянув в теорию.")
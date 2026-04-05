import streamlit as st
import json
import os

# ==================== НАСТРОЙКИ СТРАНИЦЫ ====================
st.set_page_config(
    page_title="ExamFlow | Твой IT-наставник", 
    layout="wide", 
    page_icon="👨‍💻"
)

# Файл для хранения прогресса
DB_FILE = "user_progress.json"

# ==================== БАЗА ДАННЫХ (ИНФОРМАТИКА) ====================

def load_data():
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except: pass

    # Темы с теорией, ссылками на Полякова/РешуЕГЭ и видеоразборами
    return {
        "Информатика": [
            {
                "id": 1, "class": 9, "type": "ОГЭ", 
                "name": "Кодирование текста (№1)", 
                "theory": "Каждый символ весит определенное количество бит (i). Общий объём текста: $I = k \cdot i$. Если кодировка Unicode, то 1 символ = 16 бит (2 байта).", 
                "link": "https://kpolyakov.spb.ru/school/oge/download.htm",
                "video": "https://www.youtube.com/watch?v=R0_qNf6O6oM",
                "question": "Статья из 100 символов весит 800 бит. Сколько бит весит 1 символ?",
                "answer": "8",
                "done": False
            },
            {
                "id": 2, "class": 11, "type": "ЕГЭ", 
                "name": "Анализ графов (№1)", 
                "theory": "Нужно сопоставить таблицу расстояний и схему дорог. Ищи 'уникальные' вершины (например, единственную точку с 3 дорогами).", 
                "link": "https://inf-ege.sdamgia.ru/test?theme=221",
                "video": "https://www.youtube.com/watch?v=mC1yI5qI7eE",
                "question": "Как называется вершина графа, в которую не ведет ни одно ребро?",
                "answer": "исток",
                "done": False
            },
            {
                "id": 3, "class": 11, "type": "ЕГЭ", 
                "name": "Логические выражения (№2)", 
                "theory": "Операции: 1. **И** (/\) - истина только 1+1. 2. **ИЛИ** (\/) - ложь только 0+0. 3. **Следование** (->) - ложь только из 1 в 0.", 
                "link": "https://kpolyakov.spb.ru/school/ege/gen.php?action=viewAll&topicId=2",
                "video": "https://www.youtube.com/watch?v=SAn_C_yLp9Y",
                "question": "Какая операция ложна только тогда, когда из истины следует ложь?",
                "answer": "импликация",
                "done": False
            },
            {
                "id": 4, "class": 11, "type": "ЕГЭ", 
                "name": "Кодирование звука и фото (№7)", 
                "theory": "Фото: $I = X \cdot Y \cdot i$. Звук: $I = f \cdot t \cdot k \cdot i$. Где f - частота, t - время, k - каналы, i - разрешение.", 
                "link": "https://inf-ege.sdamgia.ru/test?theme=227",
                "video": "https://www.youtube.com/watch?v=m88L5B-YtB8",
                "question": "Сколько бит нужно для кодирования 4 цветов?",
                "answer": "2",
                "done": False
            }
        ],
        "Математика": [
            {
                "id": 10, "class": 9, "type": "ОГЭ", 
                "name": "Квадратные уравнения", 
                "theory": "Формула корней: $x = (-b ± \sqrt{D}) / 2a$, где $D = b^2 - 4ac$.", 
                "link": "https://math-oge.sdamgia.ru/test?theme=23",
                "video": "https://www.youtube.com/watch?v=7pZbeS2M-n4",
                "question": "Найдите дискриминант уравнения $x^2 - 4x + 4 = 0$",
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
st.sidebar.markdown("---")
menu = st.sidebar.radio("Разделы:", ["📊 Статистика", "📅 Мой план", "📚 Теория", "🧠 Тесты"])
st.sidebar.markdown("---")
selected_subject = st.sidebar.selectbox("Предмет:", list(st.session_state.db.keys()))

# --- СТРАНИЦА 1: СТАТИСТИКА ---
if menu == "📊 Статистика":
    st.title("📈 Твой прогресс")
    all_t = [t for sub in st.session_state.db.values() for t in sub]
    total = len(all_t)
    done = sum(1 for t in all_t if t["done"])
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Всего тем", total)
    col2.metric("Выучено", done)
    col3.metric("Готовность", f"{int(done/total*100) if total > 0 else 0}%")
    
    st.progress(done / total if total > 0 else 0)
    st.success("Продолжай в том же духе! Каждая отмеченная галочка приближает тебя к бюджету.")

# --- СТРАНИЦА 2: ПЛАНИРОВЩИК ---
elif menu == "📅 Мой план":
    st.title(f"📅 Чек-лист: {selected_subject}")
    st.write("Отмечай темы, которые ты уже разобрал.")
    
    for i, topic in enumerate(st.session_state.db[selected_subject]):
        c1, c2 = st.columns([4, 1])
        icon = "✅" if topic["done"] else "⬜"
        c1.markdown(f"### {icon} {topic['name']}")
        c1.caption(f"{topic['type']} | {topic['class']} класс")
        
        if c2.button("Изменить" , key=f"btn_{topic['id']}"):
            st.session_state.db[selected_subject][i]["done"] = not topic["done"]
            save_data()
            st.rerun()

# --- СТРАНИЦА 3: ТЕОРИЯ ---
elif menu == "📚 Теория":
    st.title(f"📚 База знаний: {selected_subject}")
    for topic in st.session_state.db[selected_subject]:
        with st.expander(f"🔍 {topic['name']}"):
            st.markdown(f"**Краткая шпаргалка:**\n\n{topic['theory']}")
            
            col1, col2 = st.columns(2)
            if "link" in topic:
                col1.link_button("🌐 Подробная теория (сайт)", topic["link"])
            
            if "video" in topic:
                st.markdown("---")
                st.write("📺 **Видеоразбор темы:**")
                st.video(topic["video"])

# --- СТРАНИЦА 4: ТЕСТЫ ---
elif menu == "🧠 Тесты":
    st.title(f"🧠 Тренажер: {selected_subject}")
    subject_topics = st.session_state.db[selected_subject]
    
    target_name = st.selectbox("Выбери тему для теста:", [t["name"] for t in subject_topics])
    current = next(t for t in subject_topics if t["name"] == target_name)
    
    st.info(f"**Вопрос:** {current['question']}")
    ans = st.text_input("Твой ответ:", key=f"inp_{current['id']}")
    
    if st.button("Проверить ответ"):
        if ans.lower().strip() == current['answer'].lower():
            st.balloons()
            st.success("Красавчик! Это правильный ответ.")
        else:
            st.error(f"Неа, попробуй еще раз. Правильный ответ скрыт в теории!")

# Запуск в терминале: python -m streamlit run main.py

import streamlit as st
import tempfile
from pathlib import Path
import final_pred
from collections import Counter

def state(all_marks):
    dict_pattern = Counter(all_marks)
    zero = dict_pattern.get(0, 0)
    ones = dict_pattern.get(1, 0)
    inv_ones = dict_pattern.get(-1, 0)
    state_print = []
    state_print.append((f"Статистика по {len(all_marks)} диалогам:"))
    state_print.append((f"Нейтрально - {zero} из {len(all_marks)} ({100.0 * zero / len(all_marks):.2f}%)"))
    state_print.append((f"Стремление - {ones} из {len(all_marks)} ({100.0 * ones / len(all_marks):.2f}%)"))
    state_print.append((f"Избегание - {inv_ones} из {len(all_marks)} ({100.0 * inv_ones / len(all_marks):.2f}%)"))
    return "\n".join(state_print)
    
def print_state(path):
    all_marks, dialogs = final_pred.predict_docx(path)
    final_res = []
    final_res.append("Классы: -1 = Избегание, 0 = Нейтрально, 1 = Стремление\n")

    for num, (interviewer_question, respondent_answer) in enumerate(dialogs):
        mark = all_marks[num]
        if (mark == -1):
            mark_str = "Избегание"
        elif (mark == 0):
            mark_str = "Нейтрально"
        else:
            mark_str = "Стремление"

        line = (
            f"Диалог #{num + 1} (И: {interviewer_question} / Р: {respondent_answer}) "
            f"-> класс: {mark} ({mark_str})\n"
        )

        final_res.append(line)
    final_res.append(state(all_marks))
    final_res = "\n".join(final_res)
    return final_res


st.title("Цифровой анализ интервью для выявления мотивационных паттернов: Стремление – Избегание")
example_view = """
<div style="
    border: 1px solid #e1e4e8;
    border-radius: 8px;
    padding: 16px;
    margin: 10px 0;
    background-color: #f6f8fa;
    box-shadow: 0 1px 3px rgba(0,0,0,0.1);
">
    <p style="margin: 0; color: #333;"><b>И:</b> Мы подключены. Итак, господин Исид, вы меня слышите? Как вы поживаете?</p>
    <p style="margin: 8px 0 0 0; color: #333;"><b>Р:</b> Я в порядке. А вы?</p>
    <p style="margin: 8px 0 0 0; color: #333;"><b>И:</b> Прежде всего, большое спасибо, что присоединились ко мне. Для меня это большое удовольствие иметь вас в гостях.</p>
</div>
"""

st.markdown(example_view, unsafe_allow_html=True)

user_file = st.file_uploader("Загрузите .docx", type=["docx"])


              
if user_file:
    user_path = Path(tempfile.gettempdir()) / user_file.name
    with open(user_path, "wb") as f:
        f.write(user_file.getbuffer())
    user_state = print_state(user_path)
    st.text_area("Результат анализа загруженного файла", value=user_state, height=400)
    st.download_button("Скачать отчёт", user_state, file_name="result.txt", mime="text/plain")
    
st.subheader("Можете посмотреть примеры файлов")    

examples_dir = Path(__file__).parent / "Интервью_русские"
sample_files = sorted(examples_dir.glob("*.docx"))


names = [p.name for p in sample_files]
choice = st.selectbox("Выберите пример", names)
with open(examples_dir / choice, "rb") as f:
        st.download_button("Скачать пример", f.read(), file_name=choice, mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document")
if st.button("Проанализировать пример"):
    example_state = print_state(examples_dir / choice)
    st.text_area("Результат анализа примера", value=example_state, height=400)
    st.download_button("Скачать отчёт примера", example_state, file_name="result_example.txt", mime="text/plain")

            

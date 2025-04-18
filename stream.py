import streamlit as st
import tempfile
from pathlib import Path
import final_pred


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


st.title("Digital-Analysis-of-the-Interview-for-Identifying-Motivational-Patterns-Approach-Avoidance")
user_file = st.file_uploader("Загрузите .docx", type=["docx"])
if user_file:
    user_path = Path(tempfile.gettempdir()) / user_file.name
    with open(user_path, "wb") as f:
        f.write(user_file.getbuffer())
    user_state = print_state(user_path)
    st.text_area("Результат", value=user_state, height=400)
    st.download_button("Скачать отчёт", user_state, file_name="result.txt", mime="text/plain")

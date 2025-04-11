import argparse
import docx
import joblib
from collections import Counter
from io import StringIO
import sys


def read_docx(path):
    cur_file = docx.Document(path)
    res = []

    for line in cur_file.paragraphs:
        res.append(line.text)

    return "\n".join(res)


def get_interviewer_lines(text):
    interviewer_lines = []

    for line in text.split('\n'):
        line = line.lstrip()
        if line.startswith("И:"):
            interviewer_lines.append(line[len("И:"):].strip())

    return interviewer_lines


def get_respondent_lines(text):
    respondent_lines = []

    for line in text.split('\n'):
        line = line.lstrip()
        if line.startswith("Р:"):
            respondent_lines.append(line[len("Р:"):].strip())

    return respondent_lines


def get_dialog_pairs(path):
    text = read_docx(path)
    interviewer_lines = get_interviewer_lines(text)
    respondent_lines = get_respondent_lines(text)

    dialogs = []
    count = min(len(interviewer_lines), len(respondent_lines))

    for i in range(count):
        dialogs.append((interviewer_lines[i], respondent_lines[i]))

    return dialogs


def predict_docx(path):
    model = joblib.load('model_course.pkl')
    vectorizer = joblib.load('vectorizer_course.pkl')

    dialogs = get_dialog_pairs(path)
    all_marks = []

    for (interviewer_question, respondent_answer) in dialogs:
        dialog = f"Вопрос: {interviewer_question} Ответ: {respondent_answer}"
        vector_of_dialog = vectorizer.transform([dialog])
        mark = model.predict(vector_of_dialog)
        all_marks.append(int(mark[0]))

    return all_marks, dialogs


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


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--doc", type=str, required=True,
                        help="Путь к .docx файлу (формат: И:.. / Р:..).")
    parser.add_argument("--out", type=str, default=None,
                        help="Путь к файлу для сохранения вывода (если не указан, вывод в консоль).")
    args = parser.parse_args()

    all_marks, dialogs = predict_docx(args.doc)

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

    if args.out is not None:
        with open(args.out, "w", encoding="utf-8") as f:
            f.write(final_res)
        print(f"Результат сохранён в файл: {args.out}")
    else:
        print(final_res)

import argparse
import docx
import joblib
from collections import Counter
from io import StringIO
import sys

def read_docx(path):
    doc = docx.Document(path)
    lines = [p.text for p in doc.paragraphs]
    return lines

def get_dialog_pairs(lines):
    interviewer_lines = []
    respondent_lines = []
    for line in lines:
        line = line.strip()
        if line.startswith("И:"):
            interviewer_lines.append(line[2:].strip())
        elif line.startswith("Р:"):
            respondent_lines.append(line[2:].strip())

    count = min(len(interviewer_lines), len(respondent_lines))
    pairs = []
    for i in range(count):
        int_text = interviewer_lines[i]
        res_text = respondent_lines[i]
        pairs.append((int_text, res_text))
    return pairs

def predict_docx(docx_path, model_path, vectorizer_path):
    model = joblib.load(model_path)
    vectorizer = joblib.load(vectorizer_path)

    lines = read_docx(docx_path)
    pairs = get_dialog_pairs(lines)

    marks = []
    for (int_text, res_text) in pairs:
        text_for_clf = f"Вопрос: {int_text} Ответ: {res_text}"
        X = vectorizer.transform([text_for_clf])
        pred = model.predict(X)
        marks.append(int(pred[0]))

    return marks, pairs

def state(all_marks):
    c = Counter(all_marks)
    total = len(all_marks)
    inv_ones = c.get(-1, 0)
    zero = c.get(0, 0)
    ones = c.get(1, 0)

    if total > 0:
        inv_ones_pct = 100.0 * inv_ones / total
        zero_pct = 100.0 * zero / total
        ones_pct = 100.0 * ones / total
    else:
        inv_ones_pct = zero_pct = ones_pct = 0.0

    # Подготавливаем строку со статистикой
    stats = []
    stats.append(f"\nСтатистика по {total} диалогам:")
    stats.append(f"Нейтрально – {zero} из {total} ({zero_pct:.2f}%)")
    stats.append(f"Стремление – {ones} из {total} ({ones_pct:.2f}%)")
    stats.append(f"Избегание – {inv_ones} из {total} ({inv_ones_pct:.2f}%)")
    return "\n".join(stats)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--doc", type=str, required=True,
                        help="Путь к .docx файлу (формат: И:.. / Р:..).")
    parser.add_argument("--model", type=str, default="model_course.pkl",
                        help="Файл с обученной моделью SVC.")
    parser.add_argument("--vectorizer", type=str, default="vectorizer_course.pkl",
                        help="Файл с TF-IDF векторизатором.")
    parser.add_argument("--out", type=str, default=None,
                        help="Путь к файлу для сохранения вывода (если не указан, вывод в консоль).")
    args = parser.parse_args()

    marks, dialogs = predict_docx(args.doc, args.model, args.vectorizer)

    # Собираем всё в один общий "отчёт" (строку), чтобы потом либо вывести, либо записать в файл
    output_lines = []
    output_lines.append("Классы: -1 = Избегание, 0 = Нейтрально, +1 = Стремление\n")

    for i, (int_text, res_text) in enumerate(dialogs):
        label = marks[i]
        if label == -1:
            label_name = "избегание"
        elif label == 0:
            label_name = "нейтрально"
        else:
            label_name = "стремление"

        line = (
            f"Диалог #{i+1} (И: {int_text} / Р: {res_text}) "
            f"-> класс: {label} ({label_name})"
        )
        output_lines.append(line)

    # Добавим статистику
    stats_text = state(marks)
    output_lines.append(stats_text)

    final_report = "\n".join(output_lines)

    # Если пользователь указал --out, пишем в файл
    if args.out is not None:
        with open(args.out, "w", encoding="utf-8") as f:
            f.write(final_report)
        print(f"Результат сохранён в файл: {args.out}")
    else:
        # Иначе выводим в консоль
        print(final_report)


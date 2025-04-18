# Digital Analysis of the Interview for Identifying Motivational Patterns: Approach – Avoidance
Данный проект направлен на автоматическое определение мотивационных паттернов: стремление и избегание по интервью.

Состоит из:

    1.Интервью_русские --- папка с реальными интервью, на которых происходит тестирование(там 7 файлов, названия имеют вид: Test{i}.docx
    
    2.InterviewRussian.xlsx --- таблица с этими 7 интервью, каждое разбито по диалогам(вопрос + ответ) и поставлен класс(-1, 0, 1, соответственно для избегания, нейтрально, стремления)
    
    3.MotivationPatterns.ipynb --- colab, где происходило обучение модели и ее тестирование
    
    4.TrainDatasetCurs.xlsx --- сама таблица из 10716 записей, на которой потом происходит обучение модели

Чтобы запустить данный анализ у себя:

python3 final_pred.py --doc Test_script.docx --out res_test.txt

нужно скачать файлы final_pred.py, model_course.pkl, vectorizer_course.pkl и поместить в одно место, дальше запускаем строчку выше и вместо Test_script.docx - ваше интервью для анализа, часть, начиная, с --out можно не писать, тогда будет выведен результат в консоль, иначе он сохранится в файл res_test.txt

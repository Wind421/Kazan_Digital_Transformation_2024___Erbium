Эта папка посвещена обучению модели для классифкации комментариев по эмоциональной окраске.

Содержание папки:
+ emotional_preprosessing.ipynb - содержит весь процесс преобработки датасета начиная с удаления лишних символов до лемматизации и удаления стоп-слов.
+ emotional_train_tfidf.ipynb - содержит векторизацию постов с помощью TF-IDF и обучение моделей
+ emotional_train_word2vec.ipynb - содержит векторизацию постов с помощью Word2Vec и обучение моделей, а также тест лучшей модели
+ mlp_emotion_word2vec.pkl - лучшая модель sklearn.neural_network MLPClassifier

Датасет собран из двух: 
+ https://www.kaggle.com/datasets/alexandersemiletov/toxic-russian-comments
+ https://www.kaggle.com/datasets/thorinhood/russian-twitter-sentiment

В датасете сохранены комментарии с негативной и позитивной окраской примерно по 110 тысяч и в 2 раза больше нейтральных комментариев.

Результаты обучения моделей для F1:
|Векторизатор|LogisticRegression|KNeighborsClassifier|GaussianNB|LinearDiscriminantAnalysis|CatBoostClassifier|MLPClassifier|
|------------|------------------|--------------------|----------|--------------------------|------------------|-------------|
|TF-IDF|0.65|0.49|0.47|0.6|0.53|0.6|
|Word2Vec|0.91|0.93|0.89|0.88|0.94|**0.94**|

MLPClassifier был выбран как самая легкая, быстрая и точная модель.

По скорости она превосходит LogisticRegression и KNeighborsClassifier, а по весу в 10к меньше чем CatBoostClassifier.

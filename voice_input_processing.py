
import speech_recognition  # распознавание пользовательской речи (Speech-To-Text)
import pyttsx3  # синтез речи (Text-To-Speech)
import webbrowser  # работа с использованием браузера по умолчанию (открывание вкладок с web-страницей)
import traceback  # вывод traceback без остановки работы программы при отлове исключений
import json
import wave
import os

with open("config.json", "r", encoding="UTF-8") as file:
        config = json.load(file)

class UserPerson:

    name = ""
    home_city = ""
    native_language = ""

class VoiceAssistant:

    name = "Грандесса"
    sex = "female"
    speech_language = "ru"
    recognition_language = "ru-RU"


def setup_assistant_voice():

    voices = ttsEngine.getProperty("voices")
    assistant.recognition_language = "ru-RU"
    ttsEngine.setProperty("voice", voices[0].id)


def play_voice_assistant_speech(text_to_speech):

    ttsEngine.say(str(text_to_speech))
    ttsEngine.runAndWait()


def record_and_recognize_audio(*args: tuple):

    with microphone:
        recognized_data = ""

        # регулирование уровня окружающего шума
        recognizer.adjust_for_ambient_noise(microphone, duration=2)

        try:
            print("Listening...")
            audio = recognizer.listen(microphone, 5, 5)

            with open("microphone-results.wav", "wb") as file:
                file.write(audio.get_wav_data())

        except speech_recognition.WaitTimeoutError:
            print("Не могли бы вы проверить, включен ли ваш микрофон, пожалуйста?")
            return

        # использование online-распознавания через Google
        try:
            print("Started recognition...")
            recognized_data = recognizer.recognize_google(audio, language="ru").lower()

        except speech_recognition.UnknownValueError:
            play_voice_assistant_speech("Повторите, пожалуйста?")

        return recognized_data

def play_voice_assistant_speech(text_to_speech):
    """
    Проигрывание речи ответов голосового ассистента (без сохранения аудио)
    :param text_to_speech: текст, который нужно преобразовать в речь
    """
    ttsEngine.say(str(text_to_speech))
    ttsEngine.runAndWait()

def execute_command_with_name(command_name: str, *args: list):
    """
    Выполнение заданной пользователем команды с дополнительными аргументами
    :param command_name: название команды
    :param args: аргументы, которые будут переданы в функцию
    :return:
    """
    for key in commands.keys():
        if command_name in key:
            commands[key](*args)
        else:
            print("Command not found")

def prepare_corpus():
    """
    Подготовка модели для угадывания намерения пользователя
    """
    corpus = []
    target_vector = []
    for intent_name, intent_data in config["intents"].items():
        for example in intent_data["examples"]:
            corpus.append(example)
            target_vector.append(intent_name)

    training_vector = vectorizer.fit_transform(corpus)
    classifier_probability.fit(training_vector, target_vector)
    classifier.fit(training_vector, target_vector)


def get_intent(request):
    """
    Получение наиболее вероятного намерения в зависимости от запроса пользователя
    :param request: запрос пользователя
    :return: наиболее вероятное намерение
    """
    best_intent = classifier.predict(vectorizer.transform([request]))[0]

    index_of_best_intent = list(classifier_probability.classes_).index(best_intent)
    probabilities = classifier_probability.predict_proba(vectorizer.transform([request]))[0]

    best_intent_probability = probabilities[index_of_best_intent]

    # при добавлении новых намерений стоит уменьшать этот показатель
    if best_intent_probability > 0.57:
        return best_intent

if __name__ == "__main__":

    # инициализация инструментов распознавания и ввода речи
    recognizer = speech_recognition.Recognizer()
    microphone = speech_recognition.Microphone()

    # инициализация инструмента синтеза речи
    ttsEngine = pyttsx3.init()

    # установка голоса по умолчанию
    setup_assistant_voice()

    vectorizer = TfidfVectorizer(analyzer="char", ngram_range=(2, 3))
    classifier_probability = LogisticRegression()
    classifier = LinearSVC()
    prepare_corpus()

    # отделение команд от дополнительной информации (аргументов)
    if voice_input:
        voice_input_parts = voice_input.split(" ")

        # если было сказано одно слово - выполняем команду сразу
        # без дополнительных аргументов
        if len(voice_input_parts) == 1:
            intent = get_intent(voice_input)
            if intent:
                config["intents"][intent]["responses"]()
            else:
                config["failure_phrases"]()

        # в случае длинной фразы - выполняется поиск ключевой фразы
        # и аргументов через каждое слово,
        # пока не будет найдено совпадение
        if len(voice_input_parts) > 1:
            for guess in range(len(voice_input_parts)):
                intent = get_intent((" ".join(voice_input_parts[0:guess])).strip())
                if intent:
                    command_options = [voice_input_parts[guess:len(voice_input_parts)]]
                    config["intents"][intent]["responses"](*command_options)
                    break
                if not intent and guess == len(voice_input_parts)-1:
                    config["failure_phrases"]()

    while True:
        # старт записи речи с последующим выводом распознанной речи
        # и удалением записанного в микрофон аудио
        voice_input = record_and_recognize_audio()
        if os.path.exists("microphone-results.wav"):
            os.remove("microphone-results.wav")
        print(colored(voice_input, "blue"))

        # отделение комманд от дополнительной информации (аргументов)
        voice_input = voice_input.split(" ")
        command = voice_input[0]
        command_options = [str(input_part) for input_part in voice_input[1:len(voice_input)]]
        execute_command_with_name(command, command_options)

        if command == "Грандесса":
            play_voice_assistant_speech("Здравствуй")

        if command == "Помоги мне":
            play_voice_assistant_speech("К Вашим услугам")

        if command == "Регистрация":
            play_voice_assistant_speech("Чтобы зарегистрироваться на портале необходимо нажать кнопку Регистрация")


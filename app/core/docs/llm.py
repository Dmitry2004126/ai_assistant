import textwrap


class LLMMsgBodyDocs:
    class Config:
        json_schema_extra = {
            'example': {
                'question': 'Привет, сколько будет 2 + 2?',
            }
        }
        docstring = textwrap.dedent(
            """
            Отправляет запрос к LLM. Сообщение пользователя к LLM.

            Аргументы
            - **question**: Сообщение пользователя
            """
        )


class LLM10MsgsBodyDocs:
    class Config:
        docstring = textwrap.dedent(
            """
            Возвращает последние 10 сообщений из истории чата.

            Сообщения отсортированы по дате в порядке убывания (от самых новых к старым).
            Каждое сообщение содержит текст, тип (вопрос/ответ), дату создания и ID пользователя.

            Returns:
                list[MsgResponse]: Список из 10 последних сообщений
            """
        )

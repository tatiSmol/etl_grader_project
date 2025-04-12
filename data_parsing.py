import ast

from logger import Logger


class DataParsing:
    def __init__(self, name='DataParsing'):
        self.logger = Logger(name).get_logger()

    def __data_validation(self, record):
        req_fields = ['lti_user_id', 'passback_params', 'attempt_type', 'created_at', 'is_correct']
        for field in req_fields:
            if field not in record:
                self.logger.warning(f'Пропущено поле {field} в записи: {record}')
                return False

        if record['attempt_type'] not in ('run', 'submit'):
            self.logger.warning(f"Некорректный attempt_type: {record['attempt_type']}")
            return False

        return True

    def __passback_params_processing(self, record):
        try:
            req_params = ['oauth_consumer_key', 'lis_result_sourcedid', 'lis_outcome_service_url']
            params_dict = ast.literal_eval(record['passback_params'])

            for param in req_params:
                if param not in params_dict:
                    user_id = record['lti_user_id']
                    self.logger.warning(f'Пропущен параметр {param} у пользователя: {user_id}')
                    return None
            return params_dict
        except Exception as ex:
            self.logger.warning(f'Ошибка при обработке поля passback_params: {ex}')

    def process(self, input_data):
        output_data = []
        for record in input_data:
            if not self.__data_validation(record):
                continue

            p_params = self.__passback_params_processing(record)
            if not p_params:
                continue

            valid_record = {
                'user_id': record['lti_user_id'],
                'oauth_consumer_key': p_params['oauth_consumer_key'],
                'lis_result_sourcedid': p_params['lis_result_sourcedid'],
                'lis_outcome_service_url': p_params['lis_outcome_service_url'],
                'is_correct': record['is_correct'],
                'attempt_type': record['attempt_type'],
                'created_at': record['created_at']
            }

            output_data.append(valid_record)
        self.logger.info(f'Успешно обработано {len(output_data)} записей из {len(input_data)}')
        return output_data

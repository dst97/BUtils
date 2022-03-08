import logging

import pandas
from pandas import DataFrame
import re

LOGGER = logging.getLogger()

FILE_PATTERN = re.compile(r'.*(?P<eid>h\d+)_(?P<tuid>.*)_(?P<ln>\D*)_(?P<fn>\D*).csv')


class Rubric:

    def __init__(self, file: str):
        self.__init_information(file)
        self.__init_csv(file)

    def __init_csv(self, file: str):
        try:
            self.__frame = pandas.read_csv(file, header=1, index_col='Kriterium')
            self.points = self.__frame.loc['Gesamt', 'Erzielt']
        except Exception as e:
            raise Exception("<{file}> could not be read.")

    def __init_information(self, file_name: str, warn: bool = True) -> None:
        """
        Sets the exercise id, the tu id, the last name and the first name given by the file name.
        :type warn: if a warning should be printed if the file name does not match the expected pattern
        :param file_name: the file name
        """
        self.exercise_id = self.tu_id = self.last_name = self.first_name = None
        match = FILE_PATTERN.match(file_name)
        if not match:
            if warn:
                LOGGER.warning("<{file}> does not match name pattern.".format(file=file_name))
            return
        self.exercise_id = match['eid']
        self.tu_id = match['tuid']
        self.last_name = match['ln']
        self.first_name = match['fn']

    @property
    def full_name(self) -> str:
        return '{fn} {ln}'.format(fn=self.first_name, ln=self.last_name)

    def file_name(self, data_format: str = 'json') -> str:
        return f'{self.exercise_id}_{self.tu_id}_{self.last_name}_{self.first_name}.{data_format}'

    def __str__(self):
        return '{0}'.format(self.exercise_id)

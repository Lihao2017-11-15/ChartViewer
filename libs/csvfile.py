import re
import math
from .datetime_string import to_seconds, to_timedelta
import logging
import os

logger = logging.getLogger()


class CSVFile:
    indexes = {}
    columns = []
    headers_dict = {}
    file_name = ''

    @staticmethod
    def read_rows_from_file(source_file_name):
        rows = []
        try:
            with open(source_file_name, mode='r', encoding='UTF-8-sig') as source_file:
                counter = 0
                for line in source_file:
                    rows.append(line)
                    counter += 1
        except:
            logger.error('Cannot read a file {}'.format(source_file_name))
            input()
        return rows

    def __init__(self, file_name=None, headers=None, rows_list=None):
        if file_name is not None or rows_list is not None:
            # Get a rows list if not given as argument
            if rows_list == None:
                rows_list = self.read_rows_from_file(file_name)

            # Detect number of columns in a rows list
            number_of_columns = self.detect_number_of_columns_in_rows_list(
                rows_list)

            # Case 1: headers are the first row of the file
            if headers == None:
                first_row_list = rows_list[0].replace('\n', '').split(',')
                first_row_correct_lenght = len(
                    first_row_list) == number_of_columns
                if first_row_correct_lenght:
                    first_row_correct_type = all(isinstance(
                        item, str) for item in first_row_list)
                    if first_row_correct_type:
                        headers = first_row_list
                        rows_list.pop(0)
            # Case 2: default values
            else:
                if headers != None:
                    headers_correct_type = (isinstance(headers, list) and all(
                        isinstance(item, str) for item in headers))
                    headers_correct_lenght = len(headers) != number_of_columns

                    if not headers_correct_type or headers_correct_lenght:
                        if headers_correct_type and len(headers) != number_of_columns:
                            logger.warning(
                                '{}: Incorrect headers so they have been replaced by default values.'.format(file_name))
                        headers = []
                        headers = self.get_default_headers(number_of_columns)

            self.create_table(rows_list, headers)

    def detect_number_of_columns_in_rows_list(self, rows_list):
        max_lenght = 0
        for row in rows_list:
            lenght = len(row.split(','))
            if lenght > max_lenght:
                max_lenght = lenght
        return max_lenght

    def detect_max_number_of_instances(self):
        maximum = 0
        for column in self.columns:
            if maximum < len(column.instances):
                maximum = len(column.instances)
        return maximum

    def idx(self, name):
        for column in self.columns:
            if column.name == name:
                return self.columns.index(column)
        logger.warning('There is no column with that name.')

    def sort_table(self, key_column_name, names, descending=False):
        list_dict_table = self.get_list_dict(column_names=names)
        for column in self.columns:
            if column.name == key_column_name:
                if column.content_type == 'time':
                    list_dict_table.sort(key=lambda row: to_timedelta(
                        row[key_column_name]).total_seconds(), reverse=descending)
                else:
                    list_dict_table.sort(key=lambda row: int(
                        row[key_column_name]), reverse=descending)
        self.create_table(list_dict_table=list_dict_table, column_names=names)

    def get_list_dict(self, rows_list=None, column_names=None):
        if rows_list == None:
            rows_list = self.get_rows_list()

        if column_names == None:
            column_names = self.get_names_list()

        table = []
        row_counter = 0
        for row in rows_list:
            splitted_row = row.split(',')
            table.append(dict())
            for i in range(len(column_names)):
                if len(splitted_row) >= (i + 1):
                    content = splitted_row[i].replace('\n', '')
                    content = content.strip()
                    table[row_counter][column_names[i]] = content
                else:
                    table[row_counter][column_names[i]] = ''
            row_counter += 1

        return table

    def get_list_list(self, start=0):
        number_of_rows = self.detect_max_number_of_instances()

        # Create rows scaffolding
        rows = []
        for _ in range(number_of_rows):
            rows.append([])

        # Collect column values into a row (list), convert to strings
        # and add empty instead of empty cells
        for column in self.columns[start:]:
            for counter in range(number_of_rows):
                if len(column.instances) <= counter:
                    rows[counter].append('None')
                else:
                    rows[counter].append(str(column.instances[counter]))

        return rows

    def create_table(self, rows_list=None, column_names=None, list_dict_table=None):
        self.columns = []

        if list_dict_table == None and rows_list != None:
            list_dict_table = self.get_list_dict(rows_list, column_names)
        elif list_dict_table == None and rows_list == None:
            logger.error(
                'Create table error: needed rows list or list_dict_table to create table.')

        if column_names == None:
            column_names = self.get_names_list()
        for name in column_names:
            instances = []
            for row in list_dict_table:
                if row[name] != None:
                    cell = row[name].replace('\n', '')
                    cell = cell.strip()
                    instances.append(cell)
                elif row[name] == None:
                    instances.append('')
            self.columns.append(Column(name, instances))

    def get_rows_list(self):

        rows = self.get_list_list()

        # Join columns in rows
        counter = 0
        for _ in rows:
            if rows[counter] is not None:
                row_without_none = []
                for field in rows[counter]:
                    if field is not None:
                        row_without_none.append(field)
                    else:
                        row_without_none.append('None')
                rows[counter] = row_without_none
                rows[counter] = ','.join(rows[counter])
                rows[counter] = rows[counter].replace('\n', '') + '\n'
            counter += 1

        return rows

    def add_column(self, name, instances, header=None):
        new_column = Column(name, instances)
        self.columns.append(new_column)
        if new_column.name in self.headers_dict:
            self.columns[-1].header = self.headers_dict[new_column.name]

    def insert_column(self, name, instances, col_idx):
        try:
            new_column = Column(name, instances)
            self.columns.insert(col_idx, new_column)
            if new_column.name in self.headers_dict:
                self.columns[col_idx].header = self.headers_dict[new_column.name]
        except:
            logger.error('Cannot insert a column.')

    def get_default_headers(self, number_of_columns):
        headers_list = []
        for index in range(1, number_of_columns + 1):
            headers_list.append('column_{}'.format(index))

        return headers_list

    def get_headers_list(self):
        headers_list = []
        for column in self.columns:
            if self.headers_dict != None and column.name in self.headers_dict:
                headers_list.append(self.headers_dict[column.name])
            else:
                headers_list.append(column.name)

        return headers_list

    def get_names_list(self):
        names_list = []
        idx = 0
        for name in self.indexes:
            if self.indexes[name] == idx:
                names_list.append(name)
            idx += 1

        return names_list

    def create_table_from_table(self, table):
        self.columns = []
        for column in table.columns:
            self.columns.append(column)
            if column.name in self.headers_dict:
                self.columns[-1].header = self.headers_dict[column.name]

    def update_names(self):
        names = self.get_names_list()
        indexing_range = range(min(len(names), len(self.columns)))
        for i in indexing_range:
            self.columns[i].name = names[i]

    def print_table(self, how_many_rows=None, print_separator='   '):

        rows = self.get_rows_list()
        for_print_headers = self.get_headers_list()

        # Align spaces betweenen columns if it is possible
        max_row_lenght = 0
        counter = 0
        for row in rows:
            if max_row_lenght < len(row):
                max_row_lenght = len(row)

        assumpted_console_width = 110
        if max_row_lenght < assumpted_console_width:
            # Prepare headers
            for counter in range(len(for_print_headers)):
                if len(for_print_headers[counter]) < self.columns[counter].detect_max_instance_lenght():
                    diff = self.columns[counter].detect_max_instance_lenght(
                    ) - len(for_print_headers[counter])
                    for_print_headers[counter] += ' ' * diff

            # Prepare rows
            for counter in range(len(rows)):
                rows[counter] = rows[counter].replace('\n', '')
                one_row_list = rows[counter].split(',')
                for col_idx in range(len(one_row_list)):
                    if self.columns[col_idx].detect_max_instance_lenght() < len(for_print_headers[col_idx]):
                        diff = len(
                            for_print_headers[col_idx]) - len(one_row_list[col_idx])
                        one_row_list[col_idx] += ' ' * diff
                    elif len(one_row_list[col_idx]) < self.columns[col_idx].detect_max_instance_lenght():
                        diff = self.columns[col_idx].detect_max_instance_lenght(
                        ) - len(one_row_list[col_idx])
                        one_row_list[col_idx] += ' ' * diff
                rows[counter] = ','.join(one_row_list) + '\n'

        # Print headers
        print(print_separator.join(for_print_headers))

        # Print rows
        counter = 0
        for row in rows:
            row = row.replace(',', print_separator)
            print(row, end='')
            if how_many_rows != None and counter + 1 >= how_many_rows:
                break
            counter += 1

    def save_file(self, new_file_name):
        # Save rows list without last new line transition
        rows_list = self.get_rows_list()
        with open(new_file_name, mode='w', encoding='UTF-8') as new_file:
            # Write headers
            new_file.write(','.join(self.get_headers_list()) + '\n')
            # Write rows
            for row in rows_list:
                new_file.write(row)


class CSV_gateway(CSVFile):
    def __init__(self, source, correct=False):

        if type(source) is str:
            rows_list = CSV_gateway.get_rows(source)
        else:
            rows_list = source

        separator_parameters = CSV_gateway.detect_separator(rows_list)
        if correct:
            rows_list = CSV_gateway.replace_separator(
                rows_list, separator_parameters['original_character'])
        CSVFile.__init__(self, rows_list=rows_list, headers='default')

    @staticmethod
    def get_rows(source_file_name):
        rows_list = []
        try:
            with open(source_file_name, mode='r', encoding='UTF-8-sig') as raw_file:
                for row in raw_file:
                    rows_list.append(row)
        except:
            logger.error('Cannot read a file {0}'.format(source_file_name))

        return rows_list

    @staticmethod
    def detect_separator(rows_list):
        def standard_error(number_list):
            if len(number_list) > 1:
                avg = sum(number_list) / len(number_list)
                big_sum = 0
                for num in number_list:
                    big_sum += (avg - num) * (avg - num)
                return math.sqrt(big_sum / (len(number_list) - 1))
            elif len(number_list) == 1:
                logger.error(
                    'List have only one element. Cannot obtain standard error.')
                return None
            else:
                logger.error(
                    'List have no elements. Cannot obtain standard error.')
                return None
        separators = [',', '|', '	', '.']
        separators_standard_errors = []
        separators_avarages = []
        # Calculate separators characteristics
        for sep in separators:
            separators_in_line = []
            for row in rows_list:
                separators_in_line.append(row.count(sep))
            if sum(separators_in_line) < len(rows_list):
                separators_standard_errors.append(9999)
            else:
                se = standard_error(separators_in_line)
                if se is None:
                    se = 9999
                separators_standard_errors.append(se)
            separators_avarages.append(
                round(sum(separators_in_line) / len(separators_in_line)))

        # Based on characteristics select correct separator
        counter = 0
        for se in separators_standard_errors:
            if se == 9999:
                counter += 1
        if counter == len(separators_standard_errors):
            logger.warning(
                'Cannot detect separator: default separator set (",").')
            correct_separator_index = 0
        else:
            correct_separator_index = separators_standard_errors.index(
                min(separators_standard_errors))

        separator = {}
        separator['original_character'] = separators[correct_separator_index]
        separator['number_in_line'] = separators_avarages[correct_separator_index]

        return separator

    @staticmethod
    def replace_separator(rows_list, current_separator, target_separator=','):
        rows_without_separator_list = []
        row_counter = 0
        for row in rows_list:
            if row.count(current_separator) > 0:
                rows_list[row_counter] = row.replace(
                    current_separator, target_separator)
                row_counter += 1
            else:
                rows_without_separator_list.append(row)
                row_counter += 1
        return rows_list

    @staticmethod
    def save_to_csv(new_file_name, rows_list):
        # Write cleaned content into a new csv file
        try:
            with open(new_file_name, mode='w', encoding='UTF-8') as cleaned_file:
                for element in rows_list:
                    cleaned_file.write(element)
        except:
            logger.error('Save to {} failed.'.format(new_file_name))

    @staticmethod
    def check_file_format(file_name, f_type=['.csv', '.txt']):
        if file_name[-4:] in f_type:
            return True
        else:
            return False

    @staticmethod
    def get_data_for_chart(file_path='source_file.csv', stacked=False, type_expected='float',
                           labels_column_index=0, values_columns_indexes=[1], first_row_index=1):

        labels = ['empty']
        values = [0]
        legend = []
        values_type = 'empty'

        if CSV_gateway.check_file_format(file_path) and os.path.isfile(file_path):

            table = CSV_gateway(file_path)
            # Prevent indexing beyond array
            if len(table.columns) < max(values_columns_indexes) + 1:
                values_columns_indexes = [0]
            if table.detect_max_number_of_instances() < first_row_index + 1:
                first_row_index = 0

            min_val_idx = min(values_columns_indexes)

            if stacked:
                values_columns_indexes = []
                max_val_idx = len(table.columns)

                for i in range(min_val_idx, max_val_idx+1):
                    values_columns_indexes.append(i)
            else:
                max_val_idx = max(values_columns_indexes)

            labels = table.columns[labels_column_index].instances[first_row_index:]

            if stacked:
                for column in table.columns[min_val_idx:max_val_idx+1]:
                    legend.append(column.instances[0])
            else:
                for column in table.columns[min_val_idx:max_val_idx+1]:
                    legend.append(column.instances[0])

            if stacked is False:
                # Single
                table.columns[min_val_idx].replace_empty()
                values = table.columns[min_val_idx].instances[first_row_index:]
                values_type = Column.detect_type(values)
                if values_type is 'time':
                    for i in range(len(values)):
                        values[i] = to_seconds(values[i])
            else:
                # Stacked
                for i, column in enumerate(table.columns):
                    table.columns[i].replace_empty()

                values = table.get_list_list(min_val_idx)[first_row_index:]

                # Detect type
                types_list = []
                for i in range(len(values)):
                    types_list.append(Column.detect_type(values[i]))

                if all([typo is 'float' or typo is 'int' for typo in types_list]):
                    values_type = 'float'
                    for i in range(len(values)):
                        for j in range(len(values[i])):
                            values[i][j] = float(values[i][j])
                else:
                    values_type = 'string'

        elif os.path.isfile(file_path):
            values_type = 'binary'

        if values_type == 'string':
            labels = ['Provided values are inappriopriate.']
            values = [0]
        elif values_type is 'binary':
            labels = ['Only .csv or .txt formats are allowed.',
                      'Inappropriate file type.']
            values = [0, 0]
        elif len(values) != len(labels):
            labels = ['Lenght of values list is not equal lenght of names list']
            values = [0]
        elif not os.path.isfile(file_path):
            labels = ['File not found.']
            values = [0]

        return labels, values, legend, values_type


class Column:
    name = None
    header = None
    content_type = None
    type_without_headers = None
    instances = None
    treshold_type = None
    header_first_row = False

    def __init__(self, name, instances, header=None, convert=False, replace_empty=True):
        self.name = name
        if header == None:
            self.header = name
        else:
            self.header = header
        self.instances = instances

        if replace_empty:
            self.replace_empty(without_first_row=True)
        self.type_without_headers = Column.detect_type(self.instances[1:])
        self.content_type = Column.detect_type(self.instances)

        if self.type_without_headers != self.content_type:
            self.header_first_row = True

            if replace_empty:
                self.replace_empty()

        if convert:

            min_range = 0

            if self.content_type is self.type_without_headers:
                convert_type = self.content_type
            elif self.type_without_headers != 'string':
                convert_type = self.type_without_headers
                min_range = 1

            for i in range(min_range, len(self.instances)):
                if convert_type is 'int':
                    self.instances[i] = int(self.instances[i])
                elif convert_type is 'float':
                    self.instances[i] = float(self.instances[i])

    def replace_empty(self, without_first_row=False):
        '''Replace empty fields with zeros'''
        if self.header_first_row or without_first_row:
            start = 1
        else:
            start = 0

        for i, instance in enumerate(self.instances[start:]):
            if instance is '':
                self.instances[i + start] = '0'

    @staticmethod
    def detect_type(instances):
        int_pattern = r'[0-9]+$'
        float_pattern = r'[0-9]+\.?[0-9]+$'
        datetime_pattern = r'[0-9]{4}-[0-9]{2}-[0-9]{2} [0-9]{2}:[0-9]{2}:[0-9]{2}$'
        time_pattern = r'[0-9]{1,}:[0-9]{2}:[0-9]{2}$'
        column_type = ''
        none_counter = 0
        int_counter = 0
        float_counter = 0
        datetime_counter = 0
        time_counter = 0
        for instance in instances:
            if type(instance) is not str:
                instance = str(instance)

            if instance == None:
                none_counter += 1
            elif re.match(int_pattern, instance):
                int_counter += 1
            elif re.match(datetime_pattern, instance):
                datetime_counter += 1
            elif re.match(time_pattern, instance):
                time_counter += 1
            elif re.match(float_pattern, instance):
                float_counter += 1
            else:
                pass

        lenght = len(instances)

        if int_counter + none_counter == lenght:
            column_type = 'int'
        elif datetime_counter + none_counter == lenght:
            column_type = 'datetime'
        elif time_counter + none_counter == lenght:
            column_type = 'time'
        elif float_counter + none_counter + int_counter == lenght:
            column_type = 'float'
        else:
            column_type = 'string'

        return column_type

    def detect_max_instance_lenght(self):
        maximum = 0
        for instance in self.instances:
            if instance != None and maximum < len(instance):
                maximum = len(instance)
            elif instance == None and maximum < len(self.header):
                maximum = len(self.header)

        return maximum

# Standard library imports

from datetime import timedelta
from colorsys import rgb_to_hsv

# Kivy imports

from kivy.core.window import Window
from kivy.graphics import Color, Line, Rectangle
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.widget import Widget
from kivy.uix.scrollview import ScrollView
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import BooleanProperty, NumericProperty


class Chart(Widget):
    font_width_ratio = 0.67
    font_name = 'RobotoMono-Regular'
    hints = {'left': 0.01, 'right': 0.02, 'bottom': 0.01, 'top': 0.01}
    mid_space_factor = 0.01
    h_axis_height_factor = 0.05
    legend_area_height = 0.05
    title_area_height = 0.05
    minimal_height = 300
    minimal_width = 100
    min_font_size = NumericProperty(16)

    def __init__(self):
        super().__init__()


class Hbarchart(Chart):
    grid_widget = None
    max_label_lenght = 63
    black = BooleanProperty(True)
    grid = BooleanProperty(True)
    stacked_colors = [(0.1, 0.5, 0), (0.38, 0.59, 0),
                      (0.6, 0.62, 0), (204, 164, 0), (1, 0.65, 0)]
    one_color = [(1, 0, 0)]
    grid_counter = 0
    unit = '-'
    slices = 11
    time = False
    lang_dict = {'day': 'day', 'days': 'days'}
    legend = []
    title = ''
    values = [['0']]
    labels = ['label']
    pareto = False
    pareto_color_ads = [0.5, 0.2, 0.0]
    pareto_limits = [0.70, 0.90, 1.00]
    pareto_labels = ['(70%)', '(20%)', '(10%)']

    def __init__(self, **kwargs):
        '''
        values = ['0'] (or values = [[], [], ..., []]), labels = ['label'],
        hints = {'left': 0.01, 'right': 0.02, 'bottom': 0.01, 'top': 0.01}
        mid_space_factor = 0.01, h_axis_height_factor = 0.05,
        legend_area_height = 0.05, title_area_height = 0.05, unit = '-', 
        slices = 11, time = False, lang_dict = {'day': 'day', 'days': 'days'},
        legend = []
        '''
        super(Hbarchart, self).__init__()

        self.bind(size=self.new)
        self.bind(black=self.toggle_colors)
        self.bind(grid=self.toggle_grid)

        self.new(self, **kwargs, init=True)

    def new(self, *args, **kwargs):
        '''
        values = ['0'] (or values = [[], [], ..., []]), labels = ['label'],
        hints = {'left': 0.01, 'right': 0.02, 'bottom': 0.01, 'top': 0.01}
        mid_space_factor = 0.01, h_axis_height_factor = 0.05,
        legend_area_height = 0.05, title_area_height = 0.05, unit = '-', 
        slices = 11, time = False, lang_dict = {'day': 'day', 'days': 'days'}, 
        legend = []
        '''
        if not 'init' in kwargs or 'init' in kwargs and not kwargs['init']:
            self.clear_widgets()
            self.canvas.clear()

        if 'values' in kwargs:
            self.values = kwargs.pop('values')
        if 'labels' in kwargs:
            self.labels = kwargs.pop('labels')
        if 'hints' in kwargs:
            self.hints = kwargs.pop('hints')
        if 'h_axis_height_factor' in kwargs:
            self.units_area_factors = kwargs.pop('h_axis_height_factor')
        if 'legend_area_height' in kwargs:
            self.legend_area_height = kwargs.pop('legend_area_height')
        if 'title_area_height' in kwargs:
            self.title_area_height = kwargs.pop('title_area_height')
        if 'unit' in kwargs:
            self.unit = kwargs.pop('unit')
        if 'slices' in kwargs:
            self.slices = kwargs.pop('slices')
        if 'time' in kwargs:
            self.time = kwargs.pop('time')
        if 'lang_dict' in kwargs:
            self.lang_dict = kwargs.pop('lang_dict')
        if 'legend' in kwargs:
            self.legend = kwargs.pop('legend')
        if 'title' in kwargs:
            self.title = kwargs.pop('title')
        if 'min_font' in kwargs:
            self.min_font_size = kwargs.pop('min_font')
        if 'pareto' in kwargs:
            self.pareto = kwargs.pop('pareto')

        self._hbarchart()

    def _hbarchart(self):
        # General actions
        self._prepare_data()
        self._get_parameters()

        if self.parent:
            # Draw chart
            self._draw_background()
            self._draw_grid()
            self._draw_record_labels()
            self._draw_rectangles()
            self._draw_legend()
            self._draw_title()

    def _get_parameters(self):
        # Calculate chart cords
        self.cords = {}
        self.cords['x'] = self.pos[0] + self.hints['left'] * self.size[0]
        self.cords['y'] = self.pos[1] + self.hints['bottom'] * self.size[1]
        self.cords['x2'] = self.pos[0] + \
            self.size[0] * (1 - self.hints['right'])
        self.cords['y2'] = self.pos[1] + self.size[1] * (1 - self.hints['top'])

        # Calculate spaces
        self.middle_space = self.size[0] * self.mid_space_factor
        self.axis_labels_space = self.size[1] * self.h_axis_height_factor
        self.top_extra_hints = 0

        if len(self.legend) > 0:
            self.top_extra_hints += self.legend_area_height * self.size[1]
        if len(self.title) > 0:
            self.top_extra_hints += self.title_area_height * self.size[1]

        self.drawing_height = self.cords['y2'] - self.cords['y'] \
            - self.axis_labels_space - self.top_extra_hints

        # Calculate records height
        number_of_records = max(len(self.labels), len(self.values))

        if number_of_records is 1:
            self.record_height = 0.25 * self.drawing_height
        else:
            self.record_height = self.drawing_height / number_of_records
        self.rect_height = self.record_height * 0.75

        # Calculate minimal widget size
        self.minimal_height = max(
            self.min_font_size * number_of_records * 1.35,
            300)

        self.minimal_width = max(
            self.min_font_size * self.font_width_ratio
            * self.max_label_lenght * 1.85, 100)

        # Calculate input font parameters
        self.records_font_size = min(
            self.size[1] * 0.1, self.record_height - 1)
        if len(self.labels) is 0:
            self.greatest_char_count = 0
        else:
            self.greatest_char_count = max(
                [len(label) for label in self.labels])
        self.max_label_width = 0.5 * self.size[0]

        # Calculate font size
        for i in range(int(self.records_font_size)):
            actual_label_width = self.font_width_ratio * self.records_font_size \
                * self.greatest_char_count
            if actual_label_width <= self.max_label_width:
                break
            else:
                self.records_font_size -= i

        # Calculate labels width
        self.labels_width = self.font_width_ratio * \
            self.records_font_size * self.greatest_char_count

        # General font size
        approximate_unit_area_width = max(
            0.05 * self.size[0],
            3 * self.min_font_size * self.font_width_ratio)
        drawing_width = self.cords['x2'] + approximate_unit_area_width \
            - self.cords['x'] - self.labels_width - self.middle_space
        self.general_font_size = max(
            min(drawing_width * 0.03, self.drawing_height * 0.02),
            self.min_font_size)

        # Unit area width
        self.unit_with_brackets = '[{}]'.format(self.unit)
        self.unit_area_width = len(
            self.unit_with_brackets) * self.general_font_size

        # Calculate drawing cords
        self.drawing_cords = {}
        self.drawing_cords['x'] = self.cords['x'] + self.labels_width \
            + self.middle_space
        self.drawing_cords['y'] = self.cords['y'] + self.axis_labels_space
        self.drawing_cords['x2'] = self.cords['x2'] - self.unit_area_width
        self.drawing_cords['y2'] = self.cords['y2'] - self.top_extra_hints

        # Other calculations
        self.general_labels_height = self.general_font_size + 1
        self.pixels_per_character = self.general_font_size * self.font_width_ratio

    def _prepare_data(self):
        # Convert labels to string and trim too long ones
        for i, label in enumerate(self.labels):
            self.labels[i] = str(self.labels[i])
            if len(label) > self.max_label_lenght:
                self.labels[i] = self.labels[i][:self.max_label_lenght - 3] + '...'

        if not self.time:

            if type(self.values[0]) is list:
                for i, row in enumerate(self.values):
                    for j, value in enumerate(row):
                        self.values[i][j] = float(value)
            else:
                for i, value in enumerate(self.values):
                    self.values[i] = float(value)

    def _draw_record_labels(self):
        # Draw record labels
        x_start = self.pos[0] + self.hints['left'] * self.size[0]
        rectangle_labels = Widget()
        for i in range(len(self.labels)):
            label = Label(text=self.labels[i],
                          pos=(x_start,
                               self.drawing_cords['y'] + self.record_height * i),
                          size=(self.labels_width, self.rect_height),
                          halign='right',
                          valign='middle',
                          font_size='{}sp'.format(self.records_font_size),
                          font_name=self.font_name,
                          text_size=(self.labels_width, self.record_height),
                          color=self.contour_color)
            rectangle_labels.add_widget(label)
        self.add_widget(rectangle_labels)

    def _draw_rectangles(self):
        # Draw rectangles
        with self.canvas:
            value_list_lenght = len(self.values)

            # Detect value of longest bar
            max_value = 0
            bar_values = []
            for i in range(value_list_lenght):
                if type(self.values[i]) is list:
                    bar_value = sum(self.values[i])
                else:
                    bar_value = self.values[i]
                if bar_value > max_value:
                    max_value = bar_value
                bar_values.append(bar_value)

            # Iterate by record
            aggregated_column_share = 0
            sum_of_values = sum(bar_values)
            for i in range(value_list_lenght):
                # Calculate bar width
                max_rect_width = \
                    self.drawing_cords['x2'] - self.drawing_cords['x']
                if max_value > 0:
                    bar_width = max_rect_width * bar_values[i] / max_value
                else:
                    bar_width = 0

                if type(self.values[i]) is list:
                    no_of_slices = len(self.values[i])
                else:
                    if max_value > 0:
                        percentage_column_share = bar_values[i] / sum_of_values
                        aggregated_column_share += percentage_column_share
                    else:
                        percentage_column_share = 0

                    no_of_slices = 1

                    if self.pareto:
                        if aggregated_column_share <= self.pareto_limits[0]:
                            add = self.pareto_color_ads[0]
                        elif aggregated_column_share <= self.pareto_limits[1]:
                            add = self.pareto_color_ads[1]
                        elif aggregated_column_share > self.pareto_limits[1]:
                            add = self.pareto_color_ads[2]
                    else:
                        add = 0.5

                    # Color
                    color = rgb_to_hsv(*self.one_color[0])
                    Color(color[0],
                          (0.5 + add),
                          color[2],
                          mode='hsv')

                # Iterate by slice
                done_width = 0
                slice_width = bar_width
                for j in range(no_of_slices):
                    if no_of_slices > 1:
                        if bar_values[i] > 0:
                            slice_width = self.values[i][j] / \
                                bar_values[i] * bar_width
                        else:
                            slice_width = 0

                        # Color
                        if no_of_slices is 2:
                            if j is 0:
                                Color(*self.stacked_colors[0])
                            else:
                                Color(*self.stacked_colors[2])
                        else:
                            Color(*self.stacked_colors[j % 5])

                    Rectangle(pos=(self.drawing_cords['x'] + done_width,
                                   self.drawing_cords['y'] + self.record_height * i),
                              size=(slice_width, self.rect_height))

                    done_width += slice_width

    def _draw_background(self):
        # Draw background color
        if self.black:
            self.background_color = [0, 0, 0, 1]
            self.contour_color = [1, 1, 1, 1]
        else:
            self.background_color = [1, 1, 1, 1]
            self.contour_color = [0, 0, 0, 1]
        with self.canvas:
            Color(*self.background_color)
            Rectangle(size=self.size, pos=self.pos)

    def _draw_grid(self):
        # Draw grid
        if self.grid and self.grid_widget not in self.children:
            self.grid_widget = Widget()
            chart_width = self.drawing_cords['x2'] - self.drawing_cords['x']

            # Add markers
            with self.grid_widget.canvas:
                Color(*self.contour_color)
                # Add horizontal axis
                Line(bezier=(self.drawing_cords['x'], self.drawing_cords['y'],
                             self.drawing_cords['x2'], self.drawing_cords['y']))
                # Add frame
                Line(points=(self.drawing_cords['x'], self.drawing_cords['y'],
                             self.drawing_cords['x'], self.drawing_cords['y2'],
                             self.drawing_cords['x2'], self.drawing_cords['y2'],
                             self.drawing_cords['x2'], self.drawing_cords['y']))

                # Add vertical lines
                for i in range(self.slices + 1):
                    increment = chart_width / self.slices * i
                    Line(points=(
                        self.drawing_cords['x'] + increment, self.drawing_cords['y'] -
                        self.drawing_height * 0.01,
                        self.drawing_cords['x'] + increment, self.drawing_cords['y2']))

            # Add grid values

            axis_tick_label_pixels = []
            axis_tick_labels = []

            if type(self.values[0]) is list:
                max_val = max([sum(instance) for instance in self.values])
            else:
                max_val = max(self.values)

            # Calculate tick label value with correct precision
            counter = 0
            label_values = []
            precision = 0
            while counter <= self.slices:
                if precision == 0:
                    label_value = round(max_val / self.slices * counter)
                else:
                    label_value = round(
                        max_val / self.slices * counter, precision)
                if max_val > 0:
                    if label_value in label_values:
                        precision += 1
                        counter = 0
                        label_values = []
                    else:
                        label_values.append(label_value)
                        counter += 1
                else:
                    label_values.append(label_value)
                    counter += 1

            for i in range(self.slices + 1):
                label_value = label_values[i]
                # If label is a time type translate to timedelta
                if self.time:
                    label_value = self.seconds_to_timedelta(label_value)

                label_value = str(label_value)

                if self.lang_dict.values is not {'day', 'days'}:
                    # Translate period names into other language
                    label_value = label_value.replace(
                        'days', self.lang_dict['days'])
                    label_value = label_value.replace(
                        'day', self.lang_dict['day'])

                axis_tick_labels.append(label_value)

                # Calculate label lenght in pixels and add to list
                axis_tick_label_pixels.append(
                    len(axis_tick_labels[i]) * self.pixels_per_character)

            max_lab_lenght = max(axis_tick_label_pixels)
            val_start_pos = (self.drawing_cords['x'],
                             self.drawing_cords['y'] - self.drawing_height * 0.03)
            increment = 0

            # Decide whether vertical offset is needed
            if max_lab_lenght > 0.8 * chart_width / self.slices:
                v_offset = self.general_font_size
            else:
                v_offset = 0

            for i in range(self.slices + 1):
                increment = chart_width / self.slices * i

                label_value = Label(
                    text='{}'.format(axis_tick_labels[i]),
                    pos=(val_start_pos[0] + increment - axis_tick_label_pixels[i] / 2,
                         val_start_pos[1] - (i % 2) * v_offset),
                    size=(axis_tick_label_pixels[i],
                          self.general_labels_height),
                    font_size='{}sp'.format(self.general_font_size),
                    font_name=self.font_name,
                    text_size=(
                        axis_tick_label_pixels[i], self.general_font_size),
                    halign='center',
                    valign='center',
                    color=self.contour_color)
                self.grid_widget.add_widget(label_value)

            # Add unit
            if not v_offset or (self.slices + 1) % 2:
                unit_v_offset = self.general_font_size
            else:
                unit_v_offset = 0

            unit_pos = (self.drawing_cords['x2'] + self.unit_area_width / 2,
                        val_start_pos[1] - unit_v_offset)
            unit_label = Label(text=self.unit_with_brackets,
                               pos=unit_pos,
                               size=(self.unit_area_width,
                                     self.general_labels_height),
                               halign='center',
                               valign='center',
                               font_size='{}sp'.format(self.general_font_size),
                               font_name=self.font_name,
                               text_size=(self.unit_area_width,
                                          self.general_labels_height),
                               color=self.contour_color)
            self.grid_widget.add_widget(unit_label)

            self.add_widget(self.grid_widget)

    def _draw_legend(self):
        if len(self.legend) > 0:
            self.legend_widget = Widget()

            if len(self.legend) is 1:
                colors = list(self.one_color)
            else:
                colors = list(self.stacked_colors)

            for i in range(len(colors)):
                colors[i] = rgb_to_hsv(*colors[i])

            new_legend = []
            new_colors = []
            if self.pareto and len(self.legend) is 1:

                for i in range(3):
                    new_legend.append(
                        '{} {}'.format(self.legend[0], self.pareto_labels[i]))
                    new_colors.append((colors[0][0], 0.5 + self.pareto_color_ads[i],
                                       colors[0][2]))
            else:
                new_legend = self.legend
                new_colors = colors

            chart_width = self.drawing_cords['x2'] - self.drawing_cords['x']
            legend_level = self.drawing_cords['y2'] + 0.01 * self.size[1]
            one_character_width = self.general_font_size * self.font_width_ratio
            legend_lenght = len(new_legend)
            after_label_offset = chart_width * 0.015
            before_label_offset = one_character_width
            max_stripe_lenght = 0.1 * chart_width
            center = self.drawing_cords['x'] + chart_width / 2

            all_after_offset = (legend_lenght - 1) * after_label_offset
            all_before_offset = legend_lenght * before_label_offset
            all_offset = all_after_offset + all_before_offset

            label_widths = []
            total_labels_width = 0
            for i in range(legend_lenght):
                width = one_character_width * len(new_legend[i])
                label_widths.append(width)
                total_labels_width += width

            space_for_stripes = chart_width - total_labels_width - all_offset

            space_for_one_stripe = space_for_stripes / legend_lenght
            if space_for_one_stripe > max_stripe_lenght:
                space_for_one_stripe = max_stripe_lenght

            space_for_stripes = space_for_one_stripe * legend_lenght
            stripes_and_labels = space_for_stripes + total_labels_width

            centered_start_pos = center - (stripes_and_labels + all_offset) / 2

            with self.legend_widget.canvas:
                current_offset = 0
                for i in range(legend_lenght):
                    ii = i % 5
                    Color(*new_colors[ii], mode='hsv')
                    Rectangle(pos=(centered_start_pos + current_offset,
                                   legend_level),
                              size=(space_for_one_stripe, self.general_labels_height))

                    self.legend_widget.add_widget(
                        Label(text=new_legend[i],
                              pos=(centered_start_pos + current_offset
                                   + space_for_one_stripe + one_character_width,
                                   legend_level),
                              size=(label_widths[i],
                                    self.general_labels_height),
                              font_name=self.font_name,
                              font_size='{}sp'.format(self.general_font_size),
                              color=self.contour_color))

                    current_offset += space_for_one_stripe + label_widths[i] \
                        + after_label_offset + before_label_offset

            self.add_widget(self.legend_widget)

    def _draw_title(self):
        title_lenght = len(self.title)

        if title_lenght:
            if len(self.legend):
                y = self.drawing_cords['y2'] + \
                    self.legend_area_height * self.size[1]
            else:
                y = self.drawing_cords['y2']

            title_width = self.drawing_cords['x2'] - self.drawing_cords['x']

            title_height = self.font_width_ratio * self.records_font_size
            self.title_font_size = self.general_font_size * 1.5
            self.title_labels_height = self.title_font_size + 1

            self.one_character_width = self.font_width_ratio * self.title_font_size
            max_title_lenght = round(
                title_width / self.one_character_width) - 3

            if title_lenght > max_title_lenght:
                title = self.title[:(max_title_lenght + 1)] + '...'
            else:
                title = self.title

            title = Label(text=title,
                          pos=(self.drawing_cords['x'], y),
                          size=(title_width, self.title_labels_height),
                          font_size=self.title_font_size,
                          font_name=self.font_name,
                          color=self.contour_color)

            self.add_widget(title)

    def toggle_grid(self, *args):
        if not self.grid and self.grid_widget in self.children:
            self.remove_widget(self.grid_widget)
        elif self.grid and self.grid_widget not in self.children:
            self.grid_widget = None
            self._draw_grid()
            overdraw_limit = 5
            if self.grid_counter < overdraw_limit:
                self._draw_rectangles()
                self.grid_counter += 1
            else:
                self.new()
                self.grid_counter = 0

    def toggle_colors(self, *args):
        # Draw chart
        self.clear_widgets()
        self.canvas.clear()
        self._draw_background()
        self._draw_grid()
        self._draw_record_labels()
        self._draw_rectangles()
        self._draw_legend()
        self._draw_title()

    # Auxiliary methods

    @staticmethod
    def seconds_to_timedelta(seconds):
        '''Convert seconds (int or float) into timedelta object'''
        timedelta_object = timedelta(seconds=seconds)
        return timedelta_object


class Hbarchart_With_Scroll(ScrollView):

    def __init__(self, *args, **kwargs):
        '''
        values = ['0'] (or values = [[], [], ..., []]), labels = ['label'],
        hints = {'left': 0.01, 'right': 0.02, 'bottom': 0.01, 'top': 0.01}
        mid_space_factor = 0.01, h_axis_height_factor = 0.05,
        legend_area_height = 0.05, title_area_height = 0.05, unit = '-', 
        slices = 11, time = False, lang_dict = {'day': 'day', 'days': 'days'}, 
        legend = []
        '''
        super(Hbarchart_With_Scroll, self).__init__()
        self.bind(size=self.resize)
        self.new(**kwargs)

    def new(self, *args, **kwargs):
        '''
        values = ['0'] (or values = [[], [], ..., []]), labels = ['label'],
        hints = {'left': 0.01, 'right': 0.02, 'bottom': 0.01, 'top': 0.01}
        mid_space_factor = 0.01, h_axis_height_factor = 0.05,
        legend_area_height = 0.05, title_area_height = 0.05, unit = '-', 
        slices = 11, time = False, lang_dict = {'day': 'day', 'days': 'days'}, 
        legend = []
        '''

        if len(self.children) > 0:
            self.chart.new(**kwargs, min_font=self.get_min_font())
            self.box.clear_widgets()
            self.box.size = (self.get_chart_width(), self.get_chart_height())
            self.box.add_widget(self.chart)
        else:
            self.chart = Hbarchart(**kwargs, min_font=self.get_min_font())
            self.box = BoxLayout(size_hint_y=None,
                                 size_hint_x=None,
                                 height=self.get_chart_height(),
                                 width=self.get_chart_width())
            self.box.add_widget(self.chart)
            self.add_widget(self.box)

    def resize(self, *args):
        # Change dimension only when is inappropriate

        correct_heigth = self.get_chart_height()
        if self.box.height is not correct_heigth:
            self.box.height = correct_heigth

        correct_width = self.get_chart_width()
        if self.box.width is not correct_width:
            self.box.width = correct_width
        
        self.scroll_wheel_distance = 0.15 * self.box.height

    def get_min_font(self):
        min_font = int(self.size[1] * 0.013)
        if min_font < 10:
            min_font = 10
        return min_font

    def get_chart_height(self):
        return max(self.size[1], self.chart.minimal_height)

    def get_chart_width(self):
        return max(self.size[0], self.chart.minimal_width)


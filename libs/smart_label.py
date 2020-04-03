from kivy.uix.label import Label
from kivy.properties import NumericProperty


class SmartLabel(Label):

    prefered_font_size = NumericProperty(16)

    def on_size(self, *args, **kwarg):
        self.text_size = self.size
        self.halign = 'center'
        self.valign = 'center'

        font_ratio = 0.8
        safety_first = 2

        widget_height = self.size[1]
        widget_width = self.size[0]
        no_of_charts = len(self.text)
        no_of_levels = widget_height / self.font_size
        label_lenght = no_of_charts * self.font_size * \
            font_ratio / no_of_levels * safety_first
        new_font_size = self.font_size

        if label_lenght >= (widget_width - font_ratio * new_font_size) \
                or new_font_size > self.prefered_font_size:
            # Decrease
            while label_lenght > (widget_width - font_ratio * new_font_size) \
                or new_font_size > self.prefered_font_size:
                new_font_size -= 1
                no_of_levels = widget_height / new_font_size
                label_lenght = no_of_charts * new_font_size * \
                    font_ratio / no_of_levels * safety_first

        elif label_lenght < (widget_width - font_ratio * new_font_size) \
                and new_font_size < self.prefered_font_size:
            # Increase
            while label_lenght < (widget_width - font_ratio * new_font_size) \
                    and new_font_size < self.prefered_font_size:
                new_font_size += 1
                no_of_levels = widget_height / new_font_size
                label_lenght = no_of_charts * new_font_size * \
                    font_ratio / no_of_levels * safety_first

        self.font_size = new_font_size

    def on_prefered_font_size(self, *args, **kwargs):
        self.on_size()

'''
Chart viewer
=====================
Kivy based charting app.

'''

# Python standard library imports
import os

# Kivy imports (third party imports)
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.core.window import Window
from kivy.uix.widget import Widget
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.lang import Builder
from kivy.properties import StringProperty
from kivy.uix.popup import Popup
from kivy.config import Config

# Local application imports
from libs.csvfile import CSV_gateway
from libs.kv_chart import Hbarchart_With_Scroll
from libs.main_backend import short, get_save_path
from libs.smart_label import SmartLabel


class SmartButton(Button, SmartLabel):
    pass


class ChooseFile(Popup):
    pass


class SavePopup(Popup):
    description = StringProperty()


class ChartViewer(App):
    chart_widget = None
    source = {'hbarchart': 'hbarchart_test.csv', 'stacked': 'stacked_test.csv'}
    chart_type = 'empty'
    chart_under_change = 'empty'
    save = False
    last_button = None
    active_button_color = [0, 0, 0, 1]
    idle_button_color = [1, 1, 1, 1]

    # region sourcefile
    def select(self, directory_path, selection):

        # Save
        if self.save:
            if self.chart_widget:
                save_path = get_save_path(self.chart_type, directory_path)
                self.chart_widget.export_to_png(save_path)
                self.save = False

                if directory_path is '.':
                    path_text = f'Screenshot has been saved as "{short(save_path)}"'\
                        '\nin the same directory as "main.py" file.'
                else:
                    path_text = f'Screenshot has been saved as "{short(save_path)}"'\
                        f'\nin {directory_path} directory.'
            else:
                path_text = 'There is no chart to save.'

            SavePopup(description=path_text).open()

        # Select
        else:
            if len(selection) is not 0:
                self.source[self.chart_under_change] = selection[0]
                self.root.ids[self.chart_under_change].text = short(
                    self.source[self.chart_under_change])
                self.change_button_color(None)
                self.print_chart(self.chart_under_change)

    def choose_file(self, chart_type):
        self.chart_under_change = chart_type
        ChooseFile().open()

    # endregion sourcefile

    def change_button_color(self, args):
        button_names = ['hbarchart_button', 'stacked_button']
        size_difference = 10

        if self.chart_under_change is 'empty' or args is not None and \
                hasattr(args[0], 'name') and args[0].name in button_names:

            button = args[0]
        else:
            button = self.root.ids[self.chart_under_change + '_button']

        if self.last_button is None:
            button.background_color = self.active_button_color
            button.prefered_font_size += size_difference
        elif self.last_button is not None and self.last_button.text != button.text:
            button.background_color = self.active_button_color
            button.prefered_font_size += size_difference
            self.last_button.background_color = self.idle_button_color
            self.last_button.prefered_font_size -= size_difference
        self.last_button = button

    def print_chart(self, which):
        self.chart_type = which
        if self.chart_type is 'stacked':
            labels, values, legend, values_type = CSV_gateway.get_data_for_chart(
                self.source[self.chart_type], stacked=True)
            title = 'stacked_chart'
        else:
            labels, values, legend, values_type = CSV_gateway.get_data_for_chart(
                self.source[self.chart_type])
            title = 'horizontal_barchart'

        if values_type == 'time':
            time = True
        else:
            time = False

        if not self.chart_widget:
            self.chart_widget = Hbarchart_With_Scroll(
                values=values, labels=labels, time=time, legend=legend, title=title)
            self.root.children[0].add_widget(self.chart_widget)
        else:
            self.chart_widget.new(
                values=values, labels=labels, time=time, legend=legend, title=title)

    def save_chart(self):
        self.save = True
        ChooseFile(title='Choose save directory').open()

    def end_save(self):
        self.save = False

    def grid_and_color(self, color=False):
        if self.chart_widget is not None:
            if color:
                self.chart_widget.chart.black = not(
                    self.chart_widget.chart.black)
            else:
                self.chart_widget.chart.grid = not(
                    self.chart_widget.chart.grid)

    def build(self):
        Config.set('input', 'mouse', 'mouse,multitouch_on_demand')
        Window.maximize()
        root_widget = Builder.load_file('libs/gui.kv')
        return root_widget


if __name__ == '__main__':
    ChartViewer().run()

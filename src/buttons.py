# import datetime
# import timeit

# #kivy関連import
# from kivy.app import App   
# from kivy.uix.button import Button
# from kivy.uix.popup import Popup
# from kivy.uix.boxlayout import BoxLayout
# from kivy.uix.gridlayout import GridLayout
# from kivy.graphics import Color, Line
# from kivy.core.audio import SoundLoader
# from kivy.properties import ObjectProperty, StringProperty, ListProperty
# from kivy.utils import platform
# from kivy.clock import Clock
# from kivy.config import Config
# Config.set('kivy', 'log_level', 'debug')
# import japanize_kivy
# from camera4kivy import Preview
# try:from android.permissions import request_permissions, Permission, check_permission
# except:pass

# from src import config_manager

# DOUBLE_TAP_TIME = 0.2   # Change time in seconds
# LONG_PRESSED_TIME = 0.3  # Change time in seconds



# class ButtonGrid(GridLayout):
#     camera_preview = ObjectProperty(None)
#     buttongrid = ObjectProperty(None)

#     def __init__(self, **kwargs):
#         super(ButtonGrid, self).__init__(**kwargs)
    
    
#     def on_parent(self, instance, value):
#         self.refreshAndSwitchButtonSet()

    
#     def refreshAndSwitchButtonSet(self, mode=None):
#         offset=0
#         current_buttons = [int(bc.custom_id.replace('btn','')) for bc in self.children]
#         if len(current_buttons):offset += max(current_buttons)+1
#         try:config_manager.settings[f'btn{max(current_buttons)+1}']
#         except:offset=0
#         if not mode:
#             try:offset = min(current_buttons)
#             except:offset=0
#         self.clear_widgets()
#         try:
#             for i in range(12):
#                 n = i + offset
#                 btn = ATButton(custom_id=f'btn{n}',
#                             text = '['+str(config_manager.settings[f'btn{n}']['num'])+']\n'+config_manager.settings[f'btn{n}']['name']
#                             )
#                 btn.bind(on_single_press=lambda btn_instance=btn: self.camera_preview.capture_button(btn_instance))
#                 btn.bind(on_long_press=lambda btn_instance=btn: self.camera_preview.popup_open(btn_instance))
#                 self.add_widget(btn)
#         except:pass

#     def test_children(self):
#         current_buttons = [int(bc.custom_id.replace('btn','')) for bc in self.children]
#         print(current_buttons)




# class ATButton(Button):
#     def __init__(self,
#                  custom_id='btn0', 
#                  text='ボタン', 
#                  font_size=35, 
#                  background_color= (1,1,1,0),
#                  halign= 'center',
#                  **kwargs):
        
#         super(ATButton, self).__init__(**kwargs)

#         # デフォルト値を読み込み
#         self.custom_id = custom_id
#         self.text = text
#         self.font_size = font_size
#         self.background_color= background_color
#         self.halign= halign

#         # 文字色変更用
#         self.color_index = 0
#         self.colors = [(0, 0, 0, .7), (1, 0, 0, .7), (1, 1, 1, .7), (1, 1, 1, 0)]  # 黒, 赤, 白
#         self.color = self.colors[self.color_index]
#         Clock.schedule_interval(self.update_color, 1/4)  # 1秒ご

#         # 長押しを実装
#         self.start = 0
#         self.single_hit = 0
#         self.press_state = False
#         self.register_event_type('on_single_press')
#         self.register_event_type('on_double_press')
#         self.register_event_type('on_long_press')

    
#     def update_color(self, *args):
#         self.color_index = (self.color_index + 1) % 4
#         self.color = self.colors[self.color_index]

#     def on_touch_down(self, touch):
#         if self.collide_point(touch.x, touch.y):
#             self.start = timeit.default_timer()
#             if touch.is_double_tap:
#                 self.press_state = True
#                 self.single_hit.cancel()
#                 self.dispatch('on_double_press')
#         else:
#             return super(ATButton, self).on_touch_down(touch)

#     def on_touch_up(self, touch):
#         if self.press_state is False:
#             if self.collide_point(touch.x, touch.y):
#                 stop = timeit.default_timer()
#                 awaited = stop - self.start

#                 def not_double(time):
#                     nonlocal awaited
#                     if awaited > LONG_PRESSED_TIME:
#                         self.dispatch('on_long_press')
#                     else:
#                         self.dispatch('on_single_press')

#                 self.single_hit = Clock.schedule_once(not_double, DOUBLE_TAP_TIME)
#             else:
#                 return super(ATButton, self).on_touch_down(touch)
#         else:
#             self.press_state = False

#     def on_single_press(self):
#         print('single')
#         pass

#     def on_double_press(self):
#         print('double')
#         pass

#     def on_long_press(self):
#         print('long')
#         pass

# class PopupMenu(BoxLayout):
#     popup_text = ListProperty()
#     update_setting = ObjectProperty(None)
#     popup_close = ObjectProperty(None)



from kivy.lang import Builder
from kivy.uix.screenmanager import Screen
from kivy.uix.popup import Popup
from kivy.uix.label import Label
import os
from telegraph import Telegraph, exceptions, upload_file
from PIL import Image
from threading import Thread
from kivy.clock import Clock
from kivy.clock import mainthread
from kivy.uix.button import Button
from kivy.core.clipboard import Clipboard
from kivymd.app import MDApp
from kivy.uix.boxlayout import BoxLayout
import natsort
def convert_file_to_image(file):
    ext = os.path.splitext(file)[1].lower()
    if ext not in [".png", ".gif", ".jpg", ".jpeg"]:
        image = Image.open(file)
        new_file = os.path.splitext(file)[0] + ".png"
        image.save(new_file)
        return new_file
    else:
        return file

class ProgressScreen(Screen):
    pass

class WelcomeScreen(Screen):
    pass

class UploadScreen(Screen):
    pass

class SettingsScreen(Screen):
    pass

class ArticleScreen(Screen):
    pass

class MainApp(MDApp):
    def build(self):
        self.screen_history = []
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "Blue"
        self.article_settings = {"author": "", "title": "", "link": ""}
        screen = Builder.load_string('''
ScreenManager:
    WelcomeScreen:
    UploadScreen:
    ProgressScreen:
    ArticleScreen:
    SettingsScreen:

<WelcomeScreen>:
    name: 'welcome'
    MDBoxLayout:
        orientation: 'vertical'
        MDToolbar:
            title: 'Telegraph Uploader'
            md_bg_color: app.theme_cls.primary_dark
            specific_text_color: 1, 1, 1, 0
            elevation: 10
        MDBoxLayout:
            orientation: 'vertical' 
            padding: "10dp"
            spacing: "20dp"
            MDLabel:
                text: 'Telegraph Uploader'
                theme_text_color: "Secondary"
                font_style: "H2"
                halign: "center"
            MDFillRoundFlatButton:
                text: "Start"
                pos_hint: {"center_x": .5, "center_y": .5}
                font_style: "H4"
                theme_text_colour: "Custom"
                text_color: [0, 0, 0, 1]
                md_bg_color: app.theme_cls.primary_dark
                size_hint: (0.8, 0.8)
                size: "140dp", "80dp"
                on_release: 
                    root.manager.current = 'upload'
                    root.manager.transition.direction = 'up'
            MDFillRoundFlatButton:
                text: "Settings"
                pos_hint: {"center_x": .5, "center_y": .3}
                font_style: "H4"
                theme_text_color: "Custom"
                text_color: [0, 0, 0, 1]
                md_bg_color: app.theme_cls.primary_dark
                size_hint: (0.8, 0.8)
                size: "140dp", "80dp"
                on_release: 
                    root.manager.current = 'settings'
                    root.manager.transition.direction = 'up'

<SettingsScreen>:
    name: 'settings'
    MDBoxLayout:
        orientation: 'vertical'
        MDToolbar:
            title: 'Settings'
            md_bg_color: app.theme_cls.primary_dark
            specific_text_color: 1, 1, 1, 1
            elevation: 10
            left_action_items: [["arrow-left", lambda x: app.go_back()]]
        MDBoxLayout:
            orientation: 'vertical'
            padding: "10dp"
            spacing: "20dp"
            MDLabel:
                text: 'Article Settings'
                theme_text_color: "Secondary"
                font_style: "H5"
                halign: "center"
            MDTextField:
                id: title_field
                hint_text: "Enter article title (NECESSARILY)"
                pos_hint: {"center_x": .5}
            MDTextField:
                id: author_field
                hint_text: "Enter author name (optional)"
                pos_hint: {"center_x": .5}
            MDTextField:
                id: link_field
                hint_text: "Enter author link (optional)"
                pos_hint: {"center_x": .5}
            MDRaisedButton:
                text: "Save Article Settings"
                md_bg_color: app.theme_cls.primary_dark
                pos_hint: {"center_x": .5}
                on_release: app.save_article_settings(author_field.text, title_field.text, link_field.text)
            MDLabel:
                text: 'Theme'
                theme_text_color: "Secondary"
                font_style: "H5"
                halign: "center"
            MDSwitch:
                id: theme_switch
                pos_hint: {"center_x": .5}
                active: app.theme_cls.theme_style == "Dark"
                on_active: app.change_theme(self.active)

<UploadScreen>:
    name: 'upload'
    MDBoxLayout:
        orientation: 'vertical'
        MDToolbar:
            title: 'File Upload'
            md_bg_color: app.theme_cls.primary_dark
            specific_text_color: 1, 1, 1, 1
            elevation: 10
            left_action_items: [["arrow-left", lambda x: app.go_back()]]
        MDBoxLayout:
            orientation: 'vertical'
            padding: "10dp"
            spacing: "400dp"
            MDTextField:
                id: directory
                hint_text: "Enter directory path"
                helper_text: "Copy the path to the file folder and paste"
                helper_text_mode: "on_focus"
                icon_right: "folder"
                icon_right_color: app.theme_cls.primary_color
                pos_hint: {"center_x": .5, "top": .9}
            MDFillRoundFlatButton:
                id: upload_button
                text: "Upload"
                pos_hint: {"center_x": .5, "center_y": .3}
                font_style: "H4"
                theme_text_colour: "Custom"
                text_color: [0, 0, 0, 1]
                md_bg_color: app.theme_cls.primary_dark
                size: "140dp", "80dp"
                on_release: app.on_upload_button_release(directory.text)

<ProgressScreen>:
    name: 'progress'
    MDBoxLayout:
        orientation: 'vertical'
        MDToolbar:
            title: 'Progress'
            md_bg_color: app.theme_cls.primary_dark
            specific_text_color: 1, 1, 1, 1
            elevation: 10
        MDBoxLayout:
            orientation: 'vertical'
            padding: "10dp"
            spacing: "20dp"
            MDLabel:
                id: progress_label
                text: 'Uploading...'
                theme_text_color: "Secondary"
                font_style: "H5"
                halign: "center"
            MDProgressBar:
                id: progress_bar
                value: 0
                pos_hint: {"center_x": .5}

<ArticleScreen>:
    name: 'article'
    MDBoxLayout:
        orientation: 'vertical'
        MDToolbar:
            right_action_items: [["arrow-left", lambda x: app.go_back()]]
            title: 'Article'
            md_bg_color: app.theme_cls.primary_dark
            specific_text_color: 1, 1, 1, 1
            elevation: 10
        MDBoxLayout:
            orientation: 'vertical'
            padding: "10dp"
            spacing: "20dp"
            pos_hint: {"center_x": .5}
            MDTextField:
                id: article_link
                hint_text: "Article link"
                mode: "rectangle"
                multiline: True
                readonly: True
            MDIconButton:
                icon: "content-copy"
                pos_hint: {'center_x': .5}
                on_press: app.copy_link(article_link.text)

        ''')
        return screen

    def on_upload_button_release(self, directory_path):
        # Validate directory path
        if not os.path.isdir(directory_path):
            self.show_error_popup("Invalid Directory", "The directory path is invalid.")
            return

        # Check if article title is provided
        if not self.article_settings["title"]:
            error_message = "Please enter the article title in the settings screen."
            self.go_to_settings_screen()
            self.root.get_screen('settings').ids.title_field.error = True
            return

        # Proceed to the upload stage
        self.root.current = 'progress'
        self.start_upload(directory_path)

    def start_upload(self, directory_path):
        # Validate directory path
        if not os.path.isdir(directory_path):
            self.show_error_popup("Invalid Directory", "The directory path is invalid.")
            return

        # List of allowed extensions
        allowed_extensions = [".png", ".gif", ".jpg", ".jpeg", ".webp"]

        # Get list of files in the directory
        files = os.listdir(directory_path)

        # Filter out non-allowed files
        allowed_files = [file for file in files if os.path.splitext(file)[1].lower() in allowed_extensions]
        allowed_files = natsort.natsorted(allowed_files, alg=natsort.ns.IGNORECASE)

        # Check if there are any allowed files to upload
        if not allowed_files:
            self.show_error_popup("No Allowed Files", "There are no allowed files in the directory to upload.")
            return

        # Create a new thread for uploading files
        upload_thread = Thread(target=self.upload, args=(directory_path, allowed_files))
        upload_thread.start()

    def change_theme(self, switch_active):
        if switch_active:
            self.theme_cls.theme_style = "Dark"
        else:
            self.theme_cls.theme_style = "Light"

    @mainthread
    def change_to_article_screen(self):
        self.root.current = 'article'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.article_settings = {"author": "", "title": "", "link": ""}

    def save_article_settings(self, author, title, link):
        self.article_settings["author"] = author
        self.article_settings["title"] = title
        self.article_settings["link"] = link

    def go_back(self):
        # Get the screen that was before the current one
        current_screen = self.root.current
        if current_screen == 'upload':
            previous_screen = 'welcome'
        elif current_screen == 'settings':
            previous_screen = 'welcome'
        elif current_screen == 'article':
            previous_screen = 'welcome'
        else:
            # If there's no previous screen, just exit
            return
        self.root.current = previous_screen

    @mainthread
    def update_progress(self, progress_value):
        progress_label = self.root.get_screen('progress').ids.progress_label
        progress_bar = self.root.get_screen('progress').ids.progress_bar
        progress_bar.value = progress_value
        progress_label.text = f'Uploading... {int(progress_value)}%'

    @mainthread
    def update_article_link(self, article_url):
        article_link = self.root.get_screen('article').ids.article_link
        article_link.text = article_url

    def copy_link(self, link):
        Clipboard.copy(link)

    def show_enter_title_popup(self):
        def close_popup(instance):
            popup.dismiss()

        content = BoxLayout(orientation='vertical', padding="10dp", spacing="10dp")
        content.add_widget(Label(text="Please enter article title"))

        ok_button = Button(text="OK", size_hint=(None, None), size=("100dp", "48dp"), pos_hint={'center_x': 0.5})
        ok_button.bind(on_press=close_popup)  # Bind close_popup function to the on_press event

        content.add_widget(ok_button)

        popup = Popup(title="Enter Article Title", content=content, size_hint=(None, None), size=(400, 200))
        popup.open()

    def go_to_settings_screen(self):
        self.root.current = "settings"
        self.show_enter_title_popup()

    def upload(self, directory_path, allowed_files):
        telegraph = Telegraph()
        try:
            telegraph.create_account(short_name=self.article_settings["title"])
        except exceptions.TelegraphException as exc:
            error_message = f"Failed to create Telegraph account: {exc}"
            Clock.schedule_once(lambda dt: self.show_error_popup("Telegraph Account Creation Error", error_message))
            return

        total_files = len(allowed_files)
        uploaded_files = 0
        image_urls = []

        for file in allowed_files:
            file_path = os.path.join(directory_path, file)
            file_path = convert_file_to_image(file_path)
            try:
                upload_file_response = upload_file(file_path)
                if upload_file_response:
                    uploaded_files += 1
                    image_urls.append(upload_file_response[0])
            except exceptions.TelegraphException as exc:
                print(f"Error uploading file: {file}")
                print(f"Error: {exc}")
                self.show_error_popup("Upload Error", f"Error uploading file: {file}\nError: {exc}")
                return

            # Update the progress bar
            progress_value = (uploaded_files / total_files) * 100
            self.update_progress(progress_value)

        # If all files are uploaded, finish the upload
        if uploaded_files == total_files:
            # Set up article title, author, and hyperlink
            title = self.article_settings["title"] if self.article_settings["title"] else 'My Uploaded Media'
            author_name = self.article_settings["author"] if self.article_settings["author"] else ''
            author_url = self.article_settings["link"] if self.article_settings["link"] else ''

            # Create article on Telegraph
            html_content = "".join(f"<img src='{url}'/>" for url in image_urls)
            try:
                response = telegraph.create_page(
                    title=title,
                    author_name=author_name,
                    author_url=author_url,
                    html_content=html_content
                )
                article_url = 'http://telegra.ph/{}'.format(response['path'])
            except exceptions.TelegraphException as exc:
                self.show_error_popup("Telegraph Error", f"Error creating article: {exc}")
                return

            # Update the article link
            self.update_article_link(article_url)

            print(f'Upload Complete. Article URL: {article_url}')
            # Change to article screen after 100% upload
            Clock.schedule_once(lambda dt: self.change_to_article_screen())
    @mainthread
    def show_error_popup(self, title, message):
        def close_popup(instance):
            popup.dismiss()

        content = BoxLayout(orientation='vertical', padding="10dp", spacing="10dp")
        content.add_widget(Label(text=message))

        ok_button = Button(text="OK", size_hint=(None, None), size=("100dp", "48dp"), pos_hint={'center_x': 0.5})
        ok_button.bind(on_release=close_popup)
        content.add_widget(ok_button)

        popup = Popup(title=title, content=content, size_hint=(None, None), size=(400, 200))
        popup.open()

if __name__ == "__main__":
    MainApp().run()

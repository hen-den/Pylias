"""
This tool downloads each File of a course from Ilias at HHN and
saves that files in seperate directories.
:copyright: (c) 2020 by Mertkan Henden
:license: GNU General Public License Version 3, see LICENSE
"""
from argparse import ArgumentParser, ArgumentTypeError, RawTextHelpFormatter
from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from time import sleep
import os
import shutil
import pathlib
import getpass


class IliasParser(ArgumentParser):
    def __init__(self) -> None:
        ilias_url = 'https://ilias.hs-heilbronn.de/' \
                    'login.php?target=&client_id=ilias' \
                    'hhn&cmd=force_login&lang=de'
        usage_examples = 'Example: python main.py maxmuster -p "enter//your//path//here"'

        super(IliasParser, self).__init__(
            prog='Pylias',
            description='Download all your scripts at Ilias HHN.',
            epilog=usage_examples,
            formatter_class=RawTextHelpFormatter,
        )
        self.add_args()

    def add_args(self):
        self.add_argument(
            'username',
            metavar='u',
            type=str,
            help='Ilias Username')

        self.add_argument(
            '-p',
            '--path',
            type=self.is_valid_dir_path,
            help='Download-Directory-Path'
        )

    def validate_args(self):
        parsed = self.parse_args()
        if not parsed.username:
            self.error(
                "Your username is required to login to Ilias."
            )
        if parsed.path and not os.path.isdir(parsed.path):
            self.error(f"Directory '{parsed.path}' doesn't exist")
        return parsed.username, parsed.path

    @staticmethod
    def is_valid_dir_path(path: str) -> str:
        """Raise error if path leads to file"""

        if path.startswith("~"):
            path = os.path.normpath(os.path.expanduser(path))

        if path.startswith("."):
            path = os.path.abspath(path)

        if os.path.isfile(path):
            raise ArgumentTypeError(f"'{path}' points to a file")
        return path


class Application():
    """Application class."""

    def __init__(self, username=None, user_path=None):
        if user_path is not None:
            self.user_path = user_path
        else:
            project_path = os.getcwd()
            dl_path = os.path.join(project_path, 'DL')

            if os.path.isdir(dl_path):
                self.user_path = dl_path
            else:
                pathlib.Path(dl_path).mkdir(parents=True, exist_ok=True)
                self.user_path = dl_path

        self.username = username
        self.password = getpass.getpass()
        self.chrome_options = Options()
        self.chrome_options.add_experimental_option('prefs', {
            "download.default_directory": self.user_path,
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "plugins.always_open_pdf_externally": True
        })
        self.driver = webdriver.Chrome(options=self.chrome_options)
        self.driver.maximize_window()

    def login(self):

        ilias_url = 'https://ilias.hs-heilbronn.de/' \
                    'login.php?target=&client_id=ilias' \
                    'hhn&cmd=force_login&lang=de'
        credentials = {'username': self.username, 'password': self.password}

        self.driver.get(ilias_url)
        self.driver.find_element_by_id('username').send_keys(credentials['username'])
        self.driver.find_element_by_id('password').send_keys(credentials['password'])
        self.driver.find_element_by_name('cmd[doStandardAuthentication]').click()

    def manage_dl_directory(self):
        # The Path of the directory to be sorted
        path = self.user_path

        # This populates a list with the filenames in the directory
        print(path)
        list_ = os.listdir(path)

        if len(list_) > 0:
            for file_ in list_:
                filename, ext = os.path.splitext(file_)
                # Stores the extension type
                ext = ext[1:]
                # If it is directory, it forces the next iteration
                if ext == '':
                    continue

                else:
                    pathlib.Path(path + '/' + 'content').mkdir(parents=True, exist_ok=True)
                    shutil.move(path + '/' + file_, path + '/' + 'content' + '/' + file_)

    def iterate_list(self):
        try:
            list_name = str(self.driver.find_element_by_xpath('//*[@id="il_mhead_t_focus"]').text)
            breadcrumb_list = self.breadcrumb_structure()
            filtered_breadcrumb = self.filter_string(breadcrumb_list)

            # Get icons of list
            icons = self.driver.find_elements_by_class_name('ilListItemIcon')
            icons_count = len(icons)

            if icons_count > 0:
                # downloads all files and opens directories in new tabs
                for i in range(0, icons_count):
                    title = icons[i].get_attribute("title")

                    if title == 'Symbol Lernmodul Datei' or title == 'Symbol Datei':
                        webdriver.ActionChains(self.driver).move_to_element(icons[i]).click(icons[i]).perform()
                        sleep(6)

                    if title == 'Symbol Ordner' or title == 'Symbol Kurs':
                        ActionChains(self.driver).key_down(Keys.CONTROL).key_down(Keys.ALT).click(icons[i]).perform()
                sleep(3)
                # moves downloaded files in related directory
                self.file_sort(filtered_breadcrumb=filtered_breadcrumb)

        except Exception:
            pass

        finally:
            present_tabs = len(self.driver.window_handles)
            if present_tabs > 1:
                self.driver.close()
                self.driver.switch_to.window(self.driver.window_handles[-1])
                return False
            if present_tabs == 1:
                return True

    def select_course(self):
        # Get name of list-item
        all_list_items = self.driver.find_elements_by_xpath('//a[starts-with(@class, "il_ContainerItemTitle")]')
        course_count = len(all_list_items)

        # Get icons of list
        icons = self.driver.find_elements_by_class_name('ilListItemIcon')
        print(icons)
        # Selected courses list
        all_courses = []
        selected_courses = {}

        for i in range(0, course_count):
            title = icons[i].get_attribute("title")
            if title == 'Symbol Kurs':
                all_courses.append(all_list_items[i].text)

        for i in range(len(all_courses)):
            selected_courses[i] = all_courses[i]

        # Show user selectable courses
        for course_index in selected_courses:
            print(course_index, ':', selected_courses[course_index])

        for course in selected_courses:
            course_to_click = self.driver.find_element_by_partial_link_text(course)
            ActionChains(self.driver).key_down(Keys.CONTROL).key_down(Keys.ALT).click(course_to_click).perform()

    def file_sort(self, filtered_breadcrumb=None):
        """
        Move recent downloaded files into related directory.
        Directory structure is identical to breadcrumb structure.
        """
        # The Path of the directory to be sorted
        path = self.user_path

        # This populates a list with the filenames in the directory
        list_ = os.listdir(path)

        # Creates the filtered final path
        final_path = self.final_path(path=path, filtered_breadcrumb=filtered_breadcrumb)
        sleep(1)

        # Traverses every file in DL-directory
        for file_ in list_:
            filename, ext = os.path.splitext(file_)
            # Stores the extension type
            ext = ext[1:]
            # If it is directory, it forces the next iteration
            if ext == '':
                continue

            # If a directory with the name 'final_path' exists, it moves the file to that directory
            if os.path.exists(final_path):
                shutil.move(path + '/' + file_, final_path + '/' + file_)

            # If the directory does not exist, it creates a new directory
            else:
                pathlib.Path(final_path).mkdir(parents=True, exist_ok=True)
                shutil.move(path + '/' + file_, final_path + '/' + file_)

    def final_path(self, path=None, filtered_breadcrumb=None):
        """
        Creates the final directory path by combining
        the DL-Path and the list of breadcrumb strings.
        :param path: str, path of DL-directory
        :param filtered_breadcrumb: list, filtered list of strings
        :return: str, combined path
        """
        if isinstance(filtered_breadcrumb, list):
            final_path = path
            for i in filtered_breadcrumb:
                final_path += '/' + i
        return str(final_path)

    def breadcrumb_structure(self):
        """
        Extracts Breadcrumb structure from current site.
        :return: list
        """
        breadcrumb = self.driver.find_elements_by_xpath('//ol[starts-with(@class, "breadcrumb ")]/li')
        breadcrumb_list = []
        all_breadcrumb = len(breadcrumb)
        for i in range(0, all_breadcrumb):
            breadcrumb_list.append(breadcrumb[i].text)
        return breadcrumb_list

    def filter_string(self, filter_content=None):
        """
        Filters list of Strings or string
        :param filter_content: list or str
        :return: list or str
        """
        filtered_list = []
        final_list = []
        if isinstance(filter_content, list):
            for i in filter_content:
                for c in i:
                    if c.isalnum():
                        filtered_list.append(c)
                    elif c == " ":
                        filtered_list.append('_')
                    elif c == '-':
                        filtered_list.append('-')
                final_list.append(''.join(filtered_list))
                filtered_list.clear()

        elif isinstance(filter_content, str):
            for c in filter_content:
                if c.isalnum():
                    filtered_list.append(c)
                elif c == " ":
                    filtered_list.append('_')
                elif c == '-':
                    filtered_list.append('-')
            final_list = ''.join(filtered_list)

        return final_list


def main():
    """Main entry point."""
    username, user_path = IliasParser().validate_args()
    bot = Application(username=username, user_path=user_path)
    bot.manage_dl_directory()
    bot.login()
    # bot.select_course()
    end = False
    while not end:
        end = bot.iterate_list()


if __name__ == '__main__':
    main()

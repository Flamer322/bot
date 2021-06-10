from setuptools import setup


setup(
  name='WeatherBotB',
  version='0.0.51',
  username='flamer322',
  author='flamer322',
  author_email='flamer322@yandex.ru',
  packages=['weather'],
  url='https://github.com/Flamer322/bot',
  description='Telegram API based WeatherBot',
  long_description=open('README.md').read(),
  long_description_content_type="text/markdown",
  install_requires=[
      "requests",
      "pyTelegramBotAPI"
  ],
)

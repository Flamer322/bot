from setuptools import setup


setup(
  name='WeatherBotKB',
  version='0.0.3',
  username='Ivan-Kulagin',
  author='Kulagin & Bartenev',
  author_email='b.bar1enev@gmail.com',
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
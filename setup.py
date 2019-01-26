from setuptools import setup

setup(name='emoji_sync',
      version='0.1',
      description='Sync emoji between slack workspaces.',
      url='http://github.com/abrunet/emoji_sync',
      license='MIT',
      packages=['emoji_sync'],
      entry_points={
          'console_scripts': [
              'emoji-sync=emoji_sync.emoji_sync:main',
              'emoji-report=emoji_sync.emoji_report:main',
          ],
      },
      install_requires=[
          'PyYAML',
          'requests',
      ],
      zip_safe=False)

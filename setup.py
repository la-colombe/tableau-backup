from setuptools import setup

setup(name='tableau_backup',
      version='0.1',
      description='Tool to backup Tableau site to S3 as a ZIP file',
      url='https://github.com/la-colombe/tableau-backup',
      author='Andres Recalde',
      author_email='andres@lacolombe.com',
      license='MIT',
      py_modules=['tableau_backup'],
      packages=['tableau_backup'],
      install_requires=[
          'tableauserverclient',
          'boto3',
      ],
      zip_safe=False,
      entry_points="""
      [console_scripts]
      tableau-backup=tableau_backup:main
      """,
)
import os
path = os.path.abspath(os.path.dirname(__file__))+"/manage.py"
os.system("python %s runserver"%path)


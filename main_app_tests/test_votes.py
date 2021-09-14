import os
import sys

myPath = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, myPath + '/../')

from dotenv import load_dotenv


myPath = myPath.split('/main_app_tests')[0]
load_dotenv(myPath+'/.env-local-pytests')

import os
import subprocess
import requests
import re
import sys
esports_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, esports_dir)

data_directory_pattern = r'D:\Data\speech\esports\overwatch\{}\owl'
from django.test import TestCase
import sys
import pathlib
sys.path.append(str(pathlib.Path(__file__).parent.parent))
from resources import data_manager

class DataManagerTest(TestCase):
    def setUp(self):
        data_manager.save("test.txt", "test")
    
    def test_save_text(self):
        self.assertEqual(data_manager.load("test.txt"), "test")

    def tearDown(self):
        data_manager.delete("test.txt")
        return super().tearDown()
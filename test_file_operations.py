# test_file_operations.py

import unittest
import os
import shutil
from tkinter import Label
from file_operations import rename_images, rename_images_by_folder_name

class TestFileOperations(unittest.TestCase):

    def setUp(self):
        """Set up a test directory with sample images."""
        self.test_dir = 'test_images'
        self.test_dir_copy = 'test_images_copy'
        self.author_name = 'TestAuthor'
        self.status_label = Label()

        # Create a copy of the test images directory to avoid altering original
        if os.path.exists(self.test_dir_copy):
            shutil.rmtree(self.test_dir_copy)
        shutil.copytree(self.test_dir, self.test_dir_copy)

    def tearDown(self):
        """Clean up the test directory after tests."""
        if os.path.exists(self.test_dir_copy):
            shutil.rmtree(self.test_dir_copy)

    def test_rename_images(self):
        """Test renaming images by appending author name."""
        rename_images(self.test_dir_copy, self.author_name, self.status_label)
        # Verify that images are renamed correctly
        expected_files = [
            'image1 by TestAuthor.jpg',
            'image2 by TestAuthor.png',
            'image3 by TestAuthor.gif',
        ]
        actual_files = os.listdir(self.test_dir_copy)
        self.assertCountEqual(actual_files, expected_files)

    def test_rename_images_by_folder_name(self):
        """Test renaming images by folder name and author name."""
        rename_images_by_folder_name(self.test_dir_copy, self.author_name, self.status_label)
        # Verify that images are renamed correctly
        folder_name = os.path.basename(self.test_dir_copy)
        expected_files = [
            f'{folder_name} by {self.author_name} 1.jpg',
            f'{folder_name} by {self.author_name} 2.png',
            f'{folder_name} by {self.author_name} 3.gif',
        ]
        actual_files = os.listdir(self.test_dir_copy)
        self.assertCountEqual(actual_files, expected_files)

if __name__ == '__main__':
    unittest.main()

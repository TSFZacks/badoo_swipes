import os
from PIL import ImageEnhance, Image
import shutil
import time
class PhotoServices:
    
    
    def __init__(self, PATH : str):
        self.PATH = PATH
    
    def adjust_brightness(self, image_path, brightness, save_directory):
        img = Image.open(image_path)
        enhancer = ImageEnhance.Brightness(img)
        adjusted_img = enhancer.enhance(1 + brightness)

        file_name, extension = os.path.splitext(image_path)
        new_filename = f"{file_name}_adjusted{extension}"
        save_path = os.path.join(save_directory, os.path.basename(new_filename))
        adjusted_img.save(save_path)
        
        os.remove(image_path)
        
    def adjust_brightness_directory(self, directory, brightness, save_directory):
        for filename in os.listdir(directory):
            if filename.lower().endswith((".jpg", ".png", ".jpeg")):
                image_path = os.path.join(directory, filename)
                self.adjust_brightness(image_path, brightness, save_directory)
                
    def process_images_for_editing(self, model_name):
        directory = rf"{self.PATH}"
        brightness = -0.075
        save_directory = os.path.join(directory, model_name, "Finished Photos")
        model_directory = os.path.join(directory, model_name, "Photos For Editing")
        self.adjust_brightness_directory(model_directory, brightness, save_directory)

        print("Image switch done")
        
    def move_photo_to_editing(self, selected_photo_path, model_name, attempt=1, max_attempts=2):
        editing_path = os.path.join(rf"{self.PATH}\{model_name.capitalize()}\Photos For Editing", os.path.basename(selected_photo_path))
        try:
            shutil.move(selected_photo_path, editing_path)
            print("Photo moved successfully.")
        except Exception as e:
            print(f"Attempt {attempt}: Failed to move photo to editing directory: {e}")
            if attempt < max_attempts:
                print("Refreshing driver and retrying...")
                time.sleep(5)  
                self.move_photo_to_editing(selected_photo_path, model_name, attempt + 1, max_attempts)
            else:
                print("Failed to move photo after retrying. Please check the issue.")
                
                
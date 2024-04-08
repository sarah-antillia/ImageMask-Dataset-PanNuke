# Copyright 2024 antillia.com Toshiyuki Arai
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

# 2024/04/10 to-arai 

import os
import shutil
import cv2
import numpy as np
import traceback


"""
`masks.npy` an array of 6 channel instance-wise masks 
 (0: Neoplastic cells, 
  1: Inflammatory, 
  2: Connective/Soft tissue cells, 
  3: Dead Cells, 
  4: Epithelial, 
  6: Background)
"""


class ImageMaskDatasetGenerator:

  def __init__(self, resize=(512,512), channels=[0]):
    self.resize      = resize
    self.channels    = channels
    self.start_index = 10000
    
    # OpenCV BGR color 
    self.mask_colors = [
         (  0, 255,   0), # Green  0: Neoplastic cells, 
         (255,   0,   0), # Blue   1: Inflammatory, 
         (  0,   0, 255), # Red    2: Connective/Soft tissue cells, 
         (255, 255,   0), # XXX    3: Dead Cells, 
         (  0, 255, 255), # YYY    4: Epithelial, 
         ]
  

  def generate(self, input_images_file = "",   
                     input_masks_file  = "",
                     images_output_dir= "",
                     masks_output_dir = ""):

   if os.path.exists(images_output_dir):
      shutil.rmtree(images_output_dir)
   if not os.path.exists(images_output_dir):
      os.makedirs(images_output_dir)

   if os.path.exists(masks_output_dir):
      shutil.rmtree(masks_output_dir)

   if not os.path.exists(masks_output_dir):
      os.makedirs(masks_output_dir)
     
   self.generate_mask_files(input_masks_file, masks_output_dir,)

   self.generate_image_files(input_images_file, masks_output_dir , images_output_dir)
 

  def generate_image_files(self, input_file, mask_output_dir, images_output_dir):
    images = np.load(input_file,  mmap_mode='r')
    
    index = self.start_index

    for image in images:
      try:
        print(image.shape) 
        w, h, c = image.shape
        if w <=1 or h<=1:
         continue
   
        image = np.array(image)
        image = cv2.resize(image, self.resize)
        index += 1

        image_file = str(index) + ".jpg"
        image_filepath = os.path.join(images_output_dir, image_file)
        mask_filepath  = os.path.join(mask_output_dir, image_file)
        if os.path.exists(mask_filepath):
          
          cv2.imwrite(image_filepath, image)
          print("Saved image {}".format(image_filepath))
        else:
          print("No found correspondimg mask to image {}".format(image_filepath))
      except:
        traceback.print_exc()


  def generate_mask_files(self, input_file, output_dir, ):
    images = np.load(input_file,  mmap_mode='r')
    index = self.start_index

    for image in images:
      try:
        print(image.shape) 
        w, h, c = image.shape
        if w <=1 or h<=1:
         continue
   
        image = np.array(image)
        index += 1
     
        image_file = str(index) + ".jpg"
        image_filepath = os.path.join(output_dir, image_file)
   
        if len(channels)== 1:
          channel = channels[0]
          img = image[:, :, channel]
          print("  mask shape {}".format(img.shape))
          image_file = str(index)  + ".jpg"
          if np.any(img) >0:
            image_filepath = os.path.join(output_dir, image_file)
            cv2.imwrite(image_filepath, img)
            print("Saved mask {}".format(image_filepath))
          else:
           print("Empty mask {}".format(image_file))
        else :     
          """
            `masks.npy` an array of 6 channel instance-wise masks 
              0: Neoplastic cells, 
              1: Inflammatory, 
              2: Connective/Soft tissue cells, 
              3: Dead Cells, 
              4: Epithelial, 
              6: Background)
          """     
          # Create an empty rgb (3-channels) background
          rgb_background = np.zeros((w, h, 3), np.uint8)

          for i in self.channels:
            img   = image[:, :, i]
            color = self.mask_colors[i]
            #img = np.expand_dims(img, axis=-1)
            #print("---img_expand_dim shape {}".format(img.shape))
            rgb_mask = self.colorize_mask(img, color)

            # Overlapping each mask rgb to the background 
            rgb_background += rgb_mask
          rgb_background = cv2.resize(rgb_background, self.resize)
          
          cv2.imwrite(image_filepath, rgb_background)
          print("Saved mask {}".format(image_filepath))
          
      except:
        traceback.print_exc()


  # Brute-force converter
  def colorize_mask(self, mask, color=(255, 255, 255), threshold=10):
      h, w,  = mask.shape
      rgb = np.zeros((w, h, 3), np.uint8)
      
      for i in range(w):
        for j in range(h):
          c = mask[i, j]        
          if c > threshold:
            rgb[i, j] = color
      return rgb
    
    

if __name__ == "__main__":
  try:
   input_images_file = "./Part 1/Images/images.npy"   
   input_masks_file  = "./Part 1/Masks/masks.npy"
   images_output_dir = "./PanNuke-master/images"
   masks_output_dir  = "./PanNuke-master/masks"

   #channel = 0: Neoplastic cells, 
   # all channels
   #  channels = [0, 1, 2, 3, 4, 6]
   # If you would like to create massks for 
   #  0: Neoplastic cells, 
   # specify 
   #   channels = [0]
   # If you need all non-background channels
   channels = [0, 1, 2, 3, 4]
   resize   = (512, 512)
   
   generator = ImageMaskDatasetGenerator(resize=resize, channels = channels)
   generator.generate(input_images_file = input_images_file,   
                      input_masks_file  = input_masks_file,
                      images_output_dir = images_output_dir,
                      masks_output_dir  = masks_output_dir)
     
  
  except:
    traceback.print_exc()

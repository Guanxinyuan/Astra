from PIL.Image import NONE
import cv2  # import OpenCV
import numpy
from blend_modes import lighten_only, darken_only, multiply, normal
from google.colab.patches import cv2_imshow

def read_and_resize_img(img_src, dim):
  # dim = [width, height]
  img_float = cv2.imread(img_src,-1).astype(float)
  img = cv2.resize(img_float, dim, interpolation = cv2.INTER_AREA)
  return img

n = 256


def blend_images(img_back, img_fore, mode, opacity=1):
    if mode == 'lighten':
        blended_img = lighten_only(img_back , img_fore, opacity)
    elif mode == 'darken':
        blended_img = darken_only(img_back , img_fore, opacity)
    elif mode == 'multiply': 
        blended_img = multiply(img_back , img_fore, opacity)
    elif mode == 'normal':
        blended_img = normal(img_back , img_fore, opacity)
    return blended_img


from hashlib import sha1

def get_dna(traits_string):
  return sha1(str.encode(traits_string)).hexdigest()

import os
import random
import json
import time

layers_folder = "astra_test_0521"
layer_configs = [
  {
    "growToSize": 2,
    "layers": [
    "Background",
    "Back_Orna",
    "Body",
    "Face_Mark",
    "Eyes_Down",
    "Eyes_Middle",
    "Eyes_Up",
    ]
  },

  {
    "growToSize": 5,
    "layers": [
    "Background",
    "Back_Orna",
    "Body",
    "Face_Mark",
    "Eyes_Down",
    "Eyes_Middle",
    "Eyes_Up",
    ]
  }
]


def get_dnas_and_combinations(layers_folder, layer_configs):
  combinations = []
  dna_list = set()

  for layer_config in layer_configs:
    growToSize = layer_config['growToSize']
    layers = layer_config['layers']

    path_bottom_folder = f'{layers_folder}/{layers[0]}'
    image_bottom = random.choice(os.listdir(path_bottom_folder))
    image_bottom = f'{path_bottom_folder}/{image_bottom}'

    layer_image_paths = image_bottom
    while len(dna_list) < growToSize:
      for i in range(1, len(layers)):
        path_front_folder = f'{layers_folder}/{layers[i]}'
        image_front = random.choice(os.listdir(path_front_folder))
        image_front = f'{path_front_folder}/{image_front}'

        layer_image_paths += f'\t{image_front}'
        image_bottom = image_front

      print(get_dna(layer_image_paths))

      dna = get_dna(layer_image_paths)
      if dna not in dna_list:
        dna_list.add(dna)
        combinations.append(layer_image_paths)
      else:
        print("This DNA already exists!")

  return dna_list, combinations


def combine_layers(combination, image_size=512):
  layer_image_paths = combination.split('\t')

  n = image_size
  base_path = layer_image_paths[0]
  base = read_and_resize_img(base_path, (n, n))

  for i in range(1, len(layer_image_paths)):
    cover_path = layer_image_paths[i]
    cover = read_and_resize_img(cover_path, (n, n))

    if "Eyes_Down" in cover_path:
      base = blend_images(base, cover, 'multiply')
    else:
      base = blend_images(base, cover, 'normal')

  # cv2_imshow(base)
  return base

def get_metadata(combination, common_configs):
  metadata = common_configs
  metadata['attributes'] = []

  layer_image_paths = combination.split('\t')
  for layer in layer_image_paths:
    temp = layer.split('/')
    trait_type = temp[1]
    value = temp[2][:-4]
    trait = {
        "trait_type": trait_type,
        "value": value,
    }
    metadata['attributes'].append(trait)
  return metadata


def combine_layers_all(combinations, common_configs, image_size=256):
  result_img_folder = 'build/images'
  result_metadata_folder = 'build/json'
  for i, combination in enumerate(combinations):
    filename_img = f'{i}.png'
    filename_metadata = f'{i}.json'

    result_img = combine_layers(combination, image_size=image_size)
    result_metadata = get_metadata(combination, common_configs)
    
    save_image(result_img, result_img_folder, filename_img)
    save_metadata(result_metadata, result_metadata_folder, filename_metadata)


def save_image(image, folder, filename):
  if not os.path.exists(folder):
    os.makedirs(folder)
  save_path = f'{folder}/{filename}'
  cv2.imwrite(save_path, image)

def save_metadata(metadata, folder, filename):
  if not os.path.exists(folder):
    os.makedirs(folder)
  save_path = f'{folder}/{filename}'
  with open(save_path, 'w') as f:
    json.dump(metadata, f)

dna_list, combinations = get_dnas_and_combinations(layers_folder, layer_configs)

common_configs = {
    "image": "ipfs://someplace",
    "name": "somename",
    "description": "somedescription",
    "external_url": "someurl"
}

start = time.time()
combine_layers_all(combinations, common_configs, image_size=3000)
end = time.time()
print(end-start)
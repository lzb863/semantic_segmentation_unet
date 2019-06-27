import os,shutil,json
from tqdm import tqdm
import cv2

class_id_path = "./val/class_id/"
raw_images_path = "./val/raw_images/"

for id in tqdm(sorted(os.listdir(class_id_path))):
    if(id.endswith(".png")):
        train_dict = {}
        img = id.split(".png")[0]+".jpg"
        assert img in os.listdir(raw_images_path)
        frame = cv2.imread(raw_images_path+img)
        h,w,_ = frame.shape
        train_dict["fpath_img"] = "val/raw_images/"+img
        train_dict["fpath_segm"] = "val/class_id/"+id
        train_dict["height"] = h
        train_dict["width"] = w
        train_dict["dbName"] = "BDD100K"
        with open("val_bdd.odgt","a") as f:
            f.write(json.dumps(train_dict))

class_id_path = "./train/class_id/"
raw_images_path = "./train/raw_images/"

for id in tqdm(sorted(os.listdir(class_id_path))):
    if(id.endswith(".png")):
        train_dict = {}
        img = id.split(".png")[0]+".jpg"
        assert img in os.listdir(raw_images_path)
        frame = cv2.imread(raw_images_path+img)
        h,w,_ = frame.shape
        train_dict["fpath_img"] = "train/raw_images/"+img
        train_dict["fpath_segm"] = "train/class_id/"+id
        train_dict["height"] = h
        train_dict["width"] = w
        train_dict["dbName"] = "BDD100K"
        with open("train_bdd.odgt","a") as f:
            f.write(json.dumps(train_dict))
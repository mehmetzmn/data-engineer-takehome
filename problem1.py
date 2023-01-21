# Tasks:
# Build a python scripts that detects faces in an image using OpenCV
# Saves headshots of the detected faces to a specified directory
# The scripts should take as input a file path to an image,
#                   a directory path to save the headshots,
#                   and output the number of faces detected.
# Use OpenCV's haar Cascade classifier
# Use OpenCV, numpy and PIL
# The script should be well commented
# The script should be able to handle variety of image types (e.g. jpeg, png, etc.)
# The script should be able to handle images with multiple faces
# The script should save the headshots in the specified directory,
#                                file name format --> "face_1.jpg"


import os
import cv2
import numpy as np
from pathlib import Path
from PIL import Image

def get_paths():
    print("Please enter input path: ")
    image_path = list(map(str ,input().split()))
    print("Please enter save path")
    save_path = list(map(str, input().split()))
    # if input text has white spaces, then combine them
    if len(image_path) >= 2 or len(save_path) >= 2:
        return " ".join(image_path), " ".join(save_path)
    else:
        return image_path[0], save_path[0]

def convert_from_image_to_cv2(path):
    # Converting Pil object to cv2 object
    # return np.asarray(img)
    img = Image.open(path)
    print("This is the image", img, type(img))
    return cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)

def convert_from_cv2_to_image(img):
    # Converting cv2 object (image) to Pil object
    # return Image.fromarray(img)
    print("this is the image", img, type(img))
    if img.size != 0:
        print("True")
        return Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))


def detectAndDisplay(frame, save_path):
    # Haar Cascade classifier xml file from opencv package
    face_cascade = cv2.CascadeClassifier(r"haarcascade_frontalface_alt.xml")

    frame_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    frame_gray = cv2.equalizeHist(frame_gray)
    #-- Detect faces
    faces = face_cascade.detectMultiScale(frame_gray, scaleFactor=1.045)
    print("save path -->", save_path)

    # if save path is not empty, continue from last save image
    if len(os.listdir(save_path)) != 0:
        list_of_saved_images = [x for x in os.walk(save_path)][0][2]
        last_image_number = max([int(x[5:-4]) for x in list_of_saved_images])
        count = last_image_number
    else:
        count = 0

    for (x, y, w, h) in faces:
        # create box around faces
        frame = cv2.rectangle(frame, (x-25, y-25), (x+w, y+h), (0, 255, 0), 3)
        face = frame[y - 25:y + h, x - 25:x + w]
        count +=1
        print(count)
        face = convert_from_cv2_to_image(face)
        try:
            face.save(rf"{save_path}/face_{count}.jpg")
        except:
            print("Already saved!!")

    print(f"{count} number of faces detected")
    cv2.imshow('Capture - Face detection', frame)
    return frame


if __name__ == '__main__':
    image_path, save_path = get_paths()
    print("This is image path", image_path)
    print("This is save path", save_path)
    
    # Parent Directory path
    parent_dir = Path.cwd()
    
    # Path
    try:
        path = os.path.join(parent_dir, save_path)
        os.mkdir(path)
    except FileExistsError:
        print("Path already exists!!")

    # last element of the tuple is important
    # os.walk() returns tuple object
    list_of_items = [x for x in os.walk(image_path)]
    list_of_images = [x for x in list_of_items[0][2] if x.endswith(('.jpg', '.png', '.gif', '.psd', '.jpeg'))]
    print(list_of_images)
    for image in list_of_images:
        img1 = convert_from_image_to_cv2(image)
        img = detectAndDisplay(img1, path)
        # img = convert_from_cv2_to_image(img)
        # img.save("detectedfaces.jpg")


    cv2.waitKey(0)
    cv2.destroyAllWindows()

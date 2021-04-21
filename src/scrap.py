import os
import json
import math
from datetime import datetime
import cv2
import numpy as np

def cosmic(jpg):
    # Setting camera with OpenCV
    camera = cv2.VideoCapture(2)

    # Checking if the selected camera exists
    checkstart, _ = camera.read()
    if not checkstart:
        raise "Camera not found"

    # Settings for the camera
    cv2.waitKey(30)

    cosmic_rays_data = json.load(open("data/cosmicrays/cosmic_rays.json", "r"))

    while 1:

        # Getting Camera image and converting to greyscale to get the brightness of each pixel
        check, frame = camera.read()
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Checking if there is a problem with the camera
        if not check:
            raise "Something went wrong with the camera"

        # Transforming the grayscale image in a np array for sake of speed of the program
        pixels = np.array(gray)
        # Getting coordinates of all pixels that are brighter than 10
        coordinates = np.argwhere(pixels > 10)

        # Declaring two variable to store the previous coordinates states
        prevx, prevy = -1024, -1024

        # Iterating through the coordinates of the brightest points
        for (x_coordinate, y_coordinate) in list(coordinates):

            # Skipping bright pixels near to previous bright pixels because
            # they might be part of the same cosmic ray
            if math.sqrt((y_coordinate-prevy)**2+(x_coordinate-prevx)**2) < 10:
                continue
            prevx, prevy = x_coordinate, y_coordinate

            timestamp = datetime.now().strftime('%d-%b-%Y (%H:%M:%S.%f)')

            # Creating folder with timestamp as name and putting there the two images
            # and a JSON with informations about this specific cosmic ray.
            # Adding this cosmic ray to the general cosmic ray data too.
            cosmic_rays_data["count"] += 1
            cosmic_ray_info = {
                "id": cosmic_rays_data["count"],
                "timestamp": timestamp,
                "brightness": int(pixels[x_coordinate][y_coordinate]),
                "position": [int(x_coordinate), int(y_coordinate)]
            }

            os.mkdir(f"data/cosmicrays/{timestamp}")
            if jpg:
                cv2.imwrite(f"data/cosmicrays/{timestamp}/normal.png", frame)
                cv2.imwrite(f"data/cosmicrays/{timestamp}/grayscale.png", gray)
            json.dump(cosmic_ray_info, open(f"data/cosmicrays/{timestamp}/cosmic_ray_info.json", "w"), indent=2)
            cosmic_rays_data["cosmic_rays"].append(cosmic_ray_info)
            json.dump(cosmic_rays_data, open("data/cosmicrays/cosmic_rays.json", "w"), indent=2)

        # Managing key presses
        cv2.waitKey(30)

def radiation():
    # Setting camera with OpenCV
    camera = cv2.VideoCapture(2)

    # Checking if the selected camera exists
    checkstart, _ = camera.read()
    if not checkstart:
        raise "Camera not found"

    # Settings for the camera
    cv2.waitKey(30)

    frames = json.load(open("data/particles.json", "r"))

    prectime = datetime.now()
        # Getting Camera image and converting to greyscale to get the brightness of each pixel
    check, frame = camera.read()
    originalimage = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    while (datetime.now() - prectime).seconds <= 360:
        # Getting Camera image and converting to greyscale to get the brightness of each pixel
        check, frame = camera.read()
        # Checking if there is a problem with the camera
        if not check:
            raise "Something went wrong with the camera"
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        originalimage = cv2.bitwise_or(originalimage, gray)
        cv2.imshow('', originalimage)
        cv2.waitKey(1)

    gray = originalimage

    # Checking if there is a problem with the camera
    if not check:
        raise "Something went wrong with the camera"

    # Calculating mean brightness
    mean_brightness = cv2.mean(gray)[0]

    # Getting binary and tozero thresolded images to have more info and compare their data
    # Threshold is necessary to reduce noise and getting more defined particles
    # Binary threshold will be used for defining particles locations
    # Tozero threshold will be used for defining mean particle brightness
    thrvl = 10
    _, binary_image = cv2.threshold(gray, thrvl, 255, cv2.THRESH_BINARY)
    _, tozero_image = cv2.threshold(gray, thrvl, 255, cv2.THRESH_TOZERO)

    # Getting contours of every particle using binary image for more precision
    particles_contours, _ = cv2.findContours(binary_image, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    # Setting particle count at zero to increase it only when encountering a relevant particle contour
    particles_count = 0

    particles = []

    for i in enumerate(particles_contours):

        contour = particles_contours[i]

        # Getting area of the contour
        area = cv2.contourArea(contour)

        # If area is smaller than 4 the current contour is not relevant
        if area <= 4:
            continue

        particles_count += 1

        # Finding coordinates and size of the rectangle made by the contour to precisely crop the particle
        # from the original image
        x_coordinate, y_coordinate, width, heigth = cv2.boundingRect(contour)
        particleimg = tozero_image[y_coordinate:y_coordinate+heigth, x_coordinate:x_coordinate+width]

        # Getting coordinates and the mean brightness of the current particle
        parcoord = (x_coordinate + int(width/2), y_coordinate + int(heigth/2))
        current_mean = cv2.mean(particleimg)

        particles.append([parcoord, area, current_mean])

    cv2.imshow('', binary_image)
    cv2.waitKey()

    timestamp = datetime.now().strftime('%d-%b-%Y (%H:%M:%S.%f)')
    frames.append([timestamp, mean_brightness, particles_count, particles])
    json.dump(frames, open('./data/particles.json', 'w'))

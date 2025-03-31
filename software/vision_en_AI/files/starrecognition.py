# -*- coding: utf-8 -*-
"""
Created on Mon May 18 21:32:27 2020

@author: bart.bozon
"""

import cv2
import glob
import numpy as np

for filename in glob.glob('*.png'):
    image = cv2.imread(filename,cv2.IMREAD_COLOR)
    cv2.imshow("original", image)

    # guassian blur
    radius=3
    filtered_image_kernel_3 = cv2.GaussianBlur(image, (radius,radius), 0)
    radius=15
    filtered_image_kernel_15 = cv2.GaussianBlur(image, (radius,radius), 0)
    cv2.imshow("filtered 3", filtered_image_kernel_3)
    cv2.imshow("filtered 15", filtered_image_kernel_15)
    cv2.waitKey(0)

    # zelf kernel maken, in dit geval een edge detection
    # https://en.wikipedia.org/wiki/Kernel_(image_processing)
    kernel = np.ones((3,3),)
    kernel=kernel*-1
    kernel[1][1]=8
    print ("edge detect")
    print(kernel)
    cv2.waitKey(0)

    voorbeeld=np.zeros((6,6),)
    voorbeeld [3][2]=1
    voorbeeld [3][3]=1
    print ("voorbeeld")
    print (voorbeeld)
    cv2.waitKey(0)
    voorbeeldfiltered=cv2.filter2D(voorbeeld,-1,kernel)
    print ("Gefiltered")
    print(voorbeeldfiltered)
    cv2.waitKey(0)

    filtered=cv2.filter2D(image,-1,kernel)
    cv2.imshow("filtered", filtered)
    cv2.waitKey(0)

    # is ook ingebouwd (canny edge detector)
    edges = cv2.Canny(image,100,200)
    cv2.imshow("Canny edge detector", edges)
    cv2.waitKey(0)

    # Sharpening kernel
    kernel = np.zeros((3,3), )
    kernel[0][1]=-1
    kernel[2][1]=-1
    kernel[1][0]=-1
    kernel[1][2]=-1
    kernel[1][1]=5
    print ("sharpening")
    print(kernel)
    cv2.waitKey(0)

    sharpened=cv2.filter2D(image,-1,kernel)
    cv2.imshow("sharper", sharpened)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
        
print("finished")
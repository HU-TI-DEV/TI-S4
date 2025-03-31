# -*- coding: utf-8 -*-
"""
Created on Thu May 21 13:42:56 2020

@author: bart.bozon
"""

import cv2
import numpy as np
	
cap = cv2.VideoCapture(1)
kernel = np.zeros((3,3), )
kernel[0][1]=-1
kernel[2][1]=-1
kernel[1][0]=-1
kernel[1][2]=-1
kernel[1][1]=5
kernel_edge = np.ones((3,3), )
kernel_edge=kernel_edge*-1
kernel_edge[1][1]=8
_, frame_color = cap.read()
frame_color_old=frame_color.copy()
while(1):

    # Take each frame
    _, frame_color = cap.read()
    cv2.imshow('frame_color',frame_color)
    frame_gray = cv2.cvtColor(frame_color, cv2.COLOR_BGR2GRAY)
    frame_HSV = cv2.cvtColor(frame_color, cv2.COLOR_BGR2HSV)
    cv2.imshow("frame_gray", frame_gray)
    b,g,r=cv2.split(frame_color)
    cv2.imshow("red", r)
    cv2.imshow("green", g)
    cv2.imshow("blue", b)
    H,S,V=cv2.split(frame_HSV)
    cv2.imshow("H", H)
    cv2.imshow("S", S)
    cv2.imshow("V", V)
    edge=cv2.filter2D(frame_gray,-1,kernel_edge)
    cv2.imshow("edge", edge)
    sharp=cv2.filter2D(frame_gray,-1,kernel)
    cv2.imshow("sharp", sharp)
    frame_subtract=cv2.subtract(frame_color_old,frame_color)
    cv2.imshow("frame subtract", frame_subtract)
    frame_minus=(frame_color_old-frame_color)
    cv2.imshow("frame minus", frame_minus)
    frame_color_old=frame_color.copy()

    res=cv2.bitwise_and(g,b)
    res=cv2.bitwise_and(res,r)
    cv2.imshow("res_and", res)
    k = cv2.waitKey(5) & 0xFF
    if k == 27:
        break

cv2.destroyAllWindows()

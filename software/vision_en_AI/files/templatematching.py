# -*- coding: utf-8 -*-
"""
Created on Thu May 21 13:42:56 2020

@author: bart.bozon
"""

import cv2

# All the 6 methods for comparison in a list
methods = ['cv2.TM_CCOEFF', 'cv2.TM_CCOEFF_NORMED', 'cv2.TM_CCORR',
            'cv2.TM_CCORR_NORMED', 'cv2.TM_SQDIFF', 'cv2.TM_SQDIFF_NORMED']
#https://docs.opencv.org/master/d4/dc6/tutorial_py_template_matching.html
	
cap = cv2.VideoCapture(1)
template_match=cv2.imread("template_match.png",0) 
cv2.imshow("template_match.png",template_match)
while(1):


    # Take each frame
    _, frame_color = cap.read()
    frame_gray = cv2.cvtColor(frame_color, cv2.COLOR_BGR2GRAY)
    res = cv2.matchTemplate(frame_gray,template_match,cv2.TM_CCOEFF_NORMED)
    cv2.imshow("frame_gray", frame_gray)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
    cv2.circle(res, max_loc, 10, (255, 0, 0), 1)
    cv2.imshow("res", res)
    #cv2.imwrite("template.png",frame_gray)
    
    k = cv2.waitKey(5) & 0xFF
    if k == 27:
        break
    
cv2.destroyAllWindows()

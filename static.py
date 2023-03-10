import cv2
import numpy as np

import imutils
import scipy.spatial as sp
from imutils import contours
from imutils import perspective
from scipy.spatial import distance as dist
import streamlit as st
from PIL import Image

def static():
        image_file = st.file_uploader("Upload Images", type=["png","jpg","jpeg"])
        def mp(x,y):
            return((x[0]+y[0])*0.5,(x[1]+y[1])*0.5)

        my_img = image_file.name
        if image_file.name:
            #frame = np.array(my_img)

            
        # load the image, convert it to grayscale, and blur it slightly
            image = cv2.imread(my_img)

            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            gray = cv2.GaussianBlur(gray, (5, 5), 1)
            # perform edge detection, then perform a dilation + erosion to
            # close gaps in between object edges
            edged = cv2.Canny(gray, 100, 200)
            kernel = np.ones((3,3))
            edged = cv2.dilate(edged,kernel, iterations=2)
            edged = cv2.erode(edged, kernel, iterations=1)
            # find contours in the edge map
            cnts = cv2.findContours(edged.copy(), cv2.RETR_EXTERNAL,
                cv2.CHAIN_APPROX_SIMPLE)
            cnts = imutils.grab_contours(cnts)
            # sort the contours from left-to-right and initialize the
            # 'pixels per metric' calibration variable
            (cnts, _) = contours.sort_contours(cnts)
            ppm = None
            width= st.number_input("Enter the width(in inches):",min_value=0.0,
                max_value=6.0,
                step=1e-5,
                format="%.5f")
            st.image(my_img)
            st.markdown("##### Uploaded Image")
            # loop over the contours individually
            for c in cnts:
                # if the contour is not sufficiently large, ignore it
                if cv2.contourArea(c) < 500:
                    continue
                # compute the rotated bounding box of the contour
                orig = image.copy()
                box = cv2.minAreaRect(c)
                box = cv2.cv.BoxPoints(box) if imutils.is_cv2() else cv2.boxPoints(box)
                box = np.array(box, dtype="int")
                # order the points in the contour
                box = perspective.order_points(box)
                cv2.drawContours(orig, [box.astype("int")], -1, (0, 255, 0), 10)
                # loop over the original points and draw them
                for (x, y) in box:
                    cv2.circle(orig, (int(x), int(y)), 5, (0, 0, 255), -1)
                    
                (upper_left, upper_right, bottom_right, bottom_left) = box
                (upper_left_upper_rightX, upper_left_upper_rightY) = mp(upper_left, upper_right)
                (bottom_left_bottom_rightX, bottom_left_bottom_rightY) = mp(bottom_left, bottom_right)
                # compute the mp 
                (upper_leftbottom_leftX, upper_leftbottom_leftY) = mp(upper_left, bottom_left)
                (upper_rightbottom_rightX, upper_rightbottom_rightY) = mp(upper_right, bottom_right)
                # draw the mps on the image
                cv2.circle(orig, (int(upper_left_upper_rightX), int(upper_left_upper_rightY)), 5, (255, 0, 0), -1)
                cv2.circle(orig, (int(bottom_left_bottom_rightX), int(bottom_left_bottom_rightY)), 5, (255, 0, 0), -1)
                cv2.circle(orig, (int(upper_leftbottom_leftX), int(upper_leftbottom_leftY)), 5, (255, 0, 0), -1)
                cv2.circle(orig, (int(upper_rightbottom_rightX), int(upper_rightbottom_rightY)), 5, (255, 0, 0), -1)
                # draw lines between the mps
                cv2.line(orig, (int(upper_left_upper_rightX), int(upper_left_upper_rightY)), (int(bottom_left_bottom_rightX), int(bottom_left_bottom_rightY)),
                    (255, 0, 255), 3)
                cv2.line(orig, (int(upper_leftbottom_leftX), int(upper_leftbottom_leftY)), (int(upper_rightbottom_rightX), int(upper_rightbottom_rightY)),
                    (255, 0, 255), 3)
                    # compute the distance between the mps
                diA = dist.euclidean((upper_left_upper_rightX, upper_left_upper_rightY), (bottom_left_bottom_rightX, bottom_left_bottom_rightY))
                diB = dist.euclidean((upper_leftbottom_leftX, upper_leftbottom_leftY), (upper_rightbottom_rightX, upper_rightbottom_rightY))
                
                if ppm is None:
                    
                    ppm = diA / width
                    # compute the size of the object
                dimA = diA / ppm
                dimB = diB / ppm
                # draw the object sizes 
                cv2.putText(orig, "{:.2f}in".format(dimA),
                    (int(upper_left_upper_rightX - 15), int(upper_left_upper_rightY - 10)), cv2.FONT_HERSHEY_COMPLEX,
                    1, (255, 0, 0), 2)
                
                cv2.putText(orig, "{:.2f}in".format(dimB),
                    (int(upper_rightbottom_rightX + 10), int(upper_rightbottom_rightY)), cv2.FONT_HERSHEY_COMPLEX,
                    1, (255, 0, 0), 2)
                st.write("Width:",dimB)
                st.write("Height:",dimA)
                st.image(orig)
                st.markdown('#')
            
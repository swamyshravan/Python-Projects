# importing libraries
import cv2
import numpy as np


# reading image
img = cv2.imread("Input/img.jpg")

# Edges
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
gray = cv2.medianBlur(gray, 7)
lines = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 15, 7)
negLines = 255-lines
#negedges = cv2.Canny(gray,100,250) #50,250
kernel = np.ones((3,3),np.uint8)
dilate = cv2.dilate(negLines, kernel, iterations=1)
edges = 255-dilate

# cartoonization
#color = cv2.drawContours(mask, c, -1, 255, -1)
color =cv2.bilateralFilter(img, 20, 150,150)
cartoon = cv2.bitwise_and(color, color, mask=edges)

# cv2.imshow("image", img)
#cv2.imwrite("Output/img_sketch.jpg", edges)
#cv2.imwrite("Output/img_cartoon.jpg", cartoon)
cv2.imshow("color", color)
cv2.imshow("edges", edges)
cv2.imshow("cartoon", cartoon)

cv2.waitKey(0)
cv2.destroyAllWindows()
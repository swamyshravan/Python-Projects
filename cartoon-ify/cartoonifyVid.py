import cv2
import sys
import numpy as np

def cartoon(frame):
    # Edges
    gray = cv2.cvtColor(frame, cv2.COLOR_BGRA2GRAY)
    gray = cv2.medianBlur(gray, 7)  #Adjust Blur according to video
    lines = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 15, 7) # adjust last 2 digits
    negLines = 255 - lines
    # negedges = cv2.Canny(gray,100,250) #50,250
    kernel = np.ones((3, 3), np.uint8)
    dilate = cv2.dilate(negLines, kernel, iterations=1)
    edges = 255 - dilate

    # cartoonization
    color = cv2.bilateralFilter(frame, 20, 150, 150)
    cartoon = cv2.bitwise_and(color, color, mask=edges)
    return cartoon


if __name__ == '__main__':
    cap = cv2.VideoCapture('Input/testVid.mp4')

    frame_width = int(cap.get(3))
    frame_height = int(cap.get(4))
    out = cv2.VideoWriter('Output/testVid_out(5).avi', cv2.VideoWriter_fourcc('M', 'J', 'P', 'G'), 20, (frame_width, frame_height))

    while (True):
        ret, frame = cap.read()

        if ret == True:
            # writing out
            cframe = cartoon(frame)
            out.write(cframe)
        else:
            print("Video cartoonification completed")
            cap.release()
            out.release()
            cv2.destroyAllWindows()
            sys.exit(0)
            break
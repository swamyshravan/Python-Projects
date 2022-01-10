import cv2
import numpy as np
import sys

# Load Yolo
net = cv2.dnn.readNet("yolov3.weights", "yolov3.cfg")
classes = []
with open("coco.names", "r") as f:
    classes = [line.strip() for line in f.readlines()]
layer_names = net.getLayerNames()
output_layers = [layer_names[i[0] - 1] for i in net.getUnconnectedOutLayers()]
colors = []
if len(colors) == 0:colors = np.random.uniform(0, 255, size=(len(classes), 3))
else: colors =colors
print('Yolo loaded')

# Loading image
img = cv2.imread('Input/fiat.jpg')
#img = cv2.resize(img, None, fx=0.4, fy=0.4)
height, width, channels = img.shape
print('image loaded')

# Detecting objects
blob = cv2.dnn.blobFromImage(img, scalefactor=0.00392, size=(416, 416), mean=(0, 0, 0), swapRB=True, crop=False)
net.setInput(blob)
outs = net.forward(output_layers)
#print(outs[0][1:])
print('Object detected')

# Showing informations on the screen
class_ids = []
confidences = []
boxes = []
for out in outs:
    for detection in out:
        scores = detection[5:]
        class_id = np.argmax(scores)
        confidence = scores[class_id]
        if confidence > 0.5:
            # Object detected
            center_x = int(detection[0] * width)
            center_y = int(detection[1] * height)
            w = int(detection[2] * width)
            h = int(detection[3] * height)
            # Rectangle coordinates
            x = int(center_x - w / 2)
            y = int(center_y - h / 2)
            boxes.append([x, y, w, h])
            confidences.append(float(confidence))
            class_ids.append(class_id)

indexes = cv2.dnn.NMSBoxes(boxes, confidences, 0.5, 0.4)
#print(len(class_ids))
print('indexes marked')
print(indexes)


carCount = []
for i in range(len(boxes)):
    if i in indexes:
        if classes[class_ids[i]] == 'car':
            carCount.append('car')
print("number of cars in fame: ",len(carCount))

font1 = cv2.FONT_HERSHEY_PLAIN
font = cv2.FONT_HERSHEY_COMPLEX_SMALL
#color = {}
for i in range(len(boxes)):
    if i in indexes:
        if classes[class_ids[i]] == 'car' or classes[class_ids[i]] == 'motorcycle':
            x, y, w, h = boxes[i]
            label = str(classes[class_ids[i]])
            c = confidences[i]
            value = c * 100
            prob = str(round(value, 2))
            tag = ('{}:{}'.format(label, prob))
            # print(tag)
            color = colors[classes.index(label)]
            # print(np.argmax(color))
            # print('color label: ', classes.index(label))
            # print('colors: ', color)
            text1 = ('{} cars detected'.format(len(indexes)))
            cv2.rectangle(img, (x, y), (x + w, y + h), color, 2)
            cv2.putText(img, tag, (x, y - 5), font1, 1, color, 1)
            cv2.putText(img, text1, (30,30), font1, 2, (10,0,200), 2)
            # cv2.putText(img, prob, (x, y+15), font, 1, color, 2)
        else: continue
print('No. of boxes: ', len(boxes))
print('No. of indexes: ', len(indexes))
print(classes[class_ids[2]])
cv2.imwrite("Output/fiatOut.jpg", img)
print('file output done')
#cv2.waitKey(0)
cv2.destroyAllWindows()
sys.exit(0)

#if __name__ == '__main__':

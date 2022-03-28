import cv2
import numpy as np
import asyncio

# Initilization
LABELS = open('weights/coco.txt').read().strip().split("\n")
model_path = 'weights/yolov5s.onnx'
net = cv2.dnn.readNet(model_path)
layer_name = net.getLayerNames()
layer_name = [layer_name[i - 1] for i in net.getUnconnectedOutLayers()]
YOLO_SIZE = 640
# Box colors
np.random.seed(4)
COLORS = np.random.randint(0, 255, size=(len(LABELS), 3), dtype="uint8")
#-----

async def find_robbers(weapons, people, filtered_indices):
    for i in filtered_indices[0]: # Weapons
        for j in filtered_indices[1]: # People
            if (weapons[i][0] > people[j][0] - people[j][2] * 0.75 and weapons[i][0] < people[j][0] + people[j][2] * 0.75) and (
                weapons[i][1] > people[j][1] - people[j][3] * 0.75 and weapons[i][1] < people[j][1] + people[j][3] * 0.75):
                print('ROBBER FOUND!!!', end=' ', flush=True)
                return

CONFIDENCE_THRESHOLD = 0.35
def make_final_boxes(image, boxes, probabilities, classIDs):
    (original_image_height, original_image_width) = image.shape[:2] # Take the height and width of the original image.
    
    # Apply Non-Maxima Suppression to suppress overlapping bounding boxes
    NMS_THRESHOLD = 0.3
    filtered_indices = []
    filtered_indices.append( cv2.dnn.NMSBoxes(boxes[0], probabilities[0], CONFIDENCE_THRESHOLD, NMS_THRESHOLD) )
    filtered_indices.append( cv2.dnn.NMSBoxes(boxes[1], probabilities[1], CONFIDENCE_THRESHOLD, NMS_THRESHOLD) )

    asyncio.run(find_robbers(boxes[0], boxes[1], filtered_indices))

    (original_image_height, original_image_width) = image.shape[:2] # Take the height and width of the original image.
    # Factors to recover the image size to before being decreased to fit YOLO 640 size
    x_factor = original_image_width / YOLO_SIZE
    y_factor = original_image_height / YOLO_SIZE

    # Draw boxes
    for i in range(2):
        for j in filtered_indices[i]:
            color = [ int(c) for c in COLORS[classIDs[i][j]] ]

            # Use the center coordinates to derive the top and left corner of the bounding box.
            (width, height) = (int(boxes[i][j][2]), int(boxes[i][j][3]))
            (left_x, top_y) = (int( (boxes[i][j][0] - width / 2) * x_factor), int( (boxes[i][j][1] - height / 2) * y_factor))

            cv2.rectangle(image, (left_x, top_y, width, height), color, 2) # Bounding box
            text = "{}: {:.2f}%".format(LABELS[classIDs[i][j]], probabilities[i][j]*100)
            #text = "{}: {:.2f}%".format('INCHEON UNIVERSITY', probabilities[i]*100)
            cv2.putText(image, text, (left_x, top_y - 25), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
            coordinate = "Coordinate: (X={}, Y={})".format(left_x, top_y)
            cv2.putText(image, coordinate, (left_x, top_y - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

def image_into_neural_network(image):
    # Image normalization
    blob = cv2.dnn.blobFromImage(image, 1 / 255.0, (YOLO_SIZE, YOLO_SIZE), swapRB=True, crop=False)

    net.setInput(blob)
    return net.forward(layer_name)[0][0] # Return anchor boxes

def initial_detection(image):
    # Initialize our lists of detected bounding boxes, confidences, and class IDs, respectively
    boxes = [[], []]
    probabilites = [[], []]
    classIDs = [[], []]

    # Process the anchor boxes
    anchor_boxes = image_into_neural_network(image)
    for anchor_box in anchor_boxes:
        candidate_probabilites = anchor_box[5:] # An anchor box has class probabilites from index 5.
        classID = np.argmax(candidate_probabilites) # Determine the most likely class.
        probability_of_most_likely_class = candidate_probabilites[classID]
        confidence = anchor_box[4] # Class probabilites are conditional probabilities by the confidence.
        # It turns out each grid box gets an anchor box 3 times thssat gets bigger in each creation.
        # Anchor boxes are the biggest in the 1st layer and get small in each layer.
        # and it turns out that each anchor box has probabilities of all the classes.

        # Filter out weak predictions by ensuring the detected confidence is greater than the minimum confidence.
        if confidence > CONFIDENCE_THRESHOLD:
            if classID == 43: # Knife detected
                (center_x, center_y, width, height) = anchor_box[0:4]
                boxes[0].append([center_x, center_y, width, height])
                probabilites[0].append(probability_of_most_likely_class)
                classIDs[0].append(classID)

            elif classID == 0: # Person detected
                (center_x, center_y, width, height) = anchor_box[0:4]
                boxes[1].append([center_x, center_y, width, height])
                probabilites[1].append(probability_of_most_likely_class)
                classIDs[1].append(classID)
        
    make_final_boxes(image, boxes, probabilites, classIDs)

# Detection with the webcam
video = cv2.VideoCapture(0) # 0 is a device number(Here it's the laptop camera)
video.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
video.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

while True:
    if cv2.waitKey(1) > -1: # End detecting by pressing Spacebar
        break

    ret, frame = video.read()
    initial_detection(frame)
    cv2.imshow("Capstone design STARS", frame)

video.release()
cv2.destroyAllWindows()
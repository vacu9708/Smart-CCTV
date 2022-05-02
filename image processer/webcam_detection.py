import cv2
import numpy as np
import onnxruntime
import imagezmq
import base64
import socketio
#import requests

# Socket
socket_io = socketio.Client()
#socket_io.connect('http://localhost:3000')
socket_io.connect('http://59.17.63.221:3000')

# Initilization
LABELS = open('weights/person_weapons.txt').read().strip().split("\n")
model_path = 'weights/person_knife.onnx'
net = onnxruntime.InferenceSession(model_path)
'''net = cv2.dnn.readNet(model_path)
layer_name = net.getLayerNames()
layer_name = [layer_name[i - 1] for i in net.getUnconnectedOutLayers()]'''
YOLO_SIZE = 640
# Box colors
np.random.seed(4)
COLORS = np.random.randint(0, 255, size=(len(LABELS), 3), dtype="uint8")
#-----

def find_robbers(people, weapons, filtered_indices):
    for i in filtered_indices[0]: # People
        for j in filtered_indices[1]: # Weapons
            # If a weapon box overlaps a person box
            if (weapons[j][0] > people[i][0] - people[i][2] * 0.75 and weapons[j][0] < people[i][0] + people[i][2] * 0.75) and (
                weapons[j][1] > people[i][1] - people[i][3] * 0.75 and weapons[j][1] < people[i][1] + people[i][3] * 0.75):
                print('!!!ROBBER FOUND!!!', end=' ', flush=True)
                message="Message from python"
                socket_io.emit("message from python", message)
                # message = {"message": "Message from python"}
                # requests.post('http://localhost:3000/process/detection', json=message)
                return

CONFIDENCE_THRESHOLD = 0.3
def make_final_boxes(image, boxes, probabilities, classIDs):
    (original_image_height, original_image_width) = image.shape[:2] # Take the height and width of the original image.
    
    # Apply Non-Maxima Suppression to suppress overlapping bounding boxes
    NMS_THRESHOLD = 0.3
    filtered_indices = []
    filtered_indices.append( cv2.dnn.NMSBoxes(boxes[0], probabilities[0], CONFIDENCE_THRESHOLD, NMS_THRESHOLD) )
    filtered_indices.append( cv2.dnn.NMSBoxes(boxes[1], probabilities[1], CONFIDENCE_THRESHOLD, NMS_THRESHOLD) )

    find_robbers(boxes[0], boxes[1], filtered_indices)

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

    input_name = net.get_inputs()[0].name
    label_name = net.get_outputs()[0].name
    return net.run([label_name], {input_name: blob.astype(np.float32)})[0][0]

    '''net.setInput(blob)
    return net.forward(layer_name)[0][0] # Return anchor boxes'''

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
            if classID == 0: # Person detected
                (center_x, center_y, width, height) = anchor_box[0:4]
                boxes[0].append([center_x, center_y, width, height])
                probabilites[0].append(probability_of_most_likely_class)
                classIDs[0].append(classID)

            elif classID == 1: # Knife detected
                (center_x, center_y, width, height) = anchor_box[0:4]
                boxes[1].append([center_x, center_y, width, height])
                probabilites[1].append(probability_of_most_likely_class)
                classIDs[1].append(classID)
        
    make_final_boxes(image, boxes, probabilites, classIDs)

# Detect the video from raspberry pi
'''image_hub = imagezmq.ImageHub() # Prepare to receive video by socket
while True:
    if cv2.waitKey(1) >= 0:
        break

    rpi_name, frame = image_hub.recv_image()
    image_hub.send_reply(b'OK')
    initial_detection(frame)
    cv2.imshow(rpi_name, frame)
    result, encoded_frame = cv2.imencode('.jpg', frame)
    image_as_text = base64.b64encode(encoded_frame).decode('utf-8')
    socket_io.emit('streaming', image_as_text)
socket_io.disconnect()'''

# Turn on webcam
video = cv2.VideoCapture(0) # 0 is a device number(Here it's the laptop camera)
video.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
video.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

while True:
    if cv2.waitKey(1) > -1: # End detecting by pressing any key
        break

    ret, frame = video.read()
    initial_detection(frame)
    #cv2.imshow("Capstone design STARS", frame)
    result, encoded_frame = cv2.imencode('.jpg', frame)
    image_as_text = base64.b64encode(encoded_frame).decode('utf-8')
    socket_io.emit('frame from python', image_as_text)
video.release()

cv2.destroyAllWindows()
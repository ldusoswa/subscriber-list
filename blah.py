import cv2

# Get the list of available cameras/webcams on your system
camera_index = 0
cameras = []
while True:
    cap = cv2.VideoCapture(camera_index)
    if not cap.read()[0]:
        break
    cameras.append(camera_index)
    cap.release()
    camera_index += 1

# Open the webcam with the index found in the previous step
cap = cv2.VideoCapture(cameras[0])

# Read a frame from the webcam
ret, frame = cap.read()

# Save the frame as an image file
cv2.imwrite("webcam_image.jpg", frame)

# Release the webcam
cap.release()

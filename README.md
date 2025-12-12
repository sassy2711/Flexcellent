# Flexcellent - A Yoga Pose Corrector 

## Overview

**Yoga Pose Corrector** is a computer vision-based application that detects yoga poses in real-time and provides instant feedback on the correctness of the posture. Using OpenCV and machine learning, the app identifies key pose landmarks and compares them against ideal reference poses, helping users correct their yoga postures efficiently. The project also includes audio feedback for hands-free usage, making it user-friendly for home workouts.

## Features

- Real-time yoga pose detection using computer vision.
- Comparison of user pose with ideal pose landmarks for accuracy.
- Instant feedback on posture correction.
- Audio guidance for hands-free usage.
- Supports multiple yoga poses.
- Cross-platform compatibility (mobile/desktop).

## Technologies Used

- **OpenCV**: For computer vision tasks like capturing images and processing pose landmarks.
- **MediaPipe**: To detect pose landmarks from images.
- **Python**: Backend logic for pose comparison and feedback.
- **Flask**: To expose the backend as an api.

## Setup Instructions

### Prerequisites

Ensure you have the following installed:

- Python 3.x
- pip

### Installation
   **Backend**
   1. **Clone the repository**:
      ```bash
      git clone https://github.com/sassy2711/Yoga_Pose_Corrector.git
      ```
   2. **Navigate into project directory**:
      ```bash
      cd Yoga_Pose_Corrector
      ```
   3. **Install Python dependencies**:
      ```bash
      pip install -r requirements.txt
      ```
   4. **Running the backend**:
      ```bash
      cd backend
      python main.py
      ```

## Yoga Poses Supported

1. **Pranamasana (Prayer Pose)**
2. **Hastauttanasana (Raised Arms Pose)**
3. **Hastapadasana (Standing Forward Bend)**
4. **Right Ashwa Sanchalanasana (Equestrian Pose - Right Leg)**
5. **Left Ashwa Sanchalanasana (Equestrian Pose - Left Leg)**
6. **Dandasana (Stick Pose)**
7. **Ashtanga Namaskara (Eight-Limbed Pose)**
8. **Bhujangasana (Cobra Pose)**
9. **Adho Mukha Svanasana (Downward-Facing Dog Pose)**

## Usage 
This version works only when you are standing to your right. That means that, when you are standing in front of the camera, you should turn towards your right and then it will work. This was done because it is hard to detect the landmark points for most poses when we are facing the camera from the front. The functionality could easily be implemented when you turn towards your left also, but was not implemented due to time constraints. It will be implemented in an update very soon.

   **Backend**
   1. You will be given a menu with different asana names.
   2. Type any name from the menu.
   3. Go in front of the camera.
   4. Turn to your right.
   5. Make sure the points are being mapped properly and you are in the frame.
   6. Do your yoga pose and enjoy audio feedback from the application.
   7. Just press Ctrl-C on the terminal to end the application.

   **Frontend**
   1. Run the server.
   2. Open the application.
   3. Select a yoga pose.
   4. The application will start a camera.
   5. Try to do the pose you've chosen within the frame.
   6. You'll receive text feedback on whether your pose is correct or not.

# asana_images

This folder has images from the internet of people doing the asanas we chose. It also contains flattering images of the team attempting to do them too. We used these images to create landmarks for ideal poses and practical expectations from the users using our application. 

# backend

## ideal_landmarks_data.py & absolutely_ideal_landmarks_data.py

These files list the nine selected yoga poses for which ideal body landmarks are provided as normalized 2D coordinates.
The landmarks for the 9 poses mentioned are included with ideal 2D body landmark coordinates for posture analysis and detection tasks.


## PoseModule.py

### Class: `PoseDetector`

#### 1. **`__init__(self, mode=False, upBody=False, smooth=True, detectionCon=0.5, trackCon=0.5)`**
   The constructor initializes the PoseDetector object using MediaPipe's pose estimation model.
   
   **Parameters:**
   - `mode`: A boolean value that determines if the pose detection should work in static image mode or video stream mode. By default, this is set to `False` for video stream mode.
   - `upBody`: A boolean that specifies whether only the upper body should be tracked. Default is `False` for full-body tracking.
   - `smooth`: A boolean value to enable or disable smoothing of the detected landmarks. By default, smoothing is enabled (`True`).
   - `detectionCon`: The minimum confidence required for pose detection, with a default value of 0.5.
   - `trackCon`: The minimum confidence required for pose tracking, set to 0.5 by default.

#### 2. **`findPose(self, frame, draw=True)`**
   This method processes a frame to detect pose landmarks. It converts the frame from BGR (used by OpenCV) to RGB format (used by MediaPipe) and applies the pose detection model.
   
   **Parameters:**
   - `frame`: The input video frame where pose detection is to be performed.
   - `draw`: A boolean flag indicating whether to draw the detected pose landmarks on the frame. By default, it's set to `True`.

   **Returns:**
   - The processed frame, with the landmarks drawn if `draw=True`.

#### 3. **`findPosition(self, frame, draw=False)`**
   This function retrieves the (x, y) coordinates of detected pose landmarks from the frame.
   
   **Parameters:**
   - `frame`: The input frame containing the detected pose.
   - `draw`: A boolean flag to determine whether the landmark points should be labeled and drawn on the frame. Default is `False`.

   **Returns:**
   - A list `lmlist` containing the (x, y) coordinates of the detected landmarks.

#### 4. **`ChangeColor(self, frame, color=(0, 255, 0), draw=True)`**
   This method changes the color of the lines connecting the detected pose landmarks.
   
   **Parameters:**
   - `frame`: The input frame where the connections between pose landmarks are drawn.
   - `color`: A tuple representing the RGB color to be used for the connections, defaulting to green `(0, 255, 0)`.
   - `draw`: A boolean flag to indicate whether to redraw the connections with the new color. Default is `True`.

   **Returns:**
   - The modified frame with the connections drawn in the specified color.

#### 5. **`map_landmarks(self, landmarks)`**
   This method maps the raw landmark list to specific body parts (e.g., 'left_eye', 'right_shoulder'). The landmarks from MediaPipe are converted into a dictionary where the body part names are the keys, and the (x, y) coordinates are the values.
   
   **Parameters:**
   - `landmarks`: A list containing the detected landmarks in (x, y) format.

   **Returns:**
   - A dictionary `landmark_dict` mapping body part names to their corresponding (x, y) coordinates.

#### 6. **`map_joints(self, landmark_dict)`**
   This method uses three landmarks to define key joints (such as 'left_knee_joint'). It calculates the points that form each joint by taking three corresponding landmarks and returning them in a dictionary.
   
   **Parameters:**
   - `landmark_dict`: A dictionary of landmarks mapped to body parts.

   **Returns:**
   - A dictionary `joint_dict` that maps joint names to lists of three points used to form that joint.

#### 7. **`map_asana_joints(self)`**
   This method creates a mapping of joints required for specific yoga poses. It defines which joints are important for evaluating the correctness of each asana (pose).
   
   **Returns:**
   - A dictionary `asana_to_joint` that maps each yoga pose to a list of the key joints to be evaluated.

#### 8. **`get_joints_for_asana(self, asana, asana_to_joint, joint_dict)`**
   This method retrieves the relevant joints for a specific yoga pose based on the `asana_to_joint` mapping. It filters the joints that are necessary for analyzing the specified asana.
   
   **Parameters:**
   - `asana`: The name of the yoga pose being analyzed.
   - `asana_to_joint`: A dictionary that maps asanas to the joints required for evaluating them.
   - `joint_dict`: A dictionary that maps joints to their corresponding points.

   **Returns:**
   - A dictionary containing the joints required to evaluate the specified asana.

#### 9. **`calculate_angle(self, points)`**
   This method calculates the angle between three points (such as shoulder, elbow, and wrist) to evaluate the posture or alignment at key joints in the body.
   
   **Parameters:**
   - `points`: A list of three points, where each point is represented by (x, y) coordinates. These points typically represent a joint and the two bones connected to it.

   **Returns:**
   - The angle (in degrees) formed between the three points, which can be used to assess the pose's accuracy.

---

## generator.py

### 1. **`euclidean_distance(self, point1, point2)`**:
   - This function calculates the Euclidean distance between two points in 2D space. 
   - The formula used is:
     \[
     \text{distance} = \sqrt{(x_2 - x_1)^2 + (y_2 - y_1)^2}
     \]
   - It is used to measure the difference in position between corresponding landmarks in two poses.

### 2. **`normalize_landmarks(self, landmarks, reference_idx)`**:
   - This function normalizes a set of landmarks relative to a reference landmark (e.g., the center of the body).
   - It subtracts the coordinates of the reference landmark (indicated by `reference_idx`) from all other landmarks, effectively centering the pose around the reference point.
   - Normalization helps make the pose comparison more robust to shifts in position or scale.

### 3. **`compare_poses(self, landmarks1, landmarks2)`**:
   - This function compares two sets of landmarks by calculating the total and average Euclidean distance between corresponding points in both poses.
   - The closer the average distance is to zero, the more similar the two poses are.
   - It loops over all the landmarks and calculates the difference between the two poses.

### 4. **`get_wrong_joints(self, asana, correct_landmarks, input_landmarks, thresh)`**:
   - This function identifies joints where the user's pose deviates significantly from the correct or reference pose.
   - First, it maps the landmarks to specific joints using the `detector.map_landmarks` and `detector.map_joints` functions.
   - Then, it calculates the angles for each joint in both the correct and input poses using `detector.calculate_angle`.
   - For each joint, it compares the angles and identifies if the deviation exceeds the given threshold (`thresh`).
   - If a joint’s angle is off, the function records whether the user needs to increase or decrease the angle and returns a dictionary of the wrong joints and necessary corrections.

### 5. **`resize_image(image, max_width=800, max_height=600)`**:
   - This function resizes an image to ensure it fits within a maximum width and height.
   - If the image is larger than the defined size limits (`max_width` and `max_height`), it scales the image down proportionally to fit.
   - This is useful for speeding up processing by reducing the image size before pose detection.

## pose_equal_check.py

### Class: `PoseSimilarity`

#### 1. **`euclidean_distance(self, point1, point2)`**
   This function calculates the Euclidean distance between two points, which is used to compare the spatial position of corresponding landmarks in different poses.

   **Parameters:**
   - `point1`: The first point represented as (x, y) coordinates.
   - `point2`: The second point represented as (x, y) coordinates.

   **Returns:**
   - The Euclidean distance between the two points.

#### 2. **`normalize_landmarks(self, landmarks, reference_idx)`**
   This method normalizes the landmark positions based on a reference point. It subtracts the reference point from all the landmarks, ensuring that the poses are compared relative to a common point.

   **Parameters:**
   - `landmarks`: A list of (x, y) coordinates representing the detected pose landmarks.
   - `reference_idx`: The index of the reference landmark used for normalization (e.g., the left hip).

   **Returns:**
   - A list of normalized landmarks where each point is adjusted based on the reference point.

#### 3. **`compare_poses(self, landmarks1, landmarks2, threshold=0.1)`**
   This function compares two sets of pose landmarks by calculating the average Euclidean distance between corresponding points. The comparison helps to assess the similarity between two poses.

   **Parameters:**
   - `landmarks1`: The first set of landmarks (e.g., from the current pose).
   - `landmarks2`: The second set of landmarks (e.g., from the correct pose).
   - `threshold`: The maximum allowable average distance between landmarks for the poses to be considered similar. Default is `0.1`.

   **Returns:**
   - The average Euclidean distance between the two sets of landmarks.

#### 4. **`get_wrong_joints(self, asana, correct_landmarks, input_landmarks, thresh)`**
   This method compares the key joints of two poses (the correct pose and the input pose) and identifies which joints have significant angular differences. It calculates the angles at specific joints and determines if they deviate from the correct angles by more than a given threshold.

   **Parameters:**
   - `asana`: The name of the yoga pose being evaluated.
   - `correct_landmarks`: The set of correct pose landmarks for the given asana.
   - `input_landmarks`: The set of input landmarks from the current pose.
   - `thresh`: The angular threshold used to determine if a joint is significantly misaligned.

   **Returns:**
   - A dictionary `wrong_joints` where the keys represent the misaligned joints and the values indicate whether the joint angle needs to be increased or decreased.

#### 5. **`isSimilar(self, pose_name, input_landmarks, euclidean_threshold)`**
   This function checks if the input pose matches a correct pose based on a Euclidean distance threshold. It compares the input pose against multiple correct poses for the same asana and returns the closest match.

   **Parameters:**
   - `pose_name`: The name of the yoga pose being evaluated.
   - `input_landmarks`: The set of landmarks from the current input pose.
   - `euclidean_threshold`: The maximum allowable average Euclidean distance between landmarks for the poses to be considered similar.

   **Returns:**
   - A tuple `(is_similar, closest_landmarks)` where `is_similar` is `True` if the pose is similar, and `closest_landmarks` is the set of correct landmarks that are closest to the input pose.

---

### Function: `resize_image(image, max_width=800, max_height=600)`

This utility function resizes the input image to fit within the specified width and height constraints while maintaining the aspect ratio.

**Parameters:**
- `image`: The input image to be resized.
- `max_width`: The maximum allowed width for the resized image. Default is `800`.
- `max_height`: The maximum allowed height for the resized image. Default is `600`.

**Returns:**
- The resized image, maintaining its original aspect ratio.

---

### Main Function: `if __name__ == "__main__"`

This section provides an example of how to use the `PoseSimilarity` class and the pose detector to analyze two images and compare their poses.

1. **Pose Detection:**
   The `PoseDetector` is used to detect the pose landmarks from two input images: `Padmasana.jpeg` (an incorrect pose) and `correct_padmasana.jpeg` (the correct pose).
   
2. **Landmark Extraction:**
   MediaPipe's `pose.process()` is used to extract the landmarks from the RGB frames, converting them from BGR to RGB. The landmarks are then normalized relative to the first landmark.

3. **Pose Comparison:**
   - The function normalizes the landmarks using the `normalize_landmarks` function and compares the poses using `compare_poses`.
   - It also identifies the incorrect joints using `get_wrong_joints`.

4. **Timing Information:**
   - The script calculates the time elapsed between frames using `time.time()` to measure performance.

## main.py

The main.py file captures live video from a webcam, detects human poses using MediaPipe, and evaluates them against predefined ideal poses for feedback. It utilizes text-to-speech functionality to provide real-time audio guidance on pose accuracy and adjustments.

### Initialization

1. **`import` statements**:
   Various libraries are imported at the beginning, including:
   - `cv2` for handling video capture and image processing.
   - `time` for measuring time intervals.
   - `PoseModule` for detecting human poses (created elsewhere in your project).
   - `mediapipe` for MediaPipe's pose detection.
   - `pose_equal_check` for pose comparison functionality using the `PoseSimilarity` class.
   - `pygame` for playing audio using the text-to-speech function.
   - `gtts` for generating speech from text using Google's TTS service.
   - `threading` to allow concurrent execution of code (e.g., playing speech in the background).

2. **`warnings.filterwarnings()`**:
   Warnings related to protobuf files are suppressed to avoid cluttering the output with unnecessary warnings.

---

### Pose Detection and TTS Setup

3. **Pose Detector Initialization**:
   - `detector = pm.PoseDetector()` initializes a pose detector using your `PoseModule`.
   - `pose = mpPose.Pose()` initializes MediaPipe's Pose estimation solution.
   - `poseEqualityDetector = pec.PoseSimilarity()` initializes the `PoseSimilarity` class, which is used to compare poses and identify wrong joints.

4. **TTS Setup**:
   - `pygame.mixer.init()` initializes the mixer from `pygame` to play audio files for the text-to-speech functionality.

---

### Function: `text_to_speech(text)`

This function converts the input text to speech and plays it using the `gTTS` (Google Text-to-Speech) API and `pygame`.

- **Steps**:
   - The text is converted to speech using `gTTS`.
   - An in-memory file (`mp3_fp`) is created to hold the generated speech.
   - The speech is loaded into `pygame` and played.
   - The function checks periodically if the audio is still playing to prevent the program from blocking during playback.

---

### Function: `menu()`

This function prints out the list of yoga poses for the user to choose from.

---

### Main Program Execution

1. **TTS announcement**:
   `text_to_speech("Program Starting.")` announces that the program is starting using the TTS function.

2. **Pose Menu**:
   - The `menu()` function displays a list of yoga poses for the user to choose from.
   - `pose_name = input()` reads the user's choice of pose for the session.

3. **Video Capture**:
   - `vid = cv.VideoCapture(0)` opens the webcam (device 0) for capturing live video.

4. **Main Loop**:
   A loop continuously captures frames from the webcam, processes them for pose detection, and checks the pose every 5 seconds.

---

### Inside the Main Loop

1. **Frame Capture**:
   - `isTrue, input_frame = vid.read()` captures a frame from the webcam.
   - The frame is resized using a scale factor to maintain the aspect ratio while increasing its size by 1.5 times.

2. **Pose Detection**:
   - `input_frame = detector.findPose(input_frame)` detects the pose in the current frame.
   - `input_landmarks = detector.findPosition(input_frame)` retrieves the pose landmarks (body keypoints).
   - If no landmarks are detected, the loop continues to the next frame.

3. **Pose Normalization**:
   The detected landmarks are normalized based on a reference point (e.g., left hip at index 0) using the `PoseSimilarity.normalize_landmarks()` method.

4. **Pose Comparison**:
   - Every 5 seconds, the current input pose is compared with the correct pose using `PoseSimilarity.isSimilar()`. 
   - If the input pose is similar to the correct one, it checks for incorrect joint angles using `PoseSimilarity.get_wrong_joints()`.

5. **TTS Feedback**:
   - If the pose is correct, a message "You're doing it absolutely right" is spoken.
   - If the pose has wrong joint angles, the feedback will indicate which joints need adjustment (e.g., "increase angle at left knee").
   - If the pose is not similar, the user is told "Thoda galat."

6. **Video Display**:
   - The input frame with the detected pose is displayed in a window using `cv.imshow()`.

7. **Exit Condition**:
   - The loop continues until the user presses the 'q' key, which breaks the loop and closes the video window.

---

### Cleanup

After the loop exits, the video window is destroyed using `cv.destroyAllWindows()`.

# frontend

The application made uses websockets to connect the client, that sends encoded images to the server, where all the backend processing occurs, then sends back a status to indicate the level of correctness of the pose performed on camera.

## FlutterFiles

Only files that were modified are included. The rest of the files required to run can be obtained by creating a new Flutter project on Android Studio.

### lib/main.dart

1. **Main Application Entry**:
   - The `main` function initializes the app, setting `HomePage` as the default screen.

2. **HomePage**:
   - Displays a list of yoga poses (asanas) represented by images.
   - Shows the current date and day of the week in the app bar.
   - Each pose is a tappable button that navigates to `CameraScreen` for further interaction.

3. **CameraScreen**:
   - Utilizes the device camera to capture images periodically for pose analysis.
   - Establishes a WebSocket connection to send captured images for pose detection.
   - Displays status messages indicating the detection results: no pose, incorrect pose, successful pose, or partial success.

4. **Camera Handling**:
   - Initializes the camera and captures images at regular intervals.
   - Compresses images before sending them via WebSocket.
   - Allows toggling between front and back cameras.

5. **WebSocket Communication**:
   - Listens for detection results from the server and updates the pose status accordingly.
   - Handles connection errors and closure.

6. **UI Elements**:
   - The app uses a `Scaffold` for layout and a `Column` for stacking UI elements.
   - Status messages are displayed at the bottom of the camera view.

7. **Asana Naming**:
   - Provides a method to retrieve the name of the asana based on the selected number, facilitating a user-friendly interface.

### pubspec.yaml

Dependencies for camera, image, web_socket_channel, flutter_svg, intl were added.

Directories `fonts` and `assets` were added under assets:

Fonts were listed, alongside their variants.

### assets/ & fonts/

These folders contain all the images (png, jgeg), svg and font files (otf, ttf) required to build the apk.

## Server/main-server-v5.py

This file acts like the server, where processing occurs and feedback for the pose captured in the app is sent back.

### Key Components

1. **Imports**: 
   - Various libraries are imported, including OpenCV for image processing, MediaPipe for pose detection, threading for concurrent execution, and gTTS for text-to-speech.

2. **Global Variables**:
   - `detector`: An instance of `PoseDetector` for detecting human poses.
   - `num_to_asana`: A dictionary mapping asana numbers to their names.

3. **Functions**:

   - **`text_to_speech(text)`**:
     - Converts the provided text into speech using Google Text-to-Speech (gTTS) and plays it using Pygame.
     - Utilizes an in-memory file to avoid reinitializing the Pygame mixer.
     - Runs in a separate thread to prevent blocking the main execution.

   - **`asanaCheck(asanaNum, input_landmarks)`**:
     - Takes an asana number and a list of landmarks as input.
     - Checks if the detected pose is similar to the expected pose using the `PoseSimilarity` class.
     - Returns:
       - `2` if the pose is correct.
       - `1` if the pose is incorrect.
       - `0` if no landmarks are detected.

   - **`FeedbackTTS(asanaCheckOutput, asanaNum, input_landmarks)`**:
     - Provides feedback based on the results from `asanaCheck`.
     - Limits feedback frequency to every 5 seconds.
     - Plays a specific message depending on the pose's correctness:
       - If the pose is incorrect, it says "Thoda galat."
       - If correct, it checks for wrong joints and gives specific feedback on which angles need adjustment.

   - **`bytes_to_cv_image(byte_stream)`**:
     - Converts a byte stream (image data) into an OpenCV image.
     - Uses NumPy to interpret the byte data and OpenCV to decode it.

   - **`websocket_handler(websocket, path)`**:
     - Asynchronously handles incoming WebSocket messages.
     - Calls `recognize_asana` with the received message and sends back the response.

   - **`recognize_asana(message)`**:
     - Processes the incoming WebSocket message:
       - Decodes the JSON to extract the asana number and image data.
       - Converts the base64 image data into a CV image.
       - Uses the `PoseDetector` to find the pose in the image and obtain landmarks.
       - Calls `asanaCheck` to determine the pose's correctness and returns a JSON response indicating the status.

### Execution Flow

- The script initializes the text-to-speech feature and sets up a WebSocket server on port `8765`.
- The server listens for incoming messages, processes each message to recognize the yoga pose, and sends back feedback based on the recognition results.

### Notes
- The pose detection logic relies on the `PoseModule` and `pose_equal_check` which aren provided in the `backend` folder and contain the actual implementation of the pose detection algorithms.
- The application combines computer vision and audio feedback to create an interactive experience for users practicing yoga.

# Contribution

## Created by
### Team TomaToeSS - ZenLegacy 2024
- Shashwat Chaturvedi
- Shiven Phogat
- Tadikonda Venkata Sai Chaitanya
- Tahir Mohammed Khadarabad

Feel free to open issues or pull requests to contribute to the project. Suggestions for new features, bug fixes, or improvements are welcome!

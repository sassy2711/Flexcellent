import numpy as np
import cv2 as cv
import mediapipe as mp
import numpy as np
import time
from . import PoseModule as pm
from .ideal_landmarks_data import ideal_landmarks as ideal_landmarks_data
from .absolutely_ideal_landmarks_data import absolutely_ideal_landmarks as absolutely_ideal_landmarks_data


ideal_landmarks = ideal_landmarks_data
absolutely_ideal_landmarks = absolutely_ideal_landmarks_data
detector = pm.PoseDetector()
mp_pose = mp.solutions.pose
pose = mp_pose.Pose()
mp_drawing = mp.solutions.drawing_utils
asana_to_joint = detector.map_asana_joints()
ctime =0
ptime = time.time()
class PoseSimilarity():
    # Function to calculate Euclidean distance between two points
    def euclidean_distance(self, point1, point2):
        return np.sqrt((point1[0] - point2[0])**2 + (point1[1] - point2[1])**2)
    
    # Function to normalize key points based on a reference point
    def normalize_landmarks(self, landmarks, reference_idx):
        ref_point = landmarks[reference_idx]
        normalized_landmarks = [(point[0] - ref_point[0], point[1] - ref_point[1]) for point in landmarks]
        return normalized_landmarks
    
    # Function to compare two sets of pose landmarks
    def compare_poses(self, landmarks1, landmarks2, threshold=0.1):
        total_distance = 0
        for i in range(len(landmarks1)):
            total_distance += self.euclidean_distance(landmarks1[i], landmarks2[i])
        avg_distance = total_distance / len(landmarks1)
        return avg_distance
    
    def get_wrong_joints(self, asana, correct_landmarks, input_landmarks, thresh):
        correct_landmark_dict = detector.map_landmarks(correct_landmarks)
        correct_joints_dict = detector.map_joints(correct_landmark_dict)
        correct_joints_dict=detector.get_joints_for_asana(asana,asana_to_joint,correct_joints_dict)

        input_landmark_dict = detector.map_landmarks(input_landmarks)
        input_joints_dict = detector.map_joints(input_landmark_dict)
        input_joints_dict=detector.get_joints_for_asana(asana,asana_to_joint,input_joints_dict)

        wrong_joints = {}
        for i in correct_joints_dict:
            correct_angle = detector.calculate_angle(correct_joints_dict[i])
            input_angle = detector.calculate_angle(input_joints_dict[i])
            diff = correct_angle - input_angle
            if(abs(diff)>thresh):
                if(diff>0):
                    wrong_joints[i] =  (i, "increase")
                else:
                    wrong_joints[i] = (i, "decrease")
        return wrong_joints
    
    def isSimilar(self, pose_name, input_landmarks, euclidean_threshold):
        correct_landmarks = ideal_landmarks[pose_name] + absolutely_ideal_landmarks[pose_name]
        mini = float('inf')
        closest_landmarks = []
        flag = 0
        for i in correct_landmarks:
            dist = self.compare_poses(i, input_landmarks, euclidean_threshold)
            if(dist<euclidean_threshold):
                print("You're doing it right.")
                flag = 1
            if(dist<mini):
                mini = dist
                closest_landmarks = i
        
        if(flag):
            return (True, closest_landmarks)
        else:            
            return (False, closest_landmarks)
        #return self.get_wrong_joints(pose_name, closest_landmarks, input_landmarks, angular_threshold)
        

def resize_image(image, max_width=800, max_height=600):
    height, width = image.shape[:2]
    if width > max_width or height > max_height:
        scaling_factor = min(max_width / width, max_height / height)
        new_size = (int(width * scaling_factor), int(height * scaling_factor))
        return cv.resize(image, new_size)
    return image




if __name__ == "__main__":
    # Example usage
    pose_sim = PoseSimilarity()
    
    

    # Example usage with your images
    frame1 = cv.imread("Padmasana.jpeg")
    frame1 = resize_image(frame1)
    #cv.imshow("Without_detection", frame1_resized)
    frame1 = detector.findPose(frame1)
    lmlist1 = detector.findPosition(frame1)
    frame2 = cv.imread("correct_padmasana.jpeg")
    frame2 = resize_image(frame2)
    frame2 = detector.findPose(frame2)
    lmlist2 = detector.findPosition(frame2)
    #cv.imshow("Corrected_padmasana", frame1)
    #cv.imshow("Wrong_padmasana", frame2)
    #Example landmarks for two poses (these should be passed in from another part of your code)
    frame_rgb1 = cv.cvtColor(frame1, cv.COLOR_BGR2RGB)
    result1 = pose.process(frame_rgb1)
    landmarks1 = []
    if result1.pose_landmarks:
        for lm in result1.pose_landmarks.landmark:
            landmarks1.append((lm.x, lm.y))

    frame_rgb2 = cv.cvtColor(frame2, cv.COLOR_BGR2RGB)
    result2 = pose.process(frame_rgb2)
    landmarks2 = []
    if result2.pose_landmarks:
        for lm in result2.pose_landmarks.landmark:
            landmarks2.append((lm.x, lm.y))
    
    # print("landmarks1: ", landmarks1)
    # print("lmlist1: ", lmlist1)
    # print("landmarks2: ", landmarks2)
    # print("lmlist2: ", lmlist2)




    # Normalize landmarks with respect to a reference point (e.g., left hip index = 24)
    normalized_landmarks1 = pose_sim.normalize_landmarks(lmlist1, reference_idx=0)
    normalized_landmarks2 = pose_sim.normalize_landmarks(lmlist2, reference_idx=0)
    
    # Compare the poses
    wrong_joints = pose_sim.get_wrong_joints(normalized_landmarks1, normalized_landmarks2, 20)
    if(pose_sim.compare_poses(normalized_landmarks1, normalized_landmarks2, 0.1)):
        print("Correct")
    else:
        for i in wrong_joints:
            print(i, wrong_joints[i])
    ctime = time.time()
    print(ctime-ptime)


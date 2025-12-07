import numpy as np
import cv2 as cv
import mediapipe as mp
import numpy as np
import time
from . import PoseModule as pm
from .pose_equal_check import PoseSimilarity

# Initialize MediaPipe Pose Detection
detector = pm.PoseDetector()
mp_pose = mp.solutions.pose
pose = mp_pose.Pose()
mp_drawing = mp.solutions.drawing_utils
ctime =0
ptime = time.time()
poses_names=["pranamasana","hastauttanasana","hastapadasana","right_ashwa_sanchalanasana","dandasana","ashtanga_namaskara","bhujangasana","adho_mukha_svanasana","ashwa_sanchalanasana"]
asana_to_joint=detector.map_asana_joints()
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
    def compare_poses(self, landmarks1, landmarks2):
        total_distance = 0
        for i in range(len(landmarks1)):
            total_distance += self.euclidean_distance(landmarks1[i], landmarks2[i])
        avg_distance = total_distance / len(landmarks1)
        return avg_distance
    
    def get_wrong_joints(self, asana,correct_landmarks, input_landmarks, thresh):
        
        

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
                    wrong_joints[i] =  (diff, correct_angle, input_angle, "increase")
                else:
                    wrong_joints[i] = (diff, correct_angle, input_angle, "decrease")
        return wrong_joints

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
    
    
    #asana=input()
    # orientations=["_straight","_left","_right"]
    # asanas_dict={}
    # lmlists=[]
    # Example usage with your images
    # for i in orientations:
    # for asana in poses_names:
    asana="ashtanga_namaskara"
    print("ideal_landmarks["+'"'+asana+'"'+"] = []")
    for i in range(6):
        frame1 = cv.imread(asana+"("+str(i+4)+")"+".jpeg")
        # if(i == 0):
        #     frame1 = cv.imread(asana+"("+str(i+1)+")"+".jpg")
        # else:
        #     frame1 = cv.imread(asana+"("+str(i+1)+")"+".jpeg")
        frame1 = resize_image(frame1)
    #cv.imshow("Without_detection", frame1_resized)
        frame1 = detector.findPose(frame1)
        lmlist1 = detector.findPosition(frame1)
        normalized_landmarks1 = pose_sim.normalize_landmarks(lmlist1, reference_idx=0)
        #print("ideal_landmarks["+'"'+asana+'"'+"].append("+str(normalized_landmarks1)+")")
        #print("\n")
    ideal=[]
    ideal.append([[0.35895463824272156, 0.20281532406806946], [0.35463595390319824, 0.22049576044082642], [0.3553725481033325, 0.22193455696105957], [0.35617923736572266, 0.22358958423137665], [0.3554527759552002, 0.22054114937782288], [0.3566543459892273, 0.22197259962558746], [0.35786157846450806, 0.22371503710746765], [0.37034621834754944, 0.23991653323173523], [0.371420294046402, 0.23829787969589233], [0.372281938791275, 0.19913111627101898], [0.37309151887893677, 0.19974231719970703], [0.42230743169784546, 0.23818714916706085], [0.4267737865447998, 0.22293226420879364], [0.36263763904571533, 0.16735711693763733], [0.36578136682510376, 0.14550209045410156], [0.2941613793373108, 0.14439605176448822], [0.2868228256702423, 0.1305263340473175], [0.2695602774620056, 0.14243540167808533], [0.2611899971961975, 0.12370029091835022], [0.26734036207199097, 0.14909586310386658], [0.2602332830429077, 0.13641008734703064], [0.2756321132183075, 0.15135787427425385], [0.2683088183403015, 0.1410904973745346], [0.5541060566902161, 0.36975666880607605], [0.5651354789733887, 0.3640387952327728], [0.5230546593666077, 0.5761637687683105], [0.5303618907928467, 0.5842007398605347], [0.47240370512008667, 0.7783742547035217], [0.47052276134490967, 0.791135847568512], [0.45394647121429443, 0.8081939816474915], [0.4492119252681732, 0.8210382461547852], [0.5210372805595398, 0.8336531519889832], [0.5247960686683655, 0.8476090431213379]])


    ideal.append([[0.5687236189842224, 0.13345174491405487], [0.5594015717506409, 0.14164121448993683], [0.5590642094612122, 0.14443747699260712], [0.5586158633232117, 0.1479499489068985], [0.5583914518356323, 0.14248791337013245], [0.557300865650177, 0.14553092420101166], [0.556181013584137, 0.1490420252084732], [0.5567854046821594, 0.1783217042684555], [0.5528435707092285, 0.17733794450759888], [0.5750820636749268, 0.14379459619522095], [0.5731013417243958, 0.14595143496990204], [0.580054759979248, 0.24721887707710266], [0.5556455850601196, 0.24190658330917358], [0.4897020757198334, 0.2517324984073639], [0.4613996148109436, 0.2502882480621338], [0.3963431119918823, 0.2899494171142578], [0.36762067675590515, 0.289299875497818], [0.36986982822418213, 0.31706538796424866], [0.3414992392063141, 0.3129805326461792], [0.36507555842399597, 0.3134972155094147], [0.3386645019054413, 0.320243775844574], [0.3798287510871887, 0.30221712589263916], [0.3496262729167938, 0.3109370470046997], [0.6969961524009705, 0.4046895205974579], [0.6781734824180603, 0.4153379797935486], [0.6083808541297913, 0.6919066309928894], [0.5970920324325562, 0.713707447052002], [0.4981353282928467, 1.0051665306091309], [0.48125651478767395, 1.0487842559814453], [0.4645255506038666, 1.064236044883728], [0.4558079242706299, 1.089485764503479], [0.5389348864555359, 1.0480855703353882], [0.5356442332267761, 1.06556236743927]])


    ideal.append([[0.4293888211250305, 0.1917852759361267], [0.4132271111011505, 0.20036421716213226], [0.41340893507003784, 0.20205792784690857], [0.4137383699417114, 0.20404206216335297], [0.4113621413707733, 0.20162969827651978], [0.4102233052253723, 0.20396743714809418], [0.40921416878700256, 0.2065081149339676], [0.4177219867706299, 0.22855490446090698], [0.4144575893878937, 0.2292698323726654], [0.4490131437778473, 0.19852575659751892], [0.44551342725753784, 0.19971401989459991], [0.4903206527233124, 0.2711751163005829], [0.4827456474304199, 0.26595795154571533], [0.3681868314743042, 0.23890560865402222], [0.3437161445617676, 0.23158805072307587], [0.22054806351661682, 0.25487446784973145], [0.20530658960342407, 0.23184098303318024], [0.18790823221206665, 0.25260448455810547], [0.1658303439617157, 0.2351047247648239], [0.18349581956863403, 0.2668827176094055], [0.16238315403461456, 0.24862456321716309], [0.19766998291015625, 0.2758750319480896], [0.17530205845832825, 0.25357410311698914], [0.6484917402267456, 0.4552537500858307], [0.6461768746376038, 0.45319005846977234], [0.5811824798583984, 0.6512591242790222], [0.577327311038971, 0.6677859425544739], [0.4956187605857849, 0.8324366807937622], [0.4954391419887543, 0.8501495718955994], [0.46420735120773315, 0.8651151657104492], [0.4554383456707001, 0.8830150365829468], [0.5712674856185913, 0.866195797920227], [0.5649605393409729, 0.8843041062355042]])
    for i in ideal:
        i=pose_sim.normalize_landmarks(i, reference_idx=0)
        print(i)
    #     lmlists.append(lmlist1)
    # asanas_dict[asana]=lmlists
    frame2 = cv.imread("wrong_padmasana.jpeg")
    frame2 = resize_image(frame2)
    frame2 = detector.findPose(frame2)
    lmlist2 = detector.findPosition(frame2)
    cv.imshow("Corrected_padmasana", frame1)
    cv.imshow("Wrong_padmasana", frame2)
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
    for i in wrong_joints:
        print(i, wrong_joints[i])
    ctime = time.time()
    print(ctime-ptime)
    #print("Poses are similar" if are_similar else "Poses are different")
    cv.waitKey(100000)

import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
from mediapipe import solutions
from mediapipe.framework.formats import landmark_pb2
import cv2
import numpy as np
import threading
import queue
import math

class PersonalAI:
	def __init__(self, file_name='flexao1.mp4', model_path = 'pose_landmarker_full.task'):
		self.file_name = file_name
		self.model_path = model_path
		self.image_q = queue.Queue()

		with open(self.model_path, 'rb') as file:
			model_data = file.read()

		self.options = python.vision.PoseLandmarkerOptions(
						base_options=python.BaseOptions(model_asset_buffer=model_data),
						running_mode=python.vision.RunningMode.VIDEO)

	@staticmethod
	def find_angle(landmarks, p1,p2,p3):
		land = landmarks.pose_landmarks[0]

		x1,y1 = (land[p1].x, land[p1].y)
		x2,y2 = (land[p2].x, land[p2].y)
		x3,y3 = (land[p3].x, land[p3].y)

		angle = math.degrees(math.atan2(y3-y2,x3-x2)- math.atan2(y1-y2,x1-x2))

		if angle > 180:
			angle = 360 - angle
		return abs(angle)

	@staticmethod
	def find_height(landmarks, p):
		land = landmarks.pose_landmarks[0]

		height = land[p].y

		return height

	def draw_landmarks_on_image(self,rgb_image, detection_result):
		pose_landmarks_list = detection_result.pose_landmarks
		annotated_image = np.copy(rgb_image)

		# Loop through the detected poses to visualize.
		for idx in range(len(pose_landmarks_list)):
			pose_landmarks = pose_landmarks_list[idx]

			# Draw the pose landmarks.
			pose_landmarks_proto = landmark_pb2.NormalizedLandmarkList()
			pose_landmarks_proto.landmark.extend([
			  landmark_pb2.NormalizedLandmark(x=landmark.x, y=landmark.y, z=landmark.z) for landmark in pose_landmarks
			])
			solutions.drawing_utils.draw_landmarks(
			annotated_image,
			pose_landmarks_proto,
			solutions.pose.POSE_CONNECTIONS,
			solutions.drawing_styles.get_default_pose_landmarks_style())
		return annotated_image

	def process_video(self, draw, display):
		print('ok')
		with python.vision.PoseLandmarker.create_from_options(self.options) as landmarker:

			cap =cv2.VideoCapture(self.file_name)
			fps = cap.get(cv2.CAP_PROP_FPS)
			calc_ts = 0

			if not cap.isOpened():
				print('cap nao esta aberto')

			while cap.isOpened():
				ret, frame = cap.read()
				if not ret:
					break

				mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=frame)
				calc_ts += int(1000/fps)
				detection_result = landmarker.detect_for_video(mp_image,calc_ts)

				
				if draw:
					frame = self.draw_landmarks_on_image(frame, detection_result)	
				
				if display:	
					cv2.imshow('frame',frame)
					key = cv2.waitKey(5)
					if key == 27: 
						break
					
				frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
				self.image_q.put((frame, detection_result, calc_ts))
			cap.release()
			cv2.destroyAllWindows()
			self.image_q.put((1, 1,'done'))

	def run(self,draw= False, display=False):
		t1 = threading.Thread(target=self.process_video, args=(draw, display))
		t1.start()
if __name__ == '__main__':
	PersonalAI = PersonalAI()
	PersonalAI.run(True,True)
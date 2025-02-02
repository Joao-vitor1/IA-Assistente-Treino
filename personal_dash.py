import streamlit as st
import pandas as pd 
from personal_Ai import *
import time

# st.set_page_config(layout= "wide") #retira as margens esquerda e direita

def contador_socos(position, elbow_angle, height_elbow, height_hand, angle_elbow_hip, count):
	if position == "em guarda" and  elbow_angle > 150 and angle_elbow_hip > 85:
		position = "socando"
		count +=0.5

	elif (position == "socando") and  (elbow_angle < 80) and (angle_elbow_hip < 70):
		position = "em guarda"
		count +=0.5
	
	return (position, elbow_angle, count)







tipo = st.sidebar.selectbox("Tipo", ['flexoes','socos'])

tipo_model = st.sidebar.selectbox("nivel model", ['lite','full','heavy'])
model_path = 'pose_landmarker_'+tipo_model+'.task'


if tipo == 'socos':
	st.write("CONTADOR DE SOCOS")

	personal_Ai = PersonalAI('socos_eu.mp4',model_path)
	personal_Ai.run(draw = True)

	placeholder = st.empty()


	

	status_punch = 'relaxed'
	position_left = 'relaxed'
	position_rigth = 'relaxed'
	count_left = 0
	count_rigth = 0

	angle_elbow_hip_right = 0
	height_left_hand = 0
	height_left_elbow = 0
	height_right_hand=0
	height_right_elbow=0
	while True:

		frame, results, ts = personal_Ai.image_q.get()
		if ts == "done":
			break


		if len(results.pose_landmarks) > 0:
			elbow_angle_right = personal_Ai.find_angle(results,12,14,16)
			elbow_angle_left = personal_Ai.find_angle(results,11,13,15)

			height_right_elbow = 1 - personal_Ai.find_height(results, 12)
			height_left_elbow = 1 - personal_Ai.find_height(results, 11)

			height_right_hand = 1 - personal_Ai.find_height(results, 20)
			height_left_hand = 1 - personal_Ai.find_height(results, 19)

			angle_elbow_hip_right = personal_Ai.find_angle(results,14,12,24)
			angle_elbow_hip_left = personal_Ai.find_angle(results,13,11,23)


			if status_punch == 'relaxed':
				if (height_left_hand > height_left_elbow) and (height_right_hand > height_right_elbow) and (elbow_angle_right < 70) and (elbow_angle_left < 70):
					status_punch = 'ready'
					position_left = 'em guarda'
					position_rigth = 'em guarda'
				
			elif status_punch == 'ready':
				position_left, elbow_angle_left, count_left = contador_socos(position_left, elbow_angle_left,
																			 height_left_elbow, height_left_hand, 
																			 angle_elbow_hip_left, count_left)

				position_rigth, elbow_angle_right, count_rigth = contador_socos(position_rigth, elbow_angle_right, 
																				height_right_elbow, height_right_hand,
																				angle_elbow_hip_right,count_rigth)
				

		with placeholder.container():
			col1, col2 = st.columns([0.4,0.6])

			col1.image(frame)
			col2.markdown(f" **left in guard: **  {(height_left_hand > height_left_elbow)}")
			col2.markdown(f" **right in guard: **  {(height_right_hand > height_right_elbow)}")
			col2.markdown(" **status: ** " + status_punch)
			col2.markdown(" **status_left: ** " + position_left)
			col2.markdown(" **status_right: ** " + position_rigth)
			col2.markdown(f' **Count: **  {int(count_rigth+count_left)}')
			col2.markdown(f' **Count left: **  {int(count_left)}')
			col2.markdown(f' **Count right: **  {int(count_rigth)}')

			# time.sleep(0.2)

elif tipo == 'flexoes':
	st.write("CONTADOR DE FLEXÕES")

	personal_Ai = PersonalAI('flexao1.mp4', model_path)
	personal_Ai.run(draw = True)

	placeholder = st.empty()

	status = "relaxed"
	count = 0

	while True:
		frame, results, ts = personal_Ai.image_q.get()
		if ts == "done":
			break

		if len(results.pose_landmarks) > 0:
			elbow_angle_right = personal_Ai.find_angle(results,12,14,16)
			elbow_angle_left = personal_Ai.find_angle(results,11,13,15)
			hip_angle_right = personal_Ai.find_angle(results,12,24,26)
			hip_angle_left = personal_Ai.find_angle(results,11,23,25)

			
			
			if elbow_angle_right > 150 and elbow_angle_left > 150 and  hip_angle_left > 170:
				status = 'ready'
				direction = "down"

			if status == 'ready':
				if direction == "down" and elbow_angle_right < 90 and elbow_angle_left < 90:
					direction = "up"
					count +=0.5

				if direction == "up" and elbow_angle_right > 135 and elbow_angle_left > 135:
					direction = "down"
					count +=0.5
			
		
		with placeholder.container():
			col1, col2 = st.columns([0.4,0.6])

			col1.image(frame)
			col2.markdown("## **status: ** ##" + status)
			col2.markdown(f'## **Count: ** ## {int(count)}')


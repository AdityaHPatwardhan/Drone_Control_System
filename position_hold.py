#!/usr/bin/env python

'''

This python file runs a ROS-node of name drone_control which holds the position of e-Drone on the given dummy.
This node publishes and subsribes the following topics:

		PUBLICATIONS			SUBSCRIPTIONS
		/drone_command			/whycon/poses
		/alt_error				/pid_tuning_altitude
		/pitch_error			/pid_tuning_pitch
		/roll_error				/pid_tuning_roll
		/yaw_error		Float64		/pid_tuning_yaw
								/drone_yaw

Rather than using different variables, use list. eg : self.setpoint = [1,2,3,4], where index corresponds to x,y,z and yaw_value...rather than defining self.x_setpoint = 1, self.y_setpoint = 2
CODE MODULARITY AND TECHNIQUES MENTIONED LIKE THIS WILL HELP YOU GAINING MORE MARKS WHILE CODE EVALUATION.	
'''

# Importing the required libraries

from plutodrone.msg import *
from geometry_msgs.msg import PoseArray
from std_msgs.msg import Int16
from std_msgs.msg import Int64
from std_msgs.msg import Float64
from pid_tune.msg import PidTune
import rospy
import time
d_roll=0.0
i_roll=0.0

d_throt=0.0
i_throt=0.0

d_pitch=0.0
i_pitch=0.0

d_yaw=0.0
i_yaw=0.0


class Edrone():
	"""docstring for Edrone"""
	def __init__(self):
		
		rospy.init_node('drone_control')	# initializing ros node with name drone_control

		# This corresponds to your current position of drone. This value must be updated each time in your whycon callback
		# [x,y,z,yaw_value]
		self.drone_position = [0.0,0.0,0.0,0.0]	

		# [x_setpoint, y_setpoint, z_setpoint, yaw_value_setpoint]
		self.setpoint = [1.42,0.06,27.65,0.00] # whycon marker at the position of the dummy given in the scene. Make the whycon marker associated with position_to_hold dummy renderable and make changes accordingly


		#Declaring a cmd of message type PlutoMsg and initializing values
		self.cmd = PlutoMsg()
		self.cmd.rcRoll = 1500
		self.cmd.rcPitch = 1500
		self.cmd.rcYaw = 1500
		self.cmd.rcThrottle = 1500
		self.cmd.rcAUX1 = 1500
		self.cmd.rcAUX2 = 1500
		self.cmd.rcAUX3 = 1500
		self.cmd.rcAUX4 = 1500
		# self.cmd.plutoIndex = 0


		#initial setting of Kp, Kd and ki for [pitch, roll, throttle, yaw]. eg: self.Kp[2] corresponds to Kp value in throttle axis
		#after tuning and computing corresponding PID parameters, change the parameters
		self.Kp = [0,9.19,27,0]
		self.Ki = [0,0.023,0.035,0]
		self.Kd = [0,4.6,40.06,0]
		#-----------------------Add other required variables for pid here ----------------------------------------------
        
		self.prev_values = [0,0,0,0]
		self.min_values = [1200,1200,1200,1200]
		self.max_values = [1800,1800,1800,1800]
		








		# Hint : Add variables for storing previous errors in each axis, like self.prev_values = [0,0,0,0] where corresponds to [pitch, roll, throttle, yaw]
		#		 Add variables for limiting the values like self.max_values = [1800,1800,1800,1800] corresponding to [pitch, roll, throttle, yaw]
		#													self.min_values = [1200,1200,1200,1200] corresponding to [pitch, roll, throttle, yaw]
		#																	You can change the upper limit and lower limit accordingly. 
		#----------------------------------------------------------------------------------------------------------

		# This is the sample time in which you need to run pid. Choose any time which you seem fit. Remember the stimulation step time is 50 ms
		self.pid_time = 0.051	 # in seconds
		self.last_time = 0.0







		# Publishing /drone_command, /alt_error, /pitch_error, /roll_error, /yaw_error
		self.command_pub = rospy.Publisher('/drone_command', PlutoMsg, queue_size=1)
		#------------------------Add other ROS Publishers here-----------------------------------------------------
		self.roll_pub = rospy.Publisher('/roll_error',Int64,queue_size=10)
		self.pitch_pub = rospy.Publisher('/pitch_error',Int64,queue_size=10)
		self.throttle_pub = rospy.Publisher('/throt_error',Int64,queue_size=10)
		self.yaw_pub = rospy.Publisher('/yaw_error',Float64,queue_size=10)
		self.zero_pub=rospy.Publisher('/zeroline',Int16,queue_size=10)
		self.need_pub=rospy.Publisher('/path/need',Int16,queue_size=10)




		#-----------------------------------------------------------------------------------------------------------


		# Subscribing to /whycon/poses, /drone_yaw, /pid_tuning_altitude, /pid_tuning_pitch, pid_tuning_roll
		rospy.Subscriber('whycon/poses', PoseArray, self.whycon_callback)
		rospy.Subscriber('/pid_tuning_altitude',PidTune,self.altitude_set_pid)
		#-------------------------Add other ROS Subscribers here----------------------------------------------------
		rospy.Subscriber('/pid_tuning_pitch',PidTune,self.pitch_set_pid)
		rospy.Subscriber('/pid_tuning_roll',PidTune,self.roll_set_pid)
		rospy.Subscriber('/pid_tuning_yaw',PidTune,self.yaw_set_pid)
		rospy.Subscriber('/drone_yaw',Float64,self.yaw_callback)	
		

		






		#------------------------------------------------------------------------------------------------------------

		self.arm() # ARMING THE DRONE 


	# Disarming condition of the drone
	def disarm(self):
		self.cmd.rcAUX4 = 1100
		self.command_pub.publish(self.cmd)
		rospy.sleep(1)


	# Arming condition of the drone : Best practise is to disarm and then arm the drone.
	def arm(self):

		self.disarm()

		self.cmd.rcRoll = 1500
		self.cmd.rcYaw = 1500
		self.cmd.rcPitch = 1500
		self.cmd.rcThrottle = 1000
		self.cmd.rcAUX4 = 1500
		self.command_pub.publish(self.cmd)	# Publishing /drone_command
		rospy.sleep(1)	



	# Whycon callback function
	# The function gets executed each time when /whycon node publishes /whycon/poses 
	def whycon_callback(self,msg):
		self.drone_position[0] = msg.poses[0].position.x
		#--------------------Set the remaining co-ordinates of the drone from msg----------------------------------------------
		self.drone_position[1] = msg.poses[0].position.y
		self.drone_position[2] = msg.poses[0].position.z
		
		#---------------------------------------------------------------------------------------------------------------
    
	def yaw_callback(self,yaw2):
		self.drone_position[3] = yaw2.data
   

	# Callback function for /pid_tuning_altitude
	# This function gets executed each time when /tune_pid publishes /pid_tuning_altitude
	

	#----------------------------Define callback function like altitide_set_pid to tune pitch, roll and yaw as well--------------

	def pitch_set_pid(self,pit):
		self.Kp[0] = pit.Kp * 0.01 
		self.Ki[0] = pit.Ki * 0.00001
		self.Kd[0] = pit.Kd * 0.01

	def roll_set_pid(self,rol):
		self.Kp[1] = rol.Kp * 0.01 
		self.Ki[1] = rol.Ki * 0.00001
		self.Kd[1] = rol.Kd * 0.01

	def altitude_set_pid(self,alt):
		self.Kp[2] = alt.Kp * 0.01 # This is just for an example. You can change the fraction value accordingly
		self.Ki[2] = alt.Ki * 0.00001
		self.Kd[2] = alt.Kd * 0.01

	def yaw_set_pid(self,yaw1):
		self.Kp[3] = yaw1.Kp * 0.01 
		self.Ki[3] = yaw1.Ki * 0.08
		self.Kd[3] = yaw1.Kd * 0.01

	#----------------------------------------------------------------------------------------------------------------------


	
	
	def pid(self):
	#-----------------------------Write the PID algorithm here--------------------------------------------------------------
	
	# Steps:
	# 	1. Compute error in each axis. eg: error[0] = self.drone_position[0] - self.setpoint[0] ,where error[0] corresponds to error in x...
		self.seconds = time.time()
		current_time = self.seconds - self.last_time
		if(current_time >= self.pid_time):
		
			error_pitch=self.drone_position[0]-self.setpoint[0]
			error_roll=self.drone_position[1]-self.setpoint[1]	
			error_throttle=self.drone_position[2]-self.setpoint[2]
			error_yaw=self.drone_position[3]-self.setpoint[3]
	#	2. Compute the error (for proportional), change in error (for derivative) and sum of errors (for integral) in each axis. Refer Getting_familiar_with_PID.pdf to understand PID equation.
	#normal error is 
    #change in error is 
		#derror[0]=error[0]-self.prev_error[0]
		#derror[1]=error[1]-self.prev_error[1]
		#derror[2]=error[2]-self.prev_error[2]
		#derror[3]=error[3]-self.prev_error[3]
	#sum of previous errors and current error is
	    #ierror[0]=error[0]+ierror[0]
		#ierror[1]=error[1]+ierror[1]
		#ierror[2]=error[2]+ierror[2]
		#ierror[3]=error[3]+ierror[3] 	
	#	3. Calculate the pid output required for each axis. For eg: calcuate self.out_roll, self.out_pitch, etc.
		#out_pitch
			self.zero_pub.publish(Int16(0))
			global d_pitch
			global i_pitch
			self.pitch_pub.publish(Int64(error_pitch))
			i_pitch=(i_pitch+error_pitch)*self.Ki[0]
			self.out_pitch=(self.Kp[0]*error_pitch)+(i_pitch*self.pid_time)+(self.Kd[0]*((error_pitch-d_pitch)/self.pid_time))
			d_pitch=error_pitch
		

		#out_roll
			global i_roll
			global d_roll
			self.roll_pub.publish(Int64(error_roll))
			i_roll=(error_roll+i_roll)*self.Ki[1]		
			self.out_roll=(self.Kp[1]*error_roll)+(i_roll*self.pid_time)+(self.Kd[1]*((error_roll-d_roll)/self.pid_time))
			d_roll=error_roll
		
		#out_throttle
			global i_throt
			global d_throt
			self.throttle_pub.publish(Int64(error_throttle))
			i_throt=(error_throttle+i_throt)*self.Ki[2]
			self.out_throttle=(self.Kp[2]*error_throttle)+(i_throt*self.pid_time)+(self.Kd[2]*((error_throttle-d_throt)/self.pid_time))
			d_throt=error_throttle
		

		#out_yaw
			global i_yaw
			global d_yaw
			self.yaw_pub.publish(Float64(error_yaw)) #This 
			i_yaw=(error_yaw+i_yaw)*self.Ki[3]		
			self.out_yaw=self.Kp[3]*error_yaw+(i_yaw*self.pid_time)+(self.Kd[3]*(error_yaw-d_yaw)/self.pid_time)
			d_yaw=error_yaw
		
		
		#pitch
			self.cmd.rcPitch=1500 + self.out_pitch
			if self.cmd.rcPitch > self.max_values[0]:
				self.cmd.rcPitch = self.max_values[0]

			if self.cmd.rcPitch < self.min_values[0]:
				self.cmd.rcPitch = self.min_values[0]	
		#roll
			self.cmd.rcRoll=1500 + self.out_roll	
			if self.cmd.rcRoll > self.max_values[1]:
				self.cmd.rcRoll = self.max_values[1]
		
			if self.cmd.rcRoll < self.min_values[1]:
				self.cmd.rcRoll = self.min_values[1]


		#throttle
			self.cmd.rcThrottle=1500 + self.out_throttle
			if self.cmd.rcThrottle > self.max_values[2]:
				self.cmd.rcThrottle = self.max_values[2]

			if self.cmd.rcThrottle < self.min_values[2]:
				self.cmd.rcThrottle = self.min_values[2]
		#yaw
			self.cmd.rcYaw=1500 + self.out_yaw
			if self.cmd.rcYaw > self.max_values[3]:
				self.cmd.rcYaw = self.max_values[3]

			if self.cmd.rcYaw < self.min_values[3]:
				self.cmd.rcYaw = self.min_values[3]	
		
			self.command_pub.publish(self.cmd)
			self.last_time = self.seconds
			

		


	    
	#	4. Reduce or add this computed output value on the avg value ie 1500. For eg: self.cmd.rcRoll = 1500 + self.out_roll. LOOK OUT FOR SIGN (+ or -). EXPERIMENT AND FIND THE CORRECT SIGN
	#	5. Don't run the pid continously. Run the pid only at the a sample time. self.sampletime defined above is for this purpose. THIS IS VERY IMPORTANT.
	#	6. Limit the output value and the final command value between the maximum(1800) and minimum(1200)range before publishing. For eg : if self.cmd.rcPitch > self.max_values[1]:
	#																														self.cmd.rcPitch = self.max_values[1]	
         
	#	7. Update previous errors.eg: self.prev_error[1] = error[1] where index 1 corresponds to that of pitch (eg)
        #self.prev_error[0]=error[0]
		#self.prev_error[1]=error[1]
		#self.prev_error[2]=error[2]
		#self.prev_error[3]=error[3]
	#	8. Add error_sum









	#------------------------------------------------------------------------------------------------------------------------


		
		




if __name__ == '__main__':

	e_drone = Edrone()

	while not rospy.is_shutdown():
		e_drone.pid()

-- This script is used for realtime emulation of the environment in V-REP

function sysCall_init()

    saltree_handle=sim.getObjectHandle('Position_hoop1')
    mangotree_handle=sim.getObjectHandle('Position_hoop2')
    cashewtree_handle=sim.getObjectHandle('Position_hoop3')
    obstacle_handle=sim.getObjectHandle('obstacle_1')

    saltree_orient_handle=sim.getObjectHandle('Orientation_hoop1')


    -- Subscribing to the required topics 
    aruco_sub = simROS.subscribe('/aruco_marker_publisher/markers', 'aruco_msgs/MarkerArray', 'aruco_callback')
    whycon_sub = simROS.subscribe('/whycon/poses', 'geometry_msgs/PoseArray', 'whycon_callback')
    key_input = simROS.subscribe('/input_key', 'std_msgs/Int16', 'key_callback')

    scale_factor = {5.6,-5.1,10.4} -- Add the scale_factor you computed learned from the tutorial of whycon transformation
    whycon_gnd=30.250
end


function sysCall_actuation()

end

function sysCall_sensing()
    -- put your sensing code here
end

function sysCall_cleanup()
    -- do some clean-up here
end



function aruco_callback(msg)
   
    x1=msg.markers[1].pose.pose.orientation.x
    y1=msg.markers[1].pose.pose.orientation.y
    z1=msg.markers[1].pose.pose.orientation.z
    w1=msg.markers[1].pose.pose.orientation.w
    aruco_0={-x1,-y1,-z1,w1}
   -- x1=msg.markers[2].pose.pose.orientation.x
   -- y1=msg.markers[2].pose.pose.orientation.y
   -- z1=msg.markers[2].pose.pose.orientation.z
   -- w1=msg.markers[2].pose.pose.orientation.w
   -- aruco_1={x1,y1,z1,w1}
   -- x2=msg.markers[3].pose.pose.orientation.x
   -- y2=msg.markers[3].pose.pose.orientation.y
   -- z2=msg.markers[3].pose.pose.orientation.z
  --  w2=msg.markers[3].pose.pose.orientation.w
  --  aruco_2={x2,y2,z2,w2}
    
    -- Get the orientation(quaternion) of the ArUco marker and set the orientation of the hoop using Orientation_hoop dummy
    -- Hint : Go through the regular API - sim.setObjectQuaternion
    

end

function whycon_callback(msg)
    x1=msg.poses[1].position.x
    x1=x1/scale_factor[1]
    y1=msg.poses[1].position.y
    y1=y1/scale_factor[2]
    z1=msg.poses[1].position.z
    z1=(whycon_gnd-z1)/scale_factor[3]
    whycon_0={x1,y1,z1}
   -- x1=msg.poses[1].position.x
   -- y1=msg.poses[1].position.y
  --  z1=msg.poses[1].position.z
   -- whycon_1={x1,y1,z1}
   -- x2=msg.poses[2].position.x
   --y2=msg.poses[2].position.y
   -- z2=msg.poses[2].position.z
  --- whycon_2={x2,y2,z2}
   -- x3=msg.poses[3].position.x
    --y3=msg.poses[3].position.y
   -- z3=msg.poses[3].position.z
    --whycon_3={x3,y3,z3}
    -- Get the position of the whycon marker and set the position of the food tree and non-food tree using Position_hoop dummy
    -- Hint : Go through the regular API - sim.setObjectPosition
    
end

function key_callback(msg)
    -- Read key input to set or unset position and orientation of food and non-food trees
    inp_key=msg.data
   --print("WE are inside ")
    print(inp_key)
    if(inp_key==10)then
        print("i ")
        print(whycon_0)
        status1=sim.setObjectPosition(saltree_handle,-1,whycon_0)
    end
    if(inp_key==30)then
        print("j")
        print(whycon_0)
        status1=sim.setObjectPosition(mangotree_handle,-1,whycon_0)
    end
    if(inp_key==20)then
        print("k ")
        print(whycon_0)
        status1=sim.setObjectPosition(cashewtree_handle,-1,whycon_0)
    end
    if(inp_key==40)then
        print("l ")
        print(whycon_0)
        status1=sim.setObjectPosition(obstacle_handle,-1,whycon_0)
    end
    if(inp_key==50)then
        print("w")
        print(aruco_0)
        status2= sim.setObjectQuaternion(saltree_orient_handle,saltree_handle,aruco_0)
    end
    if(inp_key==60)then
        print("s")
        print(aruco_0)
        status2= sim.setObjectQuaternion(mangotree_handle,-1,aruco_0)
    end
    if(inp_key==70)then
        print("a")
        print(aruco_0)
        status2= sim.setObjectQuaternion(cashewtree_handle,-1,aruco_0)
    end
    
        

    --if (inp_key==110)then
   --     status1= sim.setObjectQuaternion(saltree_handle,-1,aruco_0)
    --    status2=sim.setObjectQuaternion(mangotree_handle,-1,aruco_1)
   --     status3=sim.setObjectQuaternion(cashewtree_handle,-1,aruco_2)
   -- end
  --  if(inp_key==120)then
    --    status1=sim.setObjectPosition(saltree_handle,-1,whycon_0)
     --   status2=sim.setObjectPosition(mangotree_handle,-1,whycon_1)
    --    status3=sim.setObjectPosition(cashewtree_handle,-1,whycon_2)
    --    status4=sim.setObjectPosition(obstacle_handle,-1,whycon_3)

    --end
end
    --[[
    This child script teaches you how to use OMPL plugin in V-REP for path planning.

    Steps :
     1. Get the required handles
     2. Creat task and statespace
     3. Set the start pose and goal pose at the time at which you want to compute path
     4. Compute path and publish it as message type geometry_msgs/PoseArray

    ]]

    function sysCall_init(self)

        -- Getting the handles of start, goal dummies and the collection
        drone_handle = sim.getObjectHandle('eDroneBase')
        collection_handles= sim.getCollectionHandle('Obstacles')
        vision_sensor_position = sim.getObjectPosition(sim.getObjectHandle('Vision_sensor'),-1)
        start_handle = sim.getObjectHandle('Start')
        goal_handle = sim.getObjectHandle('initial_waypoint')
        goal_handle_1 = sim.getObjectHandle('goal_1')
        goal_handle_2 = sim.getObjectHandle('goal_2')
        collection_handles= sim.getCollectionHandle('Obstacles')
        no_of_obstacles = 6
        obstacles_handles = {}
        for i=1,no_of_obstacles do
            table.insert(obstacles_handles,sim.getObjectHandle('obstacle_'..tostring(i)))
        end


        -- Creating task and setting statespace type, lower and upper bounds
        -- Choosing algorithm for path planning and selecting the target using which path planning is done against the collection
        t=simOMPL.createTask('t')
        ss={simOMPL.createStateSpace('6d',simOMPL.StateSpaceType.pose3d,start_handle,{-3,-3,0},{3,3,3},1)}
        simOMPL.setStateSpace(t,ss)
        simOMPL.setAlgorithm(t,simOMPL.Algorithm.RRTConnect)
        simOMPL.setCollisionPairs(t,{sim.getObjectHandle('eDrone_outer'),collection_handles})

        -- no of path points minimum required
        scale_factor = {-7.5,-7.551,18.4} -- Add the scale_factor you computed learned from the tutorial of whycon transformation
        whycon_gnd=55.250
        no_of_path_points_required = 50

        compute_path_flag = true

        -- To advertise the computed pathpoints under the topic /vrep/waypoints of message type geometry_msgs/PoseArray
        path_pub=simROS.advertise('/vrep/waypoints', 'geometry_msgs/PoseArray')
        whycon_sub = simROS.subscribe('/path/need', 'std_msgs/Int64', 'demand')

    end

    -- Function to get pose (position and orientation) of a handle in reference to another handle
    function getpose(handle,ref_handle)
        position = sim.getObjectPosition(handle,ref_handle)
        orientation = sim.getObjectQuaternion(handle,ref_handle)
        pose = {position[1],position[2],position[3],orientation[1],orientation[2],orientation[3],orientation[4]}
        return pose
    end

    function demand(step)
         input = step.data    
    end
    -- Function to visualize the computed path
    function visualizePath( path )
        if not _lineContainer then
            _lineContainer=sim.addDrawingObject(sim.drawing_lines,1,0,-1,99999,{0.2,0.2,1})
        end
        sim.addDrawingObjectItem(_lineContainer,nil)
        if path then
            local pc=#path/7
            for i=1,pc-1,1 do
                lineDat={path[(i-1)*7+1],path[(i-1)*7+2],path[(i-1)*7+3],path[i*7+1],path[i*7+2],path[i*7+3]}
                sim.addDrawingObjectItem(_lineContainer,lineDat)
            end
        end
    end


    -- Function to make the message so that we can publish the path
    function packdata(path)

        local sender = {header = {}, poses = {}}
        
        sender['header']={seq=123, stamp=simROS.getTime(), frame_id="drone"}
        sender['poses'] = {}

        for i=1,((no_of_path_points_required-1)*7)+1,7 do
            a = {x = 0, y = 0, w = 0, z = 0}
            b = {x = 0, y = 0, z = 0}
            pose = {position = b, orientation = a, }
            pose.position.x =(path[i]*scale_factor[1])
            print(pose.position.x)
            pose.position.y =(path[i+1]*scale_factor[2])
            print(pose.position.y)
            pose.position.z =(whycon_gnd-(path[i+2]*scale_factor[3]))
            print(pose.position.z)
            sender.poses[math.floor(i/7) + 1] = pose
        end
        return sender
    end

    function create_path(st_handle,gl_handle,task)
        starting_pose=getpose(st_handle,-1)

        ending_pose=getpose(gl_handle,-1)

        simOMPL.setStartState(t,starting_pose)

        simOMPL.setGoalState(t,{ending_pose[1],ending_pose[2],ending_pose[3],starting_pose[4],starting_pose[5],starting_pose[6],starting_pose[7]})

        status = compute_and_send_path(t)

        return status
    end 


    function compute_and_send_path(task)
        local r
        local path
        r,path=simOMPL.compute(t,10,-1,no_of_path_points_required)
        print(r, #path)
        if(r == true) then
            visualizePath(path)
            message = packdata(path)  
            simROS.publish(path_pub,message)
        end
        return r
    end

    function sysCall_sensing()
        -- put your sensing code here

    end

    function sysCall_actuation()
        -- put your actuation code here

        -- Computing path only once. 
            -- Computing path and publishing path points
            if(input == 1 )then
                status = create_path(start_handle,goal_handle,t)
                if(status == true) then -- path computed
                    print("1 st path perfectly calculated")
                end
            end 
    end

    function sysCall_cleanup()

    end



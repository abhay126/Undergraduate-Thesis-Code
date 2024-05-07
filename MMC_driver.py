from MMC_Library_Python.MMC_PyLibrary import *
import time

#TODO can add argparse so that is accessible from command line
#TODO can write a small help script to give information about common commands one may use

# List of commands

CMD_POSITION_STATUS = "POS"
CMD_MOVE_RELATIVE   = "MVR"
CMD_MOVE_ABSOLUTE   = "MVA"
CMD_STATUS_MSG      = "STA"

# Global values
theory_move_1nm    = -0.031056
encod_move_1nm     = 2 * theory_move_1nm

def query_position(axis : int = 1) -> tuple[float]:
    """
    (int) -> (tuple(float))

    Returns theoretical position and encoder position of the motor (specified by axis) when queried 
    and if the specific motor is connected

    @inputs
    axis (int) (optional): Integer value specifying the axis of rotation set for that motor,
                            default value is 1

    @return
    Tuple[float]: Float values in a tuple where index 0 represents theoretical position and 
                    index 1 represents encoder position. Returns None for both if the call failed
    """

    # Call provided query function though the motor driver
    message = pollValues(axis, CMD_POSITION_STATUS)

    # Check if the message retreival was successful
    if message:
        print(message)
        message = message.split(sep= ',')
        return float(message[0]), float(message[1])
    
    return (None, None)

def move_pos(zero_wl : float, target_wl : float, axis : int = 1) -> None:
    """
    (float, float, int) -> (None)

    Move the motor such that the centre wavelength is changed from what it is currently at 
    to target centre wavelength, given the centre wavelength at zero position.

    @inputs
    zero_wl (float): Centre wavelength at zero position of the motor
    target_wl (float): Target centre wavelength needed from the tunable filter
    axis (int) (optional): Integer value specifying the axis of rotation set for that motor,
                            default value is 1

    @return
    Tuple[float]: Float values in a tuple where index 0 represents theoretical position and 
                    index 1 represents encoder position. Returns None for both if the call failed
    """

    # Get current positions 
    curr_theory_pos, curr_encod_pos = query_position(axis= axis)
    if curr_theory_pos == None or curr_encod_pos == None:
        # TODO maybe a kill properly function
        print("ERROR")
        exit()
    
    time.sleep(3)


    curr_wl = zero_wl + curr_encod_pos/encod_move_1nm

    wl_shift = target_wl - curr_wl

    goal_theory_pos = float("{:0.6f}".format(wl_shift * theory_move_1nm)) 
    goal_encod_pos = float("{:0.6f}".format(wl_shift * encod_move_1nm))
    error = goal_encod_pos - curr_encod_pos

    if target_wl != zero_wl:
        cmd = CMD_MOVE_RELATIVE
    
    else:
        cmd = CMD_MOVE_ABSOLUTE

    

    while abs(error) > 0.001:
        curr_theory_pos, curr_encod_pos = query_position(axis= axis)
        if curr_theory_pos == None or curr_encod_pos == None:
            # TODO maybe a kill properly function
            print("ERROR")
            exit()
        
        time.sleep(3)
        print(curr_encod_pos)
        curr_wl = zero_wl + curr_encod_pos/encod_move_1nm
        wl_shift = target_wl - curr_wl
        print(curr_wl, target_wl)
        print(wl_shift)
        goal_theory_pos = float("{:0.6f}".format(wl_shift * theory_move_1nm))
        print(goal_theory_pos)
        error = goal_encod_pos - curr_encod_pos


def get_status(message : str) -> None:
    """
    """
    message = bin(int(message)).replace("0b", "").zfill(8)
                    
    #TODO Make the messages here more descriptive
    neg_switch = message[7]
    print("neg_switch", neg_switch)

    pos_switch = message[6]
    print("pos_switch", pos_switch)

    prog_running = message[5]
    print("prog_running", prog_running)

    stage_mov = message[4]
    print("stage_mov", stage_mov)

    decelerate = message[3]
    print("decelerate", decelerate)

    const_vel = message[2]
    print("const_vel", const_vel)

    accelerate = message[1]
    print("accelerate", accelerate)

    error = message[0]
    print("error", error)


if __name__=="__main__":
    # Find the port connected to MMC
    ports = serial.tools.list_ports.comports()
    port = None

    for port in ports:
        if port.serial_number == "MMC":
            break

    if (not port) or port.serial_number != "MMC":
        print("Tunable filter not connected")
        exit()

    # Run the loop for getting commands from the user
    # and writing them on the serial network
    while True:

        # Hard coding axis to be 1 :)
        user_input = input("Enter command following the directions from MMC manual: ")
        axis = 1

        if openComPortMMC(port.name):

            # Checking if the command is for reading or writing
            if user_input[-1] == '?':

                message = pollValues(axis, user_input[ :-1])
                
                if CMD_STATUS_MSG in user_input.upper():

                    get_status(message)

                else:

                    print(message)

            else:

                writeCommandToMMC(1, user_input)


            if not closeConnectionMMC():
                print("Port is not properly closed")
# TODO Central position is not exactly constant, how to deal with it


# For data storage and analysis
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import time
# import plotter

# For interacting with the tunable filter
from MMC_Library_Python.MMC_PyLibrary import *
from MMC_driver import *
import serial

# For interacting with Time-to-Digital Converter IDQ801
import IDQ_ID801.lib.hunahpy as IDQ

# Macros
START_WL    = 760
END_WL      = 860
ZERO_POS_WL = 800


def get_sample(filename : str) -> tuple[pd.DataFrame, float]:
    """
    (str) -> (tuple[pd.Dataframe, float])

    Collects timestamps from the IDQ-ID801 device and writes them into the file
    "filename". Returns a pandas dataframe after reading the file in which timestamps
    are stored as well as the time for which data was collected

    @inputs
    filename (str): Name of the file to write IQD timestamps in

    @return
    Tuple[pd.Dataframe, float]: A tuple containing a pd.Dataframe made from the collected data,
                                and the time taken to collect this data as the second element in the tuple.
                                Returns a tuple of None if filename is invalid.
    """

    # If filename is valid
    if filename:

        # Start timer and data collection
        delta_t = time.time()
        idq.writeTimestamps(filename, binary= False)

        # Collect data for 1s and then stop data collection as well as the timer
        time.sleep(1)
        idq.writeTimestamps(None)
        delta_t = time.time() - delta_t

        # return the collected data and time taken to collect it
        return pd.read_csv(filename, header= None), delta_t
    
    return (None, None)

if __name__=="__main__":

    # # Get centre wavelength for the filter (as it is shitty and changes regularly)
    # zero_centre_wl = input(">>>Enter the centre wavelength in nm after checking the tunable filter for correct calibration: ")
    # zero_centre_wl = float(zero_centre_wl)

    # Setting up tunable filter connections
    ports = serial.tools.list_ports.comports()
    port = None

    for port in ports:
        if port.serial_number == "MMC":
            break

    if (not port) or port.serial_number != "MMC":
        print("ERROR: Tunable filter not connected")
        exit()

    else:
        status = openComPortMMC(port.name)
        if status:
            print(">>>Tunable filter successfully connected")
        else:
            print("ERROR: Tunable filter unable to connect")
            exit()

    # Setting up TDC connections
    channel_num = 1
    idq = IDQ.TDC()

    # Setting up general variables to be used based on macros and input
    # starting_wl     = zero_centre_wl
    spectrum_range  = int(END_WL - START_WL)

    # Move to starting position for the tunable filter
    move_MMC(target_wl= START_WL)
    time.sleep(5)

    # # Making sure we are starting from 0 position
    # writeCommandToMMC(1, 'zro')

    ## Basic testing and debugging comments
    # time.sleep(10)
    # writeCommandToMMC(1, 'mvr' + "{:.5f}".format(start_pos * move_1nm))
    # time.sleep(10)

    # Dataframe setups
    count_df    = pd.DataFrame()

    # # Get Dark Counts
    # timestamps, period = get_sample('scan.csv')
    # events = list(timestamps.iloc[ : , 1])
    # num_events = events.count(channel_num)
    # dark_counts = num_events/period
    # print("Dark Count Rate = ", int(dark_counts))

    # input("Dark counts measured. Press any key to continue")

    # Starting the loop
    for i in range(spectrum_range + 1):

        print("======STEP {}======".format(i))

        expected_wl = str(START_WL + i)
        theoretical_pos, encoder_pos = query_position()
        time.sleep(3)

        # Collect timestamps from the TDC
        counts = 0
        scan_data = get_sample('scan.csv')
        if not scan_data:
            print("ERROR: Data collection error")
            break

        timestamps, period = scan_data
        timestamps = timestamps.loc[timestamps[1] == channel_num]
        counts = len(timestamps)
        if counts:
            row = {'Expected Wavelength' : expected_wl,
                   'Theoretical Position' : theoretical_pos,
                   'Enocder Position' : encoder_pos,
                   'Calculated Wavelength' : get_current_wl(encoder_pos= encoder_pos), 
                   'Event Counts' : counts,
                   'Time' : period,
                   'Count Rate' : counts / period
                   }
            print(row)
            count_df[i] = row
        
        # Move to the next position
        next_wl = float(expected_wl) + 1
        move_MMC(target_wl= next_wl)
        # move_pos(zero_wl= zero_centre_wl, target_wl= float(expected_wl) + 1)
        time.sleep(3)

    count_df = count_df.transpose()
    count_df.to_csv('data.csv')

    final_positions = query_position()
    if final_positions:
        print("Final Theoretical Position = {}\nFinal Encoder Position = {}".format(final_positions[0], final_positions[1]))

    # Make it go back to absolute zero
    # move_pos(zero_centre_wl, zero_centre_wl)
    writeCommandToMMC(1, 'mva0')

    time.sleep(5)
    resting_positions = query_position()
    if resting_positions:
        print("Resting Theoretical Position = {}\nResting Encoder Position = {}".format(resting_positions[0], resting_positions[1]))
    
    closeConnectionMMC()

    idq.close()

    # # Plot it
    # plt.figure()
    # x_axis = np.linspace(starting_wl, ending_wl - 1, 100)
    # plt.plot(x_axis, count_df.iloc[0])
    # plt.show()
    # plotter.generate_plot()

    


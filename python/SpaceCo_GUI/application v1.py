import os
import customtkinter as ctk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import mplcyberpunk
import threading
import time
from datetime import datetime as dt
import random
import board
import busio
import adafruit_ads1x15.ads1015 as ADS
from adafruit_ads1x15.analog_in import AnalogIn

'APPLICATION SETUP'
app = ctk.CTk() # Create the main window
app.title("SPACECO Systems Monitoring Application")
app.geometry("1920x1080")

# This make the app clickable so that when you click on elsewhere, the cursor will be hidden in entry box
app.bind("<1>", lambda event: event.widget.focus_set()) 

'TABVIEW SETUP'
tabview = ctk.CTkTabview(master=app) # Create the tabview
tabview.pack(expand=True, fill=ctk.BOTH, padx=10, pady=(0,10))

'GLOBAL STYLING'
ctk.set_appearance_mode("dark") # Set appearance mode to dark
plt.style.use("cyberpunk") # Set plot styling to cyberpunk
heading1 = ("Helvetica", 15, "bold") # These font settings are used in everywhere except plots.
text1 = ("Helvetica", 12, "normal")

'DATA SENSING'
# Constants
pi = 3.1415926536
hydraulic_bore_diameter = 1.5 #in
hydraulic_bore_area = (hydraulic_bore_diameter**2)*(pi/4) #in2
MPa_psi = 145.037738

adc_channels = []
def initalize_ADC():
    # Create the I2C bus
    i2c = busio.I2C(board.SCL, board.SDA)

    # Create the ADC object using the I2C bus
    ads_gain = 2/3
    ads = ADS.ADS1015(i2c,gain=ads_gain, address=0x48)
    
    # Create single-ended inputs 
    chan0 = AnalogIn(ads, ADS.P0)           # Hydraulic Pressure
    chan1 = AnalogIn(ads, ADS.p1)           # Main Chamber O2 Concentration
    chan2 = AnalogIn(ads, ADS.p2)           # Airlock O2 Concentration
    adc_channels = [chan0, chan1, chan2]
    return adc_channels

def get_data(): # FOR RASPBERRY PI!
    # Collect & Convert O2 Concentration Data:
    mcO2_Offset, alO2_Offset = 1                                           # 4-20mA signal turns into 1-5V signal
    mcO2_Gain , alO2_Gain= 100/4                                           # Current Gain returns % values
    main_chamber_o2_adcIn = adc_channels[1].voltage()
    airlock_o2_adcIn = adc_channels[2].voltage()
    main_chamber_o2 = (main_chamber_o2_adcIn - mcO2_Offset) * mcO2_Gain
    airlock_o2 = (airlock_o2_adcIn - alO2_Offset) * alO2_Gain
    
    # Collect & Convert Hydraulic Pressure Values
    hp_Offset = 1                                                          # Pres. Transducer gives 1-5V signal
    hp_Gain = 7500/4                                                       # Pres. Transducer has 7,500 Psi full-scale-range (i.e 5V = 7,500 Psi)
    hp_adcIn = adc_channels[0].voltage()
    hydraulic_pressure = (hp_adcIn - hp_Offset) * hp_Gain
    hydraulic_pressure_MPa = hydraulic_pressure / MPa_psi                  # Unused
    hydraulic_load = hydraulic_bore_area * hydraulic_pressure              # In lbs 
    
    # Return Dummy Values for now
    cell_load = 1
    uhv_pressure = 1
    uhv_voltage = 1
    uhv_current = 1
    system_data = [main_chamber_o2, airlock_o2, hydraulic_pressure, hydraulic_load, cell_load, uhv_pressure, uhv_voltage, uhv_current]
    return system_data

# def get_data(): # FOR SIMULATION! Random number generator function
#     main_chamber_o2 = round(random.uniform(100, 150), 2)
#     airlock_o2 = round(random.uniform(70, 90), 2)
#     hydraulic_pressure = round(random.uniform(3000, 4000), 2)
#     hydraulic_load = round(random.uniform(25000, 28000), 2) # Calculated from the hydraulic pressure, not sensed.
#     cell_load = round(random.uniform(25000, 28000), 2)
#     uhv_pressure = round(random.uniform(1e-7, 1e-6), 10)
#     uhv_voltage = round(random.uniform(5, 20), 1)
#     uhv_current = round(random.uniform(50, 100), 1)
#     system_data = [main_chamber_o2, airlock_o2, hydraulic_pressure, hydraulic_load, cell_load, uhv_pressure, uhv_voltage, uhv_current]
#     return system_data

'RECORDING'
experiments_path = "Experiments" 
if not os.path.exists(experiments_path): # Check if the directory exists
    os.makedirs(experiments_path) # If it doesn't exist, create it
    os.makedirs(os.path.join(experiments_path, "Experiment 1")) # Then create the first experiment folder in the "Experiments" folder
    
experiments_directory = [f for f in os.listdir(experiments_path) if os.path.isdir(os.path.join(experiments_path, f))] # Look for the directories in the Experiments folder

def record_data(system):    # This function is used to record the selected data, call this function from the toggle switches
    # Save as:
    # {Experiment #} - Glovebox.csv (1st Column: Date, 2nd Column: Time, 3rd Column: main_chamber_o2, 4th column: airlock_o2)
    # {Experiment #} - Hydraulics.csv (1st Column: Date, 2nd Column: Time, 3rd Column: hydraulic_pressure, 4th column: hydraulic_load, 5th column: cell_load)
    # {Experiment #} - UHV.csv (1st Column: Date, 2nd Column: Time, 3rd Column: uhv_pressure, 4th column: uhv_voltage, 5th column: uhv_current)
    if system == 'glovebox' and switch_record_glovebox_var.get() == 'on':
        glovebox_file_name = tab_glovebox_e_r9_c2.get() + " - Glovebox.txt"
        glovebox_path = os.path.join(experiments_path, tab_glovebox_e_r9_c2.get(), glovebox_file_name)
        with open(glovebox_path, 'a') as file:
            if os.stat(glovebox_path).st_size == 0:
                file.write("Date" + "," + "Time" + "," + "Main Chamber O2 (ppm)" + "," + "Airlock O2 (ppm)" + "\n")
            file.write(str(dt.now().strftime("%m/%d/%Y")) + "," + str(dt.now().strftime("%H:%M:%S")) + "," + str(get_data()[0]) + "," + str(get_data()[1]) + "\n")
            file.close()
    elif system == 'hydraulics' and switch_record_hydraulics_var.get() == 'on':
        hydraulics_file_name = tab_hydraulics_e_r15_c2.get() + " - Hydraulics.txt"
        hydraulics_path = os.path.join(experiments_path, tab_hydraulics_e_r15_c2.get(), hydraulics_file_name)
        with open(hydraulics_path, 'a') as file:
            if os.stat(hydraulics_path).st_size == 0:
                file.write("Date" + "," + "Time" + "," + "Hydraulic Pressure (psi)" + "," + "Hydraulic Load (lbs)" + "," + "Cell Load (lbs)" + "\n")
            file.write(str(dt.now().strftime("%m/%d/%Y")) + "," + str(dt.now().strftime("%H:%M:%S")) + "," + str(get_data()[2]) + "," + str(get_data()[3]) + "," + str(get_data()[4]) + "\n")
            file.close()
    elif system == 'uhv' and switch_record_uhv_var.get() == 'on':
        uhv_file_name = tab_uhv_e_r8_c2.get() + " - UHV.txt"
        uhv_path = os.path.join(experiments_path, tab_uhv_e_r8_c2.get(), uhv_file_name)
        with open(uhv_path, 'a') as file:
            if os.stat(uhv_path).st_size == 0:
                file.write("Date" + "," + "Time" + "," + "Ultimate Pressure (Torr)" + "," +  "Voltage (kV)" + "," + "Current (mA)" + "\n")
            file.write(str(dt.now().strftime("%m/%d/%Y")) + "," + str(dt.now().strftime("%H:%M:%S")) + "," + str(get_data()[5]) + "," + str(get_data()[6]) + "," + str(get_data()[7]) + "\n")
            file.close()
    else:
        None
    app.after(1000, record_data, system)

def deltatime_recording(switch_record_var, start_time, deltatime_recording_var): # This function is used to calculate the elapsed time for recording
    elapsed_time = ctk.StringVar()
    if not switch_record_var.get() == "off":
        elapsed_time = dt.now() - dt.strptime(start_time, "%m/%d/%Y %I:%M:%S %p")
        days = elapsed_time.days
        hours, remainder = divmod(elapsed_time.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        elapsed_time = "{:02}:{:02}:{:02}".format(hours, minutes, seconds)
        if days > 0:
            elapsed_time = "{} days, {}".format(days, elapsed_time)
        deltatime_recording_var.set(elapsed_time)
    app.after(1000, deltatime_recording, switch_record_var, start_time, deltatime_recording_var)

switch_record_glovebox_var = ctk.StringVar(value="off")
def switch_record_glovebox(): # This CTK toggle switch function is used to display start/end time and recording length for the Glovebox
    if switch_record_glovebox_var.get() == "on":
        glovebox_start_time = dt.now().strftime("%m/%d/%Y %I:%M:%S %p")
        deltatime_recording_glovebox_var = ctk.StringVar()
        deltatime_recording(switch_record_glovebox_var, glovebox_start_time, deltatime_recording_glovebox_var)
        tab_glovebox_e_r11_c2.configure(textvariable=deltatime_recording_glovebox_var, text_color='green')
        tab_glovebox_e_r12_c2.configure(text=glovebox_start_time)
        tab_glovebox_e_r13_c2.configure(text='')
        record_data('glovebox')
    else:
        glovebox_end_time = dt.now().strftime("%m/%d/%Y %I:%M:%S %p")
        tab_glovebox_e_r11_c2.configure(text_color='red')
        tab_glovebox_e_r13_c2.configure(text=glovebox_end_time)

switch_record_hydraulics_var = ctk.StringVar(value="off")
def switch_record_hydraulics(): # This CTK toggle switch function is used to display start/end time and recording length for the Hydraulics
    if switch_record_hydraulics_var.get() == "on":
        hydraulics_start_time = dt.now().strftime("%m/%d/%Y %I:%M:%S %p")
        deltatime_recording_hydraulics_var = ctk.StringVar()
        deltatime_recording(switch_record_hydraulics_var, hydraulics_start_time, deltatime_recording_hydraulics_var)
        tab_hydraulics_e_r17_c2.configure(textvariable=deltatime_recording_hydraulics_var, text_color='green')
        tab_hydraulics_e_r18_c2.configure(text=hydraulics_start_time)
        tab_hydraulics_e_r19_c2.configure(text='')
        record_data('hydraulics')
    else:
        hydraulics_end_time = dt.now().strftime("%m/%d/%Y %I:%M:%S %p")
        tab_hydraulics_e_r17_c2.configure(text_color='red')
        tab_hydraulics_e_r19_c2.configure(text=hydraulics_end_time)

switch_record_uhv_var = ctk.StringVar(value="off")
def switch_record_uhv(): # This CTK toggle switch function is used to display start/end time and recording length for the Ultra-High Vacuum
    if switch_record_uhv_var.get() == "on":
        uhv_start_time = dt.now().strftime("%m/%d/%Y %I:%M:%S %p")
        deltatime_recording_uhv_var = ctk.StringVar()
        deltatime_recording(switch_record_uhv_var, uhv_start_time, deltatime_recording_uhv_var)
        tab_uhv_e_r10_c2.configure(textvariable=deltatime_recording_uhv_var, text_color='green')
        tab_uhv_e_r11_c2.configure(text=uhv_start_time)
        tab_uhv_e_r12_c2.configure(text='')
        record_data('uhv')
    else:
        uhv_end_time = dt.now().strftime("%m/%d/%Y %I:%M:%S %p")
        tab_uhv_e_r10_c2.configure(text_color='red')
        tab_uhv_e_r12_c2.configure(text=uhv_end_time)

'PLOTTING'
def deltatime_plotting(start_time): # This function is used to calculate the elapsed time for plotting
    elapsed_time = dt.now() - dt.strptime(start_time, "%m/%d/%Y %I:%M:%S %p")
    days = elapsed_time.days
    hours, remainder = divmod(elapsed_time.seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    elapsed_time = "{:02}:{:02}:{:02}".format(hours, minutes, seconds)
    if days > 0:
        elapsed_time = "{} days, {}".format(days, elapsed_time)
    return elapsed_time

plot_glovebox_get_data = False
plot_glovebox_frequency = 1  # Default value
plot_glovebox_thread = False  # Flag to track if the plotting thread has been started
def slider_plot_glovebox(value): # This CTK Slider function controls the Glovebox Plotting
    global plot_glovebox_get_data, plot_glovebox_frequency, plot_glovebox_thread
    if value == 0:
        plot_glovebox_get_data = False
        x_data_glovebox.clear() # Clear the data arrays
        y_data_glovebox_main_chamber_o2.clear()
        y_data_glovebox_airlock_o2.clear()
    elif value == 1:
        plot_glovebox_get_data = False
    elif value == 2:
        plot_glovebox_get_data = True
        if not plot_glovebox_thread:
            threading.Thread(target=plot_glovebox, daemon=True).start()
            plot_glovebox_thread = True
        # Update frequency every time it starts/resumes in case it's changed
        plot_glovebox_frequency_str = tab_glovebox_e_r15_c2.get().split(" ")[0]
        plot_glovebox_frequency = int(plot_glovebox_frequency_str) if plot_glovebox_frequency_str.isdigit() else 1

fig_glovebox = plt.figure() # Glovebox Plot Figure
fig_glovebox.patch.set_facecolor('#242424')
gs_glovebox = fig_glovebox.add_gridspec(2,1)
ax1_glovebox = fig_glovebox.add_subplot(gs_glovebox[0, 0])
ax2_glovebox = fig_glovebox.add_subplot(gs_glovebox[1, 0])
fig_glovebox.subplots_adjust(left=0.05, bottom=0.07, right=0.95, top=0.93, wspace=0, hspace=0)
fig_glovebox.tight_layout()
ax1_glovebox.set_title('Main Chamber O2 Concentration', fontname="Helvetica", fontsize="15", fontweight="bold", y=1.01)
ax1_glovebox.set_ylabel('O2 Concentration (ppm)', fontname="Helvetica", fontsize="12", fontweight="normal")
ax2_glovebox.set_title('Airlock O2 Concentration', fontname="Helvetica", fontsize="15", fontweight="bold", y=1.01)
ax2_glovebox.set_xlabel('Time', fontname="Helvetica", fontsize="12", fontweight="normal")
ax2_glovebox.set_ylabel('O2 Concentration (ppm)', fontname="Helvetica", fontsize="12", fontweight="normal")
x_data_glovebox = []
y_data_glovebox_main_chamber_o2 = []
y_data_glovebox_airlock_o2 = []

def plot_glovebox(): # This function generates the plot for the Glovebox
    global plot_glovebox_frequency
    plot_glovebox_start_time = dt.now().strftime("%m/%d/%Y %I:%M:%S %p")
    while True:
        if plot_glovebox_get_data:
            x_data_glovebox.append(deltatime_plotting(plot_glovebox_start_time))
            y_data_glovebox_main_chamber_o2.append(get_data()[0])
            y_data_glovebox_airlock_o2.append(get_data()[1])
        ax1_glovebox.clear()
        ax2_glovebox.clear()
        ax1_glovebox.plot(x_data_glovebox, y_data_glovebox_main_chamber_o2, color='cyan')
        ax2_glovebox.plot(x_data_glovebox, y_data_glovebox_airlock_o2, color='cyan')
        ax1_glovebox.set_title('Main Chamber O2 Concentration', fontname="Helvetica", fontsize="15", fontweight="bold", y=1.01)
        ax1_glovebox.set_ylabel('O2 Concentration (ppm)', fontname="Helvetica", fontsize="12", fontweight="normal")
        ax1_glovebox.xaxis.set_major_locator(plt.MaxNLocator(8))
        ax2_glovebox.set_title('Airlock O2 Concentration', fontname="Helvetica", fontsize="15", fontweight="bold", y=1.01)
        ax2_glovebox.set_xlabel('Time', fontname="Helvetica", fontsize="12", fontweight="normal")
        ax2_glovebox.set_ylabel('O2 Concentration (ppm)', fontname="Helvetica", fontsize="12", fontweight="normal")
        ax2_glovebox.xaxis.set_major_locator(plt.MaxNLocator(8))
        mplcyberpunk.make_lines_glow(ax1_glovebox)
        mplcyberpunk.make_lines_glow(ax2_glovebox)
        canvas_glovebox.draw()
        time.sleep(plot_glovebox_frequency)

plot_hydraulics_get_data = False
plot_hydraulics_frequency = 1  # Default value
plot_hydraulics_thread = False  # Flag to track if the plotting thread has been started
def slider_plot_hydraulics(value): # This CTK Slider function controls the Hydraulics Plotting
    global plot_hydraulics_get_data, plot_hydraulics_frequency, plot_hydraulics_thread
    if value == 0:
        plot_hydraulics_get_data = False
        x_data_hydraulics.clear() # Clear the data arrays
        y_data_hydraulics_hydraulic_pressure.clear()
        y_data_hydraulics_hydraulic_load.clear()
        y_data_hydraulics_cell_load.clear()
    elif value == 1:
        plot_hydraulics_get_data = False
    elif value == 2:
        plot_hydraulics_get_data = True
        if not plot_hydraulics_thread:
            threading.Thread(target=plot_hydraulics, daemon=True).start()
            plot_hydraulics_thread = True
        # Update frequency every time it starts/resumes in case it's changed
        plot_hydraulics_frequency_str = tab_hydraulics_e_r21_c2.get().split(" ")[0]
        plot_hydraulics_frequency = int(plot_hydraulics_frequency_str) if plot_hydraulics_frequency_str.isdigit() else 1

fig_hydraulics = plt.figure() # Hydraulics Plot Figure
fig_hydraulics.patch.set_facecolor('#242424')
gs_hydraulics = fig_hydraulics.add_gridspec(2,1)
ax1_hydraulics = fig_hydraulics.add_subplot(gs_hydraulics[0, 0])
ax2_hydraulics = fig_hydraulics.add_subplot(gs_hydraulics[1, 0])
fig_hydraulics.subplots_adjust(left=0.05, bottom=0.07, right=0.95, top=0.93, wspace=0, hspace=0)
fig_hydraulics.tight_layout()
ax1_hydraulics.set_title('Hydraulic Pressure', fontname="Helvetica", fontsize="15", fontweight="bold", y=1.01)
ax1_hydraulics.set_ylabel('Pressure (psi)', fontname="Helvetica", fontsize="12", fontweight="normal")
ax2_hydraulics.set_title('Load', fontname="Helvetica", fontsize="15", fontweight="bold", y=1.01)
ax2_hydraulics.set_xlabel('Time', fontname="Helvetica", fontsize="12", fontweight="normal")
ax2_hydraulics.set_ylabel('Load (lbs)', fontname="Helvetica", fontsize="12", fontweight="normal")
ax2_hydraulics.legend(['Hydraulic Load', 'Cell Load'])
x_data_hydraulics = []
y_data_hydraulics_hydraulic_pressure = []
y_data_hydraulics_hydraulic_load = []
y_data_hydraulics_cell_load = []

def plot_hydraulics(): # This function generates the plot for the Hydraulics
    global plot_hydraulics_frequency
    plot_hydraulics_start_time = dt.now().strftime("%m/%d/%Y %I:%M:%S %p")
    while True:
        if plot_hydraulics_get_data:
            x_data_hydraulics.append(deltatime_plotting(plot_hydraulics_start_time))
            y_data_hydraulics_hydraulic_pressure.append(get_data()[2])
            y_data_hydraulics_hydraulic_load.append(get_data()[3])
            y_data_hydraulics_cell_load.append(get_data()[4])
        ax1_hydraulics.clear()
        ax2_hydraulics.clear()
        ax1_hydraulics.plot(x_data_hydraulics, y_data_hydraulics_hydraulic_pressure, color='cyan')
        ax2_hydraulics.plot(x_data_hydraulics, y_data_hydraulics_hydraulic_load, color='cyan')
        ax2_hydraulics.plot(x_data_hydraulics, y_data_hydraulics_cell_load, color='yellow')
        ax1_hydraulics.set_title('Hydraulic Pressure', fontname="Helvetica", fontsize="15", fontweight="bold", y=1.01)
        ax1_hydraulics.set_ylabel('Pressure (psi)', fontname="Helvetica", fontsize="12", fontweight="normal")
        ax1_hydraulics.xaxis.set_major_locator(plt.MaxNLocator(8))
        ax2_hydraulics.set_title('Load', fontname="Helvetica", fontsize="15", fontweight="bold", y=1.01)
        ax2_hydraulics.set_xlabel('Time', fontname="Helvetica", fontsize="12", fontweight="normal")
        ax2_hydraulics.set_ylabel('Load (lbs)', fontname="Helvetica", fontsize="12", fontweight="normal")
        ax2_hydraulics.xaxis.set_major_locator(plt.MaxNLocator(8))
        ax2_hydraulics.legend(['Hydraulic Load', 'Cell Load'], loc='upper right')
        mplcyberpunk.make_lines_glow(ax1_hydraulics)
        mplcyberpunk.make_lines_glow(ax2_hydraulics)
        canvas_hydraulics.draw()
        time.sleep(plot_hydraulics_frequency)

plot_uhv_get_data = False
plot_uhv_frequency = 1  # Default value
plot_uhv_thread = False  # Flag to track if the plotting thread has been started
def slider_plot_uhv(value): # This CTK Slider function controls the Ultra-High Vacuum Plotting
    global plot_uhv_get_data, plot_uhv_frequency, plot_uhv_thread
    if value == 0:
        plot_uhv_get_data = False
        x_data_uhv.clear() # Clear the data arrays
        y_data_uhv_pressure.clear()
        y_data_uhv_voltage.clear()
        y_data_uhv_current.clear()
    elif value == 1:
        plot_uhv_get_data = False
    elif value == 2:
        plot_uhv_get_data = True
        if not plot_uhv_thread:
            threading.Thread(target=plot_uhv, daemon=True).start()
            plot_uhv_thread = True
        # Update frequency every time it starts/resumes in case it's changed
        plot_uhv_frequency_str = tab_uhv_e_r14_c2.get().split(" ")[0]
        plot_uhv_frequency = int(plot_uhv_frequency_str) if plot_uhv_frequency_str.isdigit() else 1

fig_uhv = plt.figure() # Ultra-High Vacuum Plot Figure
fig_uhv.patch.set_facecolor('#242424')
gs_uhv = fig_uhv.add_gridspec(2,2)
ax1_uhv = fig_uhv.add_subplot(gs_uhv[0, :])
ax2_uhv = fig_uhv.add_subplot(gs_uhv[1, 0])
ax3_uhv = fig_uhv.add_subplot(gs_uhv[1, 1])
fig_uhv.subplots_adjust(left=0.05, bottom=0.07, right=0.95, top=0.93, wspace=0, hspace=0)
fig_uhv.tight_layout()
ax1_uhv.set_title('Ultimate Pressure', fontname="Helvetica", fontsize="15", fontweight="bold", y=1.01)
ax1_uhv.set_xlabel('Time', fontname="Helvetica", fontsize="12", fontweight="normal")
ax1_uhv.set_ylabel('Ultimate Pressure (Torr)', fontname="Helvetica", fontsize="12", fontweight="normal")
ax2_uhv.set_title('Voltage', fontname="Helvetica", fontsize="15", fontweight="bold", y=1.01)
ax2_uhv.set_xlabel('Time', fontname="Helvetica", fontsize="12", fontweight="normal")
ax2_uhv.set_ylabel('Voltage (kV)', fontname="Helvetica", fontsize="12", fontweight="normal")
ax3_uhv.set_title('Current', fontname="Helvetica", fontsize="15", fontweight="bold", y=1.01)
ax3_uhv.set_xlabel('Time', fontname="Helvetica", fontsize="12", fontweight="normal")
ax3_uhv.set_ylabel('Current (mA)', fontname="Helvetica", fontsize="12", fontweight="normal")
x_data_uhv = []
y_data_uhv_pressure = []
y_data_uhv_voltage = []
y_data_uhv_current = []

def plot_uhv(): # This function generates the plot for the Ultra-High Vacuum
    global plot_uhv_frequency
    plot_uhv_start_time = dt.now().strftime("%m/%d/%Y %I:%M:%S %p")
    while True:
        if plot_uhv_get_data:
            x_data_uhv.append(deltatime_plotting(plot_uhv_start_time))
            y_data_uhv_pressure.append(get_data()[5])
            y_data_uhv_voltage.append(get_data()[6])
            y_data_uhv_current.append(get_data()[7])
        ax1_uhv.clear()
        ax2_uhv.clear()
        ax3_uhv.clear()    
        ax1_uhv.plot(x_data_uhv, y_data_uhv_pressure, color='cyan')
        ax2_uhv.plot(x_data_uhv, y_data_uhv_voltage, color='cyan')
        ax3_uhv.plot(x_data_uhv, y_data_uhv_current, color='cyan')
        ax1_uhv.set_title('Ultimate Pressure', fontname="Helvetica", fontsize="15", fontweight="bold", y=1.01)
        ax1_uhv.set_xlabel('Time', fontname="Helvetica", fontsize="12", fontweight="normal")
        ax1_uhv.set_ylabel('Ultimate Pressure (Torr)', fontname="Helvetica", fontsize="12", fontweight="normal")
        ax1_uhv.xaxis.set_major_locator(plt.MaxNLocator(8))
        ax2_uhv.set_title('Voltage', fontname="Helvetica", fontsize="15", fontweight="bold", y=1.01)
        ax2_uhv.set_xlabel('Time', fontname="Helvetica", fontsize="12", fontweight="normal")
        ax2_uhv.set_ylabel('Voltage (kV)', fontname="Helvetica", fontsize="12", fontweight="normal")
        ax2_uhv.xaxis.set_major_locator(plt.MaxNLocator(4))
        ax3_uhv.set_title('Current', fontname="Helvetica", fontsize="15", fontweight="bold", y=1.01)
        ax3_uhv.set_xlabel('Time', fontname="Helvetica", fontsize="12", fontweight="normal")
        ax3_uhv.set_ylabel('Current (mA)', fontname="Helvetica", fontsize="12", fontweight="normal")
        ax3_uhv.xaxis.set_major_locator(plt.MaxNLocator(4))
        mplcyberpunk.make_lines_glow(ax1_uhv)
        mplcyberpunk.make_lines_glow(ax2_uhv)
        mplcyberpunk.make_lines_glow(ax3_uhv)
        canvas_uhv.draw()
        time.sleep(plot_uhv_frequency)

'ENTRY VALIDATION COMMAND FUNCTIONS'
# These functions make the CTK Entries ends with a unit that is not deletable 

def validate_sec(value): # Entry validation function for sec units
    return value.endswith(" sec")
vcmd_sec = app.register(validate_sec)

def validate_Torr(value): # Entry validation function for Torr units
    return value.endswith(" Torr")
vcmd_Torr = app.register(validate_Torr)

def validate_ppm(value): # Entry validation function for ppm units
    return value.endswith(" ppm")
vcmd_ppm = app.register(validate_ppm)

def validate_psi(value): # Entry validation function for psi units
    return value.endswith(" psi")
vcmd_psi = app.register(validate_psi)

def validate_lbs(value): # Entry validation function for lbs units
    return value.endswith(" lbs")
vcmd_lbs = app.register(validate_lbs)

def validate_MPa(value): # Entry validation function for MPa units
    return value.endswith(" MPa")
vcmd_MPa = app.register(validate_MPa)

def validate_percent(value): # Entry validation function for % units
    return value.endswith(" %")
vcmd_percent = app.register(validate_percent)

def validate_in(value): # Entry validation function for in units
    return value.endswith(" in")
vcmd_in = app.register(validate_in)

def validate_in2(value): # Entry validation function for in2 units
    return value.endswith(" in2")
vcmd_in2 = app.register(validate_in2)


'INFORMATION ABOUT THE GRID LAYOUT AND DESIGN'
# w: west frame / e: east frame / r#: row number / c# column number
# West frame is for Plotting, east frame is for Control Panel.
# Only use single frame level. Do not use frames inside of the frame! The design get messed up in that case.
# Instead of the sub frames, use .pack() function to place the widgets inside of the frame. 
# When the .pack() is used, there is no more rows or columns. Need to place each widget to a specific coordinates by relx and rely value.
# Although there is no rows and columns inside of the frames, still using r# and c# as naming to follow the order of the widgets.
# There is 0.04px rely space between each widget. If the new section to be started in the Control Panel, such as System Status, Record Status, or Plot Settings, leave 0.06 px rely space before. 
# Relx spacings are based on which side the widget sticks to. See sticky function. 
# Labels for titles stick to the west, relx = 0.03.
# Labels for variables, entry, switch, slider, optionmenu stick to the east. Labels: 0.97 relx, Entry (with units): -0.99 relx, Switch: 1 relx, Slider: 0.98 relx, Optionmenu: 0.97 relx.
# To insert any new widget that already been used in the applications, refer to the grid and design configuration of that widget. Ideally copy the settings and make the necessary changes for master, name, etc.)

'GLOVEBOX TAB'
# This section consists the grid layout and design of the Glovebox tab.
tab_glovebox = tabview.add("Glovebox")
tab_glovebox.grid_rowconfigure(0, weight=1)
tab_glovebox.grid_columnconfigure(0, weight=7)
tab_glovebox.grid_columnconfigure(1, weight=1)


tab_glovebox_w = ctk.CTkFrame(master=tab_glovebox, fg_color='#242424')
tab_glovebox_w.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")

canvas_glovebox = FigureCanvasTkAgg(fig_glovebox, master=tab_glovebox_w)
canvas_glovebox.get_tk_widget().pack(side=ctk.TOP, fill=ctk.BOTH, expand=True, pady=(10,0))

tab_glovebox_e = ctk.CTkFrame(master=tab_glovebox, fg_color='#242424')
tab_glovebox_e.grid(row=0, column=1, padx=5, pady=5, sticky="nsew")

tab_glovebox_e_r1 = ctk.CTkLabel(tab_glovebox_e, text='System Status', font=heading1)
tab_glovebox_e_r1.pack()
tab_glovebox_e_r1.place(relx=0.03, rely=0.03, anchor='w')

tab_glovebox_e_r2_c1 = ctk.CTkLabel(tab_glovebox_e, text='Main Chamber O2:', font=text1)
tab_glovebox_e_r2_c1.pack()
tab_glovebox_e_r2_c1.place(relx=0.03, rely=0.07, anchor='w')

tab_glovebox_e_r2_c2 = ctk.CTkLabel(tab_glovebox_e, text='', font=text1)
tab_glovebox_e_r2_c2.pack()
tab_glovebox_e_r2_c2.place(relx=0.97, rely=0.07, anchor='e')

tab_glovebox_e_r3_c1 = ctk.CTkLabel(tab_glovebox_e, text='Target Main Chamber O2:', font=text1)
tab_glovebox_e_r3_c1.pack()
tab_glovebox_e_r3_c1.place(relx=0.03, rely=0.11, anchor='w')

tab_glovebox_e_r3_c2 = ctk.CTkEntry(tab_glovebox_e, validate="key", validatecommand=(vcmd_ppm, "%P"), font=text1, justify='right', width=100, height=10, fg_color='#242424', border_width=0)
tab_glovebox_e_r3_c2.pack()
tab_glovebox_e_r3_c2.place(relx=0.99, rely=0.11, anchor='e')
tab_glovebox_e_r3_c2.insert(-1," ppm")

tab_glovebox_e_r4_c1 = ctk.CTkLabel(tab_glovebox_e, text='Main Chamber O2 Status:', font=text1)
tab_glovebox_e_r4_c1.pack()
tab_glovebox_e_r4_c1.place(relx=0.03, rely=0.15,anchor='w')

tab_glovebox_e_r4_c2 = ctk.CTkLabel(tab_glovebox_e, text='', font=text1)
tab_glovebox_e_r4_c2.pack()
tab_glovebox_e_r4_c2.place(relx=0.97, rely=0.15, anchor='e')

tab_glovebox_e_r5_c1 = ctk.CTkLabel(tab_glovebox_e, text='Airlock O2:', font=text1)
tab_glovebox_e_r5_c1.pack()
tab_glovebox_e_r5_c1.place(relx=0.03, rely=0.19, anchor='w')

tab_glovebox_e_r5_c2 = ctk.CTkLabel(tab_glovebox_e, text='', font=text1)
tab_glovebox_e_r5_c2.pack()
tab_glovebox_e_r5_c2.place(relx=0.97, rely=0.19, anchor='e')

tab_glovebox_e_r6_c1 = ctk.CTkLabel(tab_glovebox_e, text='Target Airlock O2:', font=text1)
tab_glovebox_e_r6_c1.pack()
tab_glovebox_e_r6_c1.place(relx=0.03, rely=0.23, anchor='w')

tab_glovebox_e_r6_c2 = ctk.CTkEntry(tab_glovebox_e, validate="key", validatecommand=(vcmd_ppm, "%P"), font=text1, justify='right', width=100, height=10, fg_color='#242424', border_width=0)
tab_glovebox_e_r6_c2.pack()
tab_glovebox_e_r6_c2.place(relx=0.99, rely=0.23, anchor='e')
tab_glovebox_e_r6_c2.insert(-1," ppm")

tab_glovebox_e_r7_c1 = ctk.CTkLabel(tab_glovebox_e, text='Airlock O2 Status:', font=text1)
tab_glovebox_e_r7_c1.pack()
tab_glovebox_e_r7_c1.place(relx=0.03, rely=0.27, anchor='w')

tab_glovebox_e_r7_c2 = ctk.CTkLabel(tab_glovebox_e, text='', font=text1)
tab_glovebox_e_r7_c2.pack()
tab_glovebox_e_r7_c2.place(relx=0.97, rely=0.27, anchor='e')

tab_glovebox_e_r8 = ctk.CTkLabel(tab_glovebox_e, text='Record Status', font=heading1)
tab_glovebox_e_r8.pack()
tab_glovebox_e_r8.place(relx=0.03, rely=0.33, anchor='w')

tab_glovebox_e_r9_c1 = ctk.CTkLabel(tab_glovebox_e, text='Record to:', font=text1)
tab_glovebox_e_r9_c1.pack()
tab_glovebox_e_r9_c1.place(relx=0.03, rely=0.37, anchor='w')

tab_glovebox_e_r9_c2 = ctk.CTkOptionMenu(tab_glovebox_e, values=experiments_directory, width=100, height=15, font=text1)
tab_glovebox_e_r9_c2.pack()
tab_glovebox_e_r9_c2.place(relx=0.97, rely=0.37, anchor='e')

tab_glovebox_e_r10_c1 = ctk.CTkLabel(tab_glovebox_e, text='End/Start Record:', font=text1)
tab_glovebox_e_r10_c1.pack()
tab_glovebox_e_r10_c1.place(relx=0.03, rely=0.41, anchor='w')

tab_glovebox_e_r10_c2 = ctk.CTkSwitch(tab_glovebox_e, text='', command=switch_record_glovebox, variable=switch_record_glovebox_var, onvalue="on", offvalue="off", switch_width=105, switch_height=15)
tab_glovebox_e_r10_c2.pack()
tab_glovebox_e_r10_c2.place(relx=1, rely=0.41, anchor='e')

tab_glovebox_e_r11_c1 = ctk.CTkLabel(tab_glovebox_e, text='Recording Length:', font=text1)
tab_glovebox_e_r11_c1.pack()
tab_glovebox_e_r11_c1.place(relx=0.03, rely=0.45, anchor='w')

tab_glovebox_e_r11_c2 = ctk.CTkLabel(tab_glovebox_e, text='', font=text1)
tab_glovebox_e_r11_c2.pack()
tab_glovebox_e_r11_c2.place(relx=0.97, rely=0.45, anchor='e')
tab_glovebox_e_r11_c2.configure(text="00:00:00")

tab_glovebox_e_r12_c1 = ctk.CTkLabel(tab_glovebox_e, text='Start Time:', font=text1)
tab_glovebox_e_r12_c1.pack()
tab_glovebox_e_r12_c1.place(relx=0.03, rely=0.49, anchor='w')

tab_glovebox_e_r12_c2 = ctk.CTkLabel(tab_glovebox_e, text='', font=text1)
tab_glovebox_e_r12_c2.pack()
tab_glovebox_e_r12_c2.place(relx=0.97, rely=0.49, anchor='e')

tab_glovebox_e_r13_c1 = ctk.CTkLabel(tab_glovebox_e, text='End Time:', font=text1)
tab_glovebox_e_r13_c1.pack()
tab_glovebox_e_r13_c1.place(relx=0.03, rely=0.53, anchor='w')

tab_glovebox_e_r13_c2 = ctk.CTkLabel(tab_glovebox_e, text='', font=text1)
tab_glovebox_e_r13_c2.pack()
tab_glovebox_e_r13_c2.place(relx=0.97, rely=0.53, anchor='e')

tab_glovebox_e_r14 = ctk.CTkLabel(tab_glovebox_e, text='Plot Settings', font=heading1)
tab_glovebox_e_r14.pack()
tab_glovebox_e_r14.place(relx=0.03, rely=0.59, anchor='w')

tab_glovebox_e_r15_c1 = ctk.CTkLabel(tab_glovebox_e, text='Plotting Frequency:', font=text1)
tab_glovebox_e_r15_c1.pack()
tab_glovebox_e_r15_c1.place(relx=0.03, rely=0.63, anchor='w')

tab_glovebox_e_r15_c2 = ctk.CTkEntry(tab_glovebox_e, validate="key", validatecommand=(vcmd_sec, "%P"), font=text1, justify='right', width=100, height=10, fg_color='#242424', border_width=0)
tab_glovebox_e_r15_c2.pack()
tab_glovebox_e_r15_c2.place(relx=0.99, rely=0.63, anchor='e')
tab_glovebox_e_r15_c2.insert(-1," sec")
tab_glovebox_e_r15_c2.insert(0,"1")

tab_glovebox_e_r16_c1 = ctk.CTkLabel(tab_glovebox_e, text='End/Pause/Start Plot:', font=text1)
tab_glovebox_e_r16_c1.pack()
tab_glovebox_e_r16_c1.place(relx=0.03, rely=0.67, anchor='w')

tab_glovebox_e_r16_c2 = ctk.CTkSlider(tab_glovebox_e, from_=0, to=2, command=slider_plot_glovebox, number_of_steps=2, width=105, height=15, border_width=3, button_color='white', button_hover_color='white', progress_color='#1f6aa5')
tab_glovebox_e_r16_c2.pack()
tab_glovebox_e_r16_c2.place(relx=0.98, rely=0.67, anchor='e')
tab_glovebox_e_r16_c2.set(0)

'HYDRAULICS TAB'
# This section consists the grid layout and design of the hydraulics tab.
tab_hydraulics = tabview.add("Hydraulics")
tab_hydraulics.grid_rowconfigure(0, weight=1)
tab_hydraulics.grid_columnconfigure(0, weight=7)
tab_hydraulics.grid_columnconfigure(1, weight=1)

tab_hydraulics_w = ctk.CTkFrame(master=tab_hydraulics, fg_color='#242424')
tab_hydraulics_w.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")

canvas_hydraulics = FigureCanvasTkAgg(fig_hydraulics, master=tab_hydraulics_w)
canvas_hydraulics.get_tk_widget().pack(side=ctk.TOP, fill=ctk.BOTH, expand=True, pady=(10,0))

tab_hydraulics_e = ctk.CTkFrame(master=tab_hydraulics, fg_color='#242424')
tab_hydraulics_e.grid(row=0, column=1, padx=5, pady=5, sticky="nsew")

tab_hydraulics_e_r1 = ctk.CTkLabel(tab_hydraulics_e, text='System Status', font=heading1)
tab_hydraulics_e_r1.pack()
tab_hydraulics_e_r1.place(relx=0.03, rely=0.03, anchor='w')

tab_hydraulics_e_r2_c1 = ctk.CTkLabel(tab_hydraulics_e, text='Hydraulic Pressure:', font=text1)
tab_hydraulics_e_r2_c1.pack()
tab_hydraulics_e_r2_c1.place(relx=0.03, rely=0.07, anchor='w')

tab_hydraulics_e_r2_c2 = ctk.CTkLabel(tab_hydraulics_e, text='', font=text1)
tab_hydraulics_e_r2_c2.pack()
tab_hydraulics_e_r2_c2.place(relx=0.97, rely=0.07, anchor='e')

tab_hydraulics_e_r3_c1 = ctk.CTkLabel(tab_hydraulics_e, text='Hydraulic Load:', font=text1)
tab_hydraulics_e_r3_c1.pack()
tab_hydraulics_e_r3_c1.place(relx=0.03, rely=0.11, anchor='w')

tab_hydraulics_e_r3_c2 = ctk.CTkLabel(tab_hydraulics_e, text='', font=text1)
tab_hydraulics_e_r3_c2.pack()
tab_hydraulics_e_r3_c2.place(relx=0.97, rely=0.11, anchor='e')

tab_hydraulics_e_r4_c1 = ctk.CTkLabel(tab_hydraulics_e, text='Cell Load:', font=text1)
tab_hydraulics_e_r4_c1.pack()
tab_hydraulics_e_r4_c1.place(relx=0.03, rely=0.15,anchor='w')

tab_hydraulics_e_r4_c2 = ctk.CTkLabel(tab_hydraulics_e, text='', font=text1)
tab_hydraulics_e_r4_c2.pack()
tab_hydraulics_e_r4_c2.place(relx=0.97, rely=0.15, anchor='e')

tab_hydraulics_e_r5_c1 = ctk.CTkLabel(tab_hydraulics_e, text='Load Percent Error:', font=text1)
tab_hydraulics_e_r5_c1.pack()
tab_hydraulics_e_r5_c1.place(relx=0.03, rely=0.19, anchor='w')

tab_hydraulics_e_r5_c2 = ctk.CTkLabel(tab_hydraulics_e, text='', font=text1)
tab_hydraulics_e_r5_c2.pack()
tab_hydraulics_e_r5_c2.place(relx=0.97, rely=0.19, anchor='e')

tab_hydraulics_e_r6_c1 = ctk.CTkLabel(tab_hydraulics_e, text='Sample Yield Strength:', font=text1)
tab_hydraulics_e_r6_c1.pack()
tab_hydraulics_e_r6_c1.place(relx=0.03, rely=0.23, anchor='w')

tab_hydraulics_e_r6_c2 = ctk.CTkEntry(tab_hydraulics_e, validate="key", validatecommand=(vcmd_MPa, "%P"), font=text1, justify='right', width=100, height=10, fg_color='#242424', border_width=0)
tab_hydraulics_e_r6_c2.pack()
tab_hydraulics_e_r6_c2.place(relx=0.99, rely=0.23, anchor='e')
tab_hydraulics_e_r6_c2.insert(-1," MPa")

tab_hydraulics_e_r7_c1 = ctk.CTkLabel(tab_hydraulics_e, text='Percent Yield Strength:', font=text1)
tab_hydraulics_e_r7_c1.pack()
tab_hydraulics_e_r7_c1.place(relx=0.03, rely=0.27, anchor='w')

tab_hydraulics_e_r7_c2 = ctk.CTkEntry(tab_hydraulics_e, validate="key", validatecommand=(vcmd_percent, "%P"), font=text1, justify='right', width=100, height=10, fg_color='#242424', border_width=0)
tab_hydraulics_e_r7_c2.pack()
tab_hydraulics_e_r7_c2.place(relx=0.99, rely=0.27, anchor='e')
tab_hydraulics_e_r7_c2.insert(-1," %")

tab_hydraulics_e_r8_c1 = ctk.CTkLabel(tab_hydraulics_e, text='Diffusion Area:', font=text1)
tab_hydraulics_e_r8_c1.pack()
tab_hydraulics_e_r8_c1.place(relx=0.03, rely=0.31, anchor='w')

tab_hydraulics_e_r8_c2 = ctk.CTkEntry(tab_hydraulics_e, validate="key", validatecommand=(vcmd_in2, "%P"), font=text1, justify='right', width=100, height=10, fg_color='#242424', border_width=0)
tab_hydraulics_e_r8_c2.pack()
tab_hydraulics_e_r8_c2.place(relx=0.99, rely=0.31, anchor='e')
tab_hydraulics_e_r8_c2.insert(-1," in2")

tab_hydraulics_e_r9_c1 = ctk.CTkLabel(tab_hydraulics_e, text='Target Offset:', font=text1)
tab_hydraulics_e_r9_c1.pack()
tab_hydraulics_e_r9_c1.place(relx=0.03, rely=0.35, anchor='w')

tab_hydraulics_e_r9_c2 = ctk.CTkEntry(tab_hydraulics_e, validate="key", validatecommand=(vcmd_percent, "%P"), font=text1, justify='right', width=100, height=10, fg_color='#242424', border_width=0)
tab_hydraulics_e_r9_c2.pack()
tab_hydraulics_e_r9_c2.place(relx=0.99, rely=0.35, anchor='e')
tab_hydraulics_e_r9_c2.insert(-1," %")

tab_hydraulics_e_r10_c1 = ctk.CTkLabel(tab_hydraulics_e, text='Target Hydraulic Pressure:', font=text1)
tab_hydraulics_e_r10_c1.pack()
tab_hydraulics_e_r10_c1.place(relx=0.03, rely=0.39, anchor='w')

tab_hydraulics_e_r10_c2 = ctk.CTkLabel(tab_hydraulics_e, text='', font=text1)
tab_hydraulics_e_r10_c2.pack()
tab_hydraulics_e_r10_c2.place(relx=0.97, rely=0.39, anchor='e')
tab_hydraulics_e_r10_c2.configure(text=" psi")

tab_hydraulics_e_r11_c1 = ctk.CTkLabel(tab_hydraulics_e, text='Hydraulic Pressure Status:', font=text1)
tab_hydraulics_e_r11_c1.pack()
tab_hydraulics_e_r11_c1.place(relx=0.03, rely=0.43, anchor='w')

tab_hydraulics_e_r11_c2 = ctk.CTkLabel(tab_hydraulics_e, text='', font=text1)
tab_hydraulics_e_r11_c2.pack()
tab_hydraulics_e_r11_c2.place(relx=0.97, rely=0.43, anchor='e')

tab_hydraulics_e_r12_c1 = ctk.CTkLabel(tab_hydraulics_e, text='Target Cell Load:', font=text1)
tab_hydraulics_e_r12_c1.pack()
tab_hydraulics_e_r12_c1.place(relx=0.03, rely=0.47, anchor='w')

tab_hydraulics_e_r12_c2 = ctk.CTkLabel(tab_hydraulics_e, text='', font=text1)
tab_hydraulics_e_r12_c2.pack()
tab_hydraulics_e_r12_c2.place(relx=0.97, rely=0.47, anchor='e')
tab_hydraulics_e_r12_c2.configure(text=" lbs")

tab_hydraulics_e_r13_c1 = ctk.CTkLabel(tab_hydraulics_e, text='Cell Load Status:', font=text1)
tab_hydraulics_e_r13_c1.pack()
tab_hydraulics_e_r13_c1.place(relx=0.03, rely=0.51, anchor='w')

tab_hydraulics_e_r13_c2 = ctk.CTkLabel(tab_hydraulics_e, text='', font=text1)
tab_hydraulics_e_r13_c2.pack()
tab_hydraulics_e_r13_c2.place(relx=0.97, rely=0.51, anchor='e')

tab_hydraulics_e_r14 = ctk.CTkLabel(tab_hydraulics_e, text='Record Status', font=heading1)
tab_hydraulics_e_r14.pack()
tab_hydraulics_e_r14.place(relx=0.03, rely=0.57, anchor='w')

tab_hydraulics_e_r15_c1 = ctk.CTkLabel(tab_hydraulics_e, text='Record to:', font=text1)
tab_hydraulics_e_r15_c1.pack()
tab_hydraulics_e_r15_c1.place(relx=0.03, rely=0.61, anchor='w')

tab_hydraulics_e_r15_c2 = ctk.CTkOptionMenu(tab_hydraulics_e, values=experiments_directory, width=100, height=15, font=text1)
tab_hydraulics_e_r15_c2.pack()
tab_hydraulics_e_r15_c2.place(relx=0.97, rely=0.61, anchor='e')

tab_hydraulics_e_r16_c1 = ctk.CTkLabel(tab_hydraulics_e, text='End/Start Record:', font=text1)
tab_hydraulics_e_r16_c1.pack()
tab_hydraulics_e_r16_c1.place(relx=0.03, rely=0.65, anchor='w')

tab_hydraulics_e_r16_c2 = ctk.CTkSwitch(tab_hydraulics_e, text='', command=switch_record_hydraulics, variable=switch_record_hydraulics_var, onvalue="on", offvalue="off", switch_width=105, switch_height=15)
tab_hydraulics_e_r16_c2.pack()
tab_hydraulics_e_r16_c2.place(relx=1, rely=0.65, anchor='e')

tab_hydraulics_e_r17_c1 = ctk.CTkLabel(tab_hydraulics_e, text='Recording Length:', font=text1)
tab_hydraulics_e_r17_c1.pack()
tab_hydraulics_e_r17_c1.place(relx=0.03, rely=0.69, anchor='w')

tab_hydraulics_e_r17_c2 = ctk.CTkLabel(tab_hydraulics_e, text='', font=text1)
tab_hydraulics_e_r17_c2.pack()
tab_hydraulics_e_r17_c2.place(relx=0.97, rely=0.69, anchor='e')
tab_hydraulics_e_r17_c2.configure(text="00:00:00")

tab_hydraulics_e_r18_c1 = ctk.CTkLabel(tab_hydraulics_e, text='Start Time:', font=text1)
tab_hydraulics_e_r18_c1.pack()
tab_hydraulics_e_r18_c1.place(relx=0.03, rely=0.73, anchor='w')

tab_hydraulics_e_r18_c2 = ctk.CTkLabel(tab_hydraulics_e, text='', font=text1)
tab_hydraulics_e_r18_c2.pack()
tab_hydraulics_e_r18_c2.place(relx=0.97, rely=0.73, anchor='e')

tab_hydraulics_e_r19_c1 = ctk.CTkLabel(tab_hydraulics_e, text='End Time:', font=text1)
tab_hydraulics_e_r19_c1.pack()
tab_hydraulics_e_r19_c1.place(relx=0.03, rely=0.77, anchor='w')

tab_hydraulics_e_r19_c2 = ctk.CTkLabel(tab_hydraulics_e, text='', font=text1)
tab_hydraulics_e_r19_c2.pack()
tab_hydraulics_e_r19_c2.place(relx=0.97, rely=0.77, anchor='e')

tab_hydraulics_e_r20 = ctk.CTkLabel(tab_hydraulics_e, text='Plot Settings', font=heading1)
tab_hydraulics_e_r20.pack()
tab_hydraulics_e_r20.place(relx=0.03, rely=0.83, anchor='w')

tab_hydraulics_e_r21_c1 = ctk.CTkLabel(tab_hydraulics_e, text='Plotting Frequency:', font=text1)
tab_hydraulics_e_r21_c1.pack()
tab_hydraulics_e_r21_c1.place(relx=0.03, rely=0.87, anchor='w')

tab_hydraulics_e_r21_c2 = ctk.CTkEntry(tab_hydraulics_e, validate="key", validatecommand=(vcmd_sec, "%P"), font=text1, justify='right', width=100, height=10, fg_color='#242424', border_width=0)
tab_hydraulics_e_r21_c2.pack()
tab_hydraulics_e_r21_c2.place(relx=0.99, rely=0.87, anchor='e')
tab_hydraulics_e_r21_c2.insert(-1," sec")
tab_hydraulics_e_r21_c2.insert(0,"1")

tab_hydraulics_e_r22_c1 = ctk.CTkLabel(tab_hydraulics_e, text='End/Pause/Start Plot:', font=text1)
tab_hydraulics_e_r22_c1.pack()
tab_hydraulics_e_r22_c1.place(relx=0.03, rely=0.91, anchor='w')

tab_hydraulics_e_r22_c2 = ctk.CTkSlider(tab_hydraulics_e, from_=0, to=2, command=slider_plot_hydraulics, number_of_steps=2, width=105, height=15, border_width=3, button_color='white', button_hover_color='white', progress_color='#1f6aa5')
tab_hydraulics_e_r22_c2.pack()
tab_hydraulics_e_r22_c2.place(relx=0.98, rely=0.91, anchor='e')
tab_hydraulics_e_r22_c2.set(0)

'ULTRA-HIGH VACUUM TAB'
# This section consists the grid layout and design of the Ultra-High Vacuum tab.
tab_uhv = tabview.add("Ultra-High Vacuum")
tab_uhv.grid_rowconfigure(0, weight=1)
tab_uhv.grid_columnconfigure(0, weight=7)
tab_uhv.grid_columnconfigure(1, weight=1)

tab_uhv_w = ctk.CTkFrame(master=tab_uhv, fg_color='#242424')
tab_uhv_w.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")

canvas_uhv = FigureCanvasTkAgg(fig_uhv, master=tab_uhv_w)
canvas_uhv.get_tk_widget().pack(side=ctk.TOP, fill=ctk.BOTH, expand=True, pady=(10,0))

tab_uhv_e = ctk.CTkFrame(master=tab_uhv, fg_color='#242424')
tab_uhv_e.grid(row=0, column=1, padx=5, pady=5, sticky="nsew")

tab_uhv_e_r1 = ctk.CTkLabel(tab_uhv_e, text='System Status', font=heading1)
tab_uhv_e_r1.pack()
tab_uhv_e_r1.place(relx=0.03, rely=0.03, anchor='w')

tab_uhv_e_r2_c1 = ctk.CTkLabel(tab_uhv_e, text='Ultimate Pressure:', font=text1)
tab_uhv_e_r2_c1.pack()
tab_uhv_e_r2_c1.place(relx=0.03, rely=0.07, anchor='w')

tab_uhv_e_r2_c2 = ctk.CTkLabel(tab_uhv_e, text='', font=text1)
tab_uhv_e_r2_c2.pack()
tab_uhv_e_r2_c2.place(relx=0.97, rely=0.07, anchor='e')

tab_uhv_e_r3_c1 = ctk.CTkLabel(tab_uhv_e, text='Target Pressure:', font=text1)
tab_uhv_e_r3_c1.pack()
tab_uhv_e_r3_c1.place(relx=0.03, rely=0.11, anchor='w')

tab_uhv_e_r3_c2 = ctk.CTkEntry(tab_uhv_e, validate="key", validatecommand=(vcmd_Torr, "%P"), font=text1, justify='right', width=100, height=10, fg_color='#242424', border_width=0)
tab_uhv_e_r3_c2.pack()
tab_uhv_e_r3_c2.place(relx=0.99, rely=0.11, anchor='e')
tab_uhv_e_r3_c2.insert(-1," Torr")

tab_uhv_e_r4_c1 = ctk.CTkLabel(tab_uhv_e, text='Pressure Status:', font=text1)
tab_uhv_e_r4_c1.pack()
tab_uhv_e_r4_c1.place(relx=0.03, rely=0.15,anchor='w')

tab_uhv_e_r4_c2 = ctk.CTkLabel(tab_uhv_e, text='', font=text1)
tab_uhv_e_r4_c2.pack()
tab_uhv_e_r4_c2.place(relx=0.97, rely=0.15, anchor='e')

tab_uhv_e_r5_c1 = ctk.CTkLabel(tab_uhv_e, text='Voltage:', font=text1)
tab_uhv_e_r5_c1.pack()
tab_uhv_e_r5_c1.place(relx=0.03, rely=0.19, anchor='w')

tab_uhv_e_r5_c2 = ctk.CTkLabel(tab_uhv_e, text='', font=text1)
tab_uhv_e_r5_c2.pack()
tab_uhv_e_r5_c2.place(relx=0.97, rely=0.19, anchor='e')

tab_uhv_e_r6_c1 = ctk.CTkLabel(tab_uhv_e, text='Current:', font=text1)
tab_uhv_e_r6_c1.pack()
tab_uhv_e_r6_c1.place(relx=0.03, rely=0.23, anchor='w')

tab_uhv_e_r6_c2 = ctk.CTkLabel(tab_uhv_e, text='', font=text1)
tab_uhv_e_r6_c2.pack()
tab_uhv_e_r6_c2.place(relx=0.97, rely=0.23, anchor='e')

tab_uhv_e_r7 = ctk.CTkLabel(tab_uhv_e, text='Record Status', font=heading1)
tab_uhv_e_r7.pack()
tab_uhv_e_r7.place(relx=0.03, rely=0.29, anchor='w')

tab_uhv_e_r8_c1 = ctk.CTkLabel(tab_uhv_e, text='Record to:', font=text1)
tab_uhv_e_r8_c1.pack()
tab_uhv_e_r8_c1.place(relx=0.03, rely=0.33, anchor='w')

tab_uhv_e_r8_c2 = ctk.CTkOptionMenu(tab_uhv_e, values=experiments_directory, width=100, height=15, font=text1)
tab_uhv_e_r8_c2.pack()
tab_uhv_e_r8_c2.place(relx=0.97, rely=0.33, anchor='e')

tab_uhv_e_r9_c1 = ctk.CTkLabel(tab_uhv_e, text='End/Start Record:', font=text1)
tab_uhv_e_r9_c1.pack()
tab_uhv_e_r9_c1.place(relx=0.03, rely=0.37, anchor='w')

tab_uhv_e_r9_c2 = ctk.CTkSwitch(tab_uhv_e, text='', command=switch_record_uhv, variable=switch_record_uhv_var, onvalue="on", offvalue="off", switch_width=105, switch_height=15)
tab_uhv_e_r9_c2.pack()
tab_uhv_e_r9_c2.place(relx=1, rely=0.37, anchor='e')

tab_uhv_e_r10_c1 = ctk.CTkLabel(tab_uhv_e, text='Recording Length:', font=text1)
tab_uhv_e_r10_c1.pack()
tab_uhv_e_r10_c1.place(relx=0.03, rely=0.41, anchor='w')

tab_uhv_e_r10_c2 = ctk.CTkLabel(tab_uhv_e, text='', font=text1)
tab_uhv_e_r10_c2.pack()
tab_uhv_e_r10_c2.place(relx=0.97, rely=0.41, anchor='e')
tab_uhv_e_r10_c2.configure(text="00:00:00")

tab_uhv_e_r11_c1 = ctk.CTkLabel(tab_uhv_e, text='Start Time:', font=text1)
tab_uhv_e_r11_c1.pack()
tab_uhv_e_r11_c1.place(relx=0.03, rely=0.45, anchor='w')

tab_uhv_e_r11_c2 = ctk.CTkLabel(tab_uhv_e, text='', font=text1)
tab_uhv_e_r11_c2.pack()
tab_uhv_e_r11_c2.place(relx=0.97, rely=0.45, anchor='e')

tab_uhv_e_r12_c1 = ctk.CTkLabel(tab_uhv_e, text='End Time:', font=text1)
tab_uhv_e_r12_c1.pack()
tab_uhv_e_r12_c1.place(relx=0.03, rely=0.49, anchor='w')

tab_uhv_e_r12_c2 = ctk.CTkLabel(tab_uhv_e, text='', font=text1)
tab_uhv_e_r12_c2.pack()
tab_uhv_e_r12_c2.place(relx=0.97, rely=0.49, anchor='e')

tab_uhv_e_r13 = ctk.CTkLabel(tab_uhv_e, text='Plot Settings', font=heading1)
tab_uhv_e_r13.pack()
tab_uhv_e_r13.place(relx=0.03, rely=0.55, anchor='w')

tab_uhv_e_r14_c1 = ctk.CTkLabel(tab_uhv_e, text='Plotting Frequency:', font=text1)
tab_uhv_e_r14_c1.pack()
tab_uhv_e_r14_c1.place(relx=0.03, rely=0.59, anchor='w')

tab_uhv_e_r14_c2 = ctk.CTkEntry(tab_uhv_e, validate="key", validatecommand=(vcmd_sec, "%P"), font=text1, justify='right', width=100, height=10, fg_color='#242424', border_width=0)
tab_uhv_e_r14_c2.pack()
tab_uhv_e_r14_c2.place(relx=0.99, rely=0.59, anchor='e')
tab_uhv_e_r14_c2.insert(-1," sec")
tab_uhv_e_r14_c2.insert(0,"1")

tab_uhv_e_r15_c1 = ctk.CTkLabel(tab_uhv_e, text='End/Pause/Start Plotting:', font=text1)
tab_uhv_e_r15_c1.pack()
tab_uhv_e_r15_c1.place(relx=0.03, rely=0.63, anchor='w')

tab_uhv_e_r15_c2 = ctk.CTkSlider(tab_uhv_e, from_=0, to=2, command=slider_plot_uhv, number_of_steps=2, width=105, height=15, border_width=3, button_color='white', button_hover_color='white', progress_color='#1f6aa5')
tab_uhv_e_r15_c2.pack()
tab_uhv_e_r15_c2.place(relx=0.98, rely=0.63, anchor='e')
tab_uhv_e_r15_c2.set(0)


'DISPLAYING SYSTEM STATUS'
def display_system_status():
    # Displays real-time values
    # Checks if targets are achieved or not
    # GLOVEBOX: For glovebox sensors, real-time values must be lower than the target to be true.
    # ULTRA-HIGH VACUUM: For ultra-high vacuum ultimate pressure, real-time value must be lower than the target to be true.
    # HYDRAULICS: Calculates the target for the hydraulics pressure and cell load based on inputs. See the comments regarding the hydraulics targets below.
    # If the target offset is NOT zero, it outputs a low and high target range based on the target offset. Real-time values must be between the low and high target to be true.
    # If the target offset is zero, it outputs the target directly. Real time values must be higher than the target to be true. 
    
    while True:
        main_chamber_o2, airlock_o2, hydraulic_pressure, hydraulic_load, cell_load, uhv_pressure, uhv_voltage, uhv_current = get_data()

        # GLOVEBOX
        tab_glovebox_e_r2_c2.configure(text=f"{main_chamber_o2:.2f} ppm")
        target_main_chamber_o2_str = tab_glovebox_e_r3_c2.get().split(" ")[0]
        if target_main_chamber_o2_str.strip():  # Check if the string is not empty
            try:
                target_main_chamber_o2 = float(target_main_chamber_o2_str)
                if main_chamber_o2 <= target_main_chamber_o2:
                    tab_glovebox_e_r4_c2.configure(text="Target Achieved", text_color='green')
                else:
                    tab_glovebox_e_r4_c2.configure(text="Not Achieved", text_color='red')
            except ValueError:
                tab_glovebox_e_r4_c2.configure(text="Invalid Target", text_color='red')
        else:
            tab_glovebox_e_r4_c2.configure(text="Target Not Set", text_color='yellow')

        tab_glovebox_e_r5_c2.configure(text=f"{airlock_o2:.2f} ppm")
        target_airlock_o2_str = tab_glovebox_e_r6_c2.get().split(" ")[0]
        if target_airlock_o2_str.strip():  # Check if the string is not empty
            try:
                target_airlock_o2 = float(target_airlock_o2_str)
                if airlock_o2 <= target_airlock_o2:
                    tab_glovebox_e_r7_c2.configure(text="Target Achieved", text_color='green')
                else:
                    tab_glovebox_e_r7_c2.configure(text="Not Achieved", text_color='red')
            except ValueError:
                tab_glovebox_e_r7_c2.configure(text="Invalid Target", text_color='red')
        else:
            tab_glovebox_e_r7_c2.configure(text="Target Not Set", text_color='yellow')

        # HYDRAULICS
        tab_hydraulics_e_r2_c2.configure(text=f"{hydraulic_pressure:.2f} psi")
        tab_hydraulics_e_r3_c2.configure(text=f"{hydraulic_load:.2f} lbs")
        tab_hydraulics_e_r4_c2.configure(text=f"{cell_load:.2f} lbs")
        
        load_percent_error = abs(100*(hydraulic_load-cell_load)/cell_load)
        tab_hydraulics_e_r5_c2.configure(text=f"{load_percent_error:.2f} %")
        
        sample_yield_strength_str = tab_hydraulics_e_r6_c2.get().split(" ")[0]
        percent_yield_strength_str = tab_hydraulics_e_r7_c2.get().split(" ")[0]
        diffusion_area_str = tab_hydraulics_e_r8_c2.get().split(" ")[0]
        target_offset_str = tab_hydraulics_e_r9_c2.get().split(" ")[0]
        
        if (sample_yield_strength_str.strip() and percent_yield_strength_str.strip() and diffusion_area_str.strip() and target_offset_str):  # Check if the string is not empty
            try:
                sample_yield_strength = float(sample_yield_strength_str)
                percent_yield_strength = float(percent_yield_strength_str)
                diffusion_area = float(diffusion_area_str)
                target_offset = float(target_offset_str)
                
                target_hydraulic_pressure = ((sample_yield_strength*percent_yield_strength/100)*MPa_psi*diffusion_area)/hydraulic_bore_area
                target_hydraulic_pressure_low = target_hydraulic_pressure-target_hydraulic_pressure*target_offset/100
                target_hydraulic_pressure_high = target_hydraulic_pressure+target_hydraulic_pressure*target_offset/100
                target_hydraulic_pressure = round(target_hydraulic_pressure)
                target_hydraulic_pressure_low = round(target_hydraulic_pressure_low)
                target_hydraulic_pressure_high = round(target_hydraulic_pressure_high)
    
                target_cell_load = (sample_yield_strength*percent_yield_strength/100)*MPa_psi*diffusion_area
                target_cell_load_low = target_cell_load-target_cell_load*target_offset/100
                target_cell_load_high = target_cell_load+target_cell_load*target_offset/100
                target_cell_load = round(target_cell_load)
                target_cell_load_low = round(target_cell_load_low)
                target_cell_load_high = round(target_cell_load_high)
                
                if target_offset != 0:
                    tab_hydraulics_e_r10_c2.configure(text=f"{target_hydraulic_pressure_low}-{target_hydraulic_pressure_high} psi")
                    tab_hydraulics_e_r12_c2.configure(text=f"{target_cell_load_low}-{target_cell_load_high} lbs")
                    if target_hydraulic_pressure_low < hydraulic_pressure < target_hydraulic_pressure_high:
                        tab_hydraulics_e_r11_c2.configure(text="Target Achieved", text_color='green')
                    else:
                        tab_hydraulics_e_r11_c2.configure(text="Not Achieved", text_color='red')
                    if target_cell_load_low < cell_load < target_cell_load_high:
                        tab_hydraulics_e_r13_c2.configure(text="Target Achieved", text_color='green')
                    else:
                        tab_hydraulics_e_r13_c2.configure(text="Not Achieved", text_color='red')
                else:
                    tab_hydraulics_e_r10_c2.configure(text=f"{target_hydraulic_pressure} psi")
                    tab_hydraulics_e_r12_c2.configure(text=f"{target_cell_load} lbs")
                    if target_hydraulic_pressure < hydraulic_pressure:
                        tab_hydraulics_e_r11_c2.configure(text="Target Achieved", text_color='green')
                    else:
                        tab_hydraulics_e_r11_c2.configure(text="Not Achieved", text_color='red')
                    if target_cell_load_low < cell_load:
                        tab_hydraulics_e_r13_c2.configure(text="Target Achieved", text_color='green')
                    else:
                        tab_hydraulics_e_r13_c2.configure(text="Not Achieved", text_color='red')
            except ValueError:
                tab_hydraulics_e_r11_c2.configure(text="Invalid Target", text_color='red')
                tab_hydraulics_e_r13_c2.configure(text="Invalid Target", text_color='red')
        else:
            tab_hydraulics_e_r11_c2.configure(text="Target Not Set", text_color='yellow')
            tab_hydraulics_e_r13_c2.configure(text="Target Not Set", text_color='yellow')

        # ULTRA-HIGH VACUUM
        tab_uhv_e_r2_c2.configure(text=f"{uhv_pressure} Torr")
        target_uhv_pressure_str = tab_uhv_e_r3_c2.get().split(" ")[0]
        if target_uhv_pressure_str.strip():  # Check if the string is not empty
            try:
                if uhv_pressure <= float(target_uhv_pressure_str):
                    tab_uhv_e_r4_c2.configure(text="Target Achieved", text_color='green')
                else:
                    tab_uhv_e_r4_c2.configure(text="Not Achieved", text_color='red')
            except ValueError:
                tab_uhv_e_r4_c2.configure(text="Invalid Target", text_color='red')
        else:
            tab_uhv_e_r4_c2.configure(text="Target Not Set", text_color='yellow')
        tab_uhv_e_r5_c2.configure(text=f"{uhv_voltage:.2f} kV")
        tab_uhv_e_r6_c2.configure(text=f"{uhv_current:.2f} mA")
        time.sleep(1)

thread_display_system_status = threading.Thread(target=display_system_status, daemon=True)
thread_display_system_status.start()

'RUN AND EXIT APPLICATION'
def run_application():   
    app.mainloop()

def exit_application():
    app.quit()
    
app.protocol("WM_DELETE_WINDOW", exit_application)

run_application()
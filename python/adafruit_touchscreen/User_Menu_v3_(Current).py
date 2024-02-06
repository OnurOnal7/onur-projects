# SPACECO Raspberry Pi based Data-Logger & Controller
# Created 10/22/2023, incorperates code by:
# Onur Onal, Kemal Yavuz, Callahan Bauman, Mehmet Sefer, and Mitchell Strobbe


import digitalio
import board
import RPi.GPIO as GPIO
import threading
import time as tm
import busio
import socket as sk
import os
from PIL import Image, ImageDraw, ImageFont
from adafruit_rgb_display import ili9341
import adafruit_ads1x15.ads1015 as ADS
from adafruit_ads1x15.analog_in import AnalogIn

#Encoder Pins
Enc_A = 26 
Enc_B = 25
Enc_SW = 27

Rotary_counter = 0
Current_A = 1
Current_B = 1
Switch_State = 0

LockRotary = threading.Lock()  #Locks Rotary Switch so that
#two functions do not try to modify it at the same time

#Display Objects & Vars ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
BORDER = 10
FONTSIZE = 24
BAUDRATE = 24000000

#Configure display_SPI pins
CS = digitalio.DigitalInOut(board.CE0)
DC = digitalio.DigitalInOut(board.CE1)

#Initalize SPI & Screen
spi1 = board.SPI()
disp1 = ili9341.ILI9341(spi1, rotation=90, cs=CS, dc=DC, baudrate=BAUDRATE)

#Initalize I2C & ADC
i2c = busio.I2C(board.SCL, board.SDA)
ads = ADS.ADS1015(i2c,gain=1, address=0x49)
dat_list = [35,0,0,0]
graphing_array =[]




if disp1.rotation % 180 == 90:
    disp_height = disp1.width  # we swap height/width to rotate it to landscape!
    disp_width = disp1.height 
else:
    disp_width = disp1.width  # we swap height/width to rotate it to landscape!
    disp_height = disp1.height

#End Display Config ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

#Rotary Encoder, Button, and Display Setup
def init_Rotary():
    # Sets Up the GPIO Pins for the Rotary Encoder
    GPIO.setwarnings(True)
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(Enc_A, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(Enc_B, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(Enc_SW, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.add_event_detect(Enc_A, GPIO.RISING, callback=rotary_interrupt)
    GPIO.add_event_detect(Enc_B, GPIO.RISING, callback=rotary_interrupt) 
    GPIO.add_event_detect(Enc_SW, GPIO.FALLING, callback=switch_interrupt)
    return

def rotary_interrupt(A_or_B):
    #Gets called when rotary encoder is turned -either direction-
    global Rotary_counter, Current_A, Current_B, LockRotary
    
    #Read the encoder pins
    Switch_A = GPIO.input(Enc_A)
    Switch_B = GPIO.input(Enc_B)
    
    #Check for bouncing
    if Current_A == Switch_A and Current_B == Switch_B:
        #if the pins are the same value as before
        #then it was switch bouncing, not rotation
        return
    
    #Update current Pin Values
    Current_A = Switch_A
    Current_B = Switch_B
    
    #Update "Rotary_counter" with detents moved (+nums -> CW ; -nums -> CCW)
    if(Switch_A and Switch_B):
        LockRotary.acquire()
        if(A_or_B == Enc_B):
            Rotary_counter += 1
        else:
            Rotary_counter -= 1
        LockRotary.release()
    return

def switch_interrupt(A):
    global Switch_State, LockRotary
    print("detected")
    
    #Read the switch pin
    Switch_SW = GPIO.input(Enc_SW)
    
    #Check for bouncing
    if Switch_State == 1 and Switch_SW == 1 :
        return
    
    #Update Switch_State to 1 to indicate that 
    #the switch has been pressed
    LockRotary.acquire()
    Switch_State = 1
    LockRotary.release()
    
    
    
    return
    
def init_Display():
    global disp1, FONTSIZE

    # Create Display Image
    image1 = Image.new("RGB", (disp_width, disp_height))

    # Get drawing object to draw on image.
    draw1 = ImageDraw.Draw(image1)

    # Draw a green filled box as the background
    draw1.rectangle((0, 0, disp_width, disp_height), fill=(255, 85, 0))
    disp1.image(image1)

    # Draw a smaller inner black rectangle
    draw1.rectangle(
        (BORDER, BORDER, disp_width - BORDER - 1, disp_height - BORDER - 1), fill=(0, 0, 0)
    )

    # Load a TTF Font
    font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", FONTSIZE)

    # Draw Some Text
    text1 = "SPACECO"
    bbox = font.getbbox(text1)

    font_width = bbox[2] - bbox[0]
    font_height = bbox[3] - bbox[1]

    center_x = (disp_width - font_width) // 2
    center_y = (disp_height - font_height) // 2

    draw1.text(
        (center_x, center_y),
        text1,
        font=font,
        fill=(255, 255, 255)
    )
    
    #Draw image
    disp1.image(image1)
    return

#Data Aquisition Functions
def pullADCvalues():
    global ads, dat_list, graphing_array
    # Configure offset and Gain Values:
    # 12-bit goes from 0-4095 with offset of 819, i.e. 819 = 0%, 4095 = 100%
    # Current Inputs are channels 1 & 2, Voltage input on channel 3
    
    hp_offset = -819
    hp_gain = 7500/(4095-819)
    O2Airlock_offset = -819
    O2Airlock_gain = 100/(4095-819)
    O2Glovebox_offset = -819
    O2Glovebox_gain = 100/(4095-819)
    
    # Read analog values from each channel
    chan1 = AnalogIn(ads, ADS.P0)
    chan2 = AnalogIn(ads, ADS.P1)
    chan3 = AnalogIn(ads, ADS.P2)
    #chan4 = AnalogIn(ads, ADS.P3)
    
    print(chan3.value)

    #Convert ADC output to real values
    Hydraulic_Pressure = (chan3.value + hp_offset) * hp_gain
    O2_Concentration_Airlock = (chan1.value + O2Airlock_offset) * O2Airlock_gain
    O2_Concentration_Glovebox = (chan2.value + O2Glovebox_offset) * O2Glovebox_gain

    # Format ADC values into a CSV string
    dat_list = [Hydraulic_Pressure,O2_Concentration_Airlock,O2_Concentration_Glovebox]
    graphing_array.append(dat_list)
    csv_string = f"{Hydraulic_Pressure}, {O2_Concentration_Airlock}, {O2_Concentration_Glovebox}\n"

    return csv_string

def write_to_csv_file(file_path, csv_data):
    # Open the file in append mode (create if not exists)
    with open(file_path, 'a') as file:
        # If the file is empty, write a header
        if os.path.getsize(file_path) == 0:
            file.write("Hydraulic Pressure, Airlock O2 Conc., Glovebox O2 Conc., ADC4_value\n")

        # Write the CSV data
        file.write(csv_data)
        file.close()
    return

#Data Display & Record
def display_data():
    global disp1, disp_height, disp_width, BORDER, FONTSIZE, dat_list, Switch_State, LockRotary
    
    #tm.sleep(0.5)
    
    print("Called")
    
    #display_types = {1,1,1,1}
    Button_Pressed = 0
    loop_data = 0
    
    # Load a TTF Font
    font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", FONTSIZE)
    text = "test 12 chars"
    bbox = font.getbbox(text)
    font_width = bbox[2] - bbox[0]
    font_height = bbox[3] - bbox[1]
    
    #Small Font
    font2 = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", FONTSIZE//2)
    bbox2 = font.getbbox(text)
    font2_width = bbox2[2] - bbox2[0]
    font2_height = bbox2[3] - bbox2[1]
    
    while(loop_data != 1):
        #Create Background
        image = Image.new("RGB", (disp_width, disp_height))
        draw = ImageDraw.Draw(image)
        draw.rectangle((0, 0, disp_width, disp_height), fill=(255, 85, 0))
    
        #Create inner rectangle
        draw.rectangle(
            (BORDER, BORDER, disp_width-BORDER-1, disp_height-BORDER-1), fill=(0, 0, 0)
        )        
        
        
        print("Entered Loop")
        print("Button Pressed State: {}".format(Button_Pressed))
        #Pull Data
        tm.sleep(0.05) #refresh at 20Hz
        csv_unused = pullADCvalues()
        csv_unused = " "
        
        
        if(Button_Pressed == 1):
            loop_data = 1
            Button_Pressed = 0
        
        #Display Hydraulic Pressure
        if(True):
            #Display the Hydraulic Pressure
            Hp_text = "Hydraulic Pressure:"
            Hp_text_value = "{:.2f} Psi".format(dat_list[0])
            Hp_x = BORDER + 10
            Hp_y = 20
            draw.text(
                (Hp_x, Hp_y),
                Hp_text,
                font=font,
                fill=(255, 255, 255)
            )
            draw.text(
                (Hp_x, Hp_y+20),
                Hp_text_value,
                font=font,
                fill=(255, 255, 255)
            )
        
        
        #Display Airlock Oxygen Concentration
        if(True):
            #Display the Airlock oxygen Concentration
            O2A_text = "Airlock O2 Con.:"
            O2A_text_value = "{:.2f} %".format(dat_list[1])
            O2A_x = BORDER + 10
            O2A_y = 80
            draw.text(
                (O2A_x, O2A_y),
                O2A_text,
                font=font,
                fill=(255, 255, 255)
            )
            draw.text(
                (O2A_x, O2A_y+20),
                O2A_text_value,
                font=font,
                fill=(255, 255, 255)
            )        
        
        #Display Glovebox Oxygen Concentration
        if(True):
            #Display the Glovebox Oxygen Concentration
            O2G_text = "Glovebox O2 Con.:"
            O2G_text_value = "{:.2f} %".format(dat_list[2])
            O2G_x = BORDER + 10
            O2G_y = 140
            draw.text(
                (O2G_x, O2G_y),
                O2G_text,
                font=font,
                fill=(255, 255, 255)
            )
            draw.text(
                (O2G_x, O2G_y+20),
                O2G_text_value,
                font=font,
                fill=(255, 255, 255)
            )
            
            
        #Display Exit Message
        exit_text = "Press Button to Exit"
        exit_x = BORDER + 10
        exit_y = 210
        draw.text(
            (exit_x, exit_y),
            exit_text,
            font=font2,
            fill=(255, 255, 255)
        )        

        disp1.image(image)
        
        #Check Button -> if pressed return to start menu
        LockRotary.acquire()
        if(Switch_State == 1):
            print("Button_Pressed")
            Button_Pressed = 1
            Switch_State = 0
            start_menu()    
        LockRotary.release()
        
        

        
    #return

def record_data():
    global disp1, disp_height, disp_width, BORDER, FONTSIZE, dat_list, Switch_State, LockRotary
    
    
    #display_types = {1,1,1,1}
    Button_Pressed = 0
    loop_data = 0
    
    # Load a TTF Font
    font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", FONTSIZE)
    text = "test 12 chars"
    bbox = font.getbbox(text)
    font_width = bbox[2] - bbox[0]
    font_height = bbox[3] - bbox[1]
    
    #Small Font
    font2 = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", FONTSIZE//2)
    bbox2 = font.getbbox(text)
    font2_width = bbox2[2] - bbox2[0]
    font2_height = bbox2[3] - bbox2[1]
    
    while(loop_data != 1):
        
        #Create Background
        image = Image.new("RGB", (disp_width, disp_height))
        draw = ImageDraw.Draw(image)
        draw.rectangle((0, 0, disp_width, disp_height), fill=(255, 85, 0))
    
        #Create inner rectangle
        draw.rectangle(
            (BORDER, BORDER, disp_width-BORDER-1, disp_height-BORDER-1), fill=(0, 0, 0)
        )        
        
        #Pull Data
        tm.sleep(0.05) #refresh at 20Hz
        csv_print = pullADCvalues()
        
        #Record data in file
        file_name = "test_data.csv"
        write_to_csv_file(file_name, csv_print)
        
        
        if(Button_Pressed == 1):
            loop_data = 1
            Button_Pressed = 0
        
        #Display Hydraulic Pressure
        if(True):
            #Display the Hydraulic Pressure
            Hp_text = "Hydraulic Pressure:"
            Hp_text_value = "{:.2f} Psi".format(dat_list[0])
            Hp_x = BORDER + 10
            Hp_y = 20
            draw.text(
                (Hp_x, Hp_y),
                Hp_text,
                font=font,
                fill=(255, 255, 255)
            )
            draw.text(
                (Hp_x, Hp_y+20),
                Hp_text_value,
                font=font,
                fill=(255, 255, 255)
            )
        
        
        #Display Airlock Oxygen Concentration
        if(True):
            #Display the Airlock oxygen Concentration
            O2A_text = "Airlock O2 Con.:"
            O2A_text_value = "{:.2f} %".format(dat_list[1])
            O2A_x = BORDER + 10
            O2A_y = 80
            draw.text(
                (O2A_x, O2A_y),
                O2A_text,
                font=font,
                fill=(255, 255, 255)
            )
            draw.text(
                (O2A_x, O2A_y+20),
                O2A_text_value,
                font=font,
                fill=(255, 255, 255)
            )        
        
        #Display Glovebox Oxygen Concentration
        if(True):
            #Display the Glovebox Oxygen Concentration
            O2G_text = "Glovebox O2 Con.:"
            O2G_text_value = "{:.2f} %".format(dat_list[2])
            O2G_x = BORDER + 10
            O2G_y = 140
            draw.text(
                (O2G_x, O2G_y),
                O2G_text,
                font=font,
                fill=(255, 255, 255)
            )
            draw.text(
                (O2G_x, O2G_y+20),
                O2G_text_value,
                font=font,
                fill=(255, 255, 255)
            )
            
        
        #Display Exit Message
        recording_text = "Recording..."
        recording_x = BORDER + 10
        recording_y = 200
        draw.text(
            (recording_x, recording_y),
            recording_text,
            font=font2,
            fill=(255, 255, 255)
        )  
        
        #Display Exit Message
        exit_text = "Press Button to Stop"
        exit_x = BORDER + 10
        exit_y = 210
        draw.text(
            (exit_x, exit_y),
            exit_text,
            font=font2,
            fill=(255, 255, 255)
        )        
        
        disp1.image(image)
        
        #Check Button -> if pressed return to start menu
        LockRotary.acquire()
        if(Switch_State == 1):
            print("Button_Pressed")
            Button_Pressed = 1
            Switch_State = 0
            start_menu()    
        LockRotary.release()
        
        

    #return

#User Interface 
def draw_menu(sel_opt):
    global disp1, disp_height, disp_width, BORDER, FONTSIZE
    #This function displays the menu options
    
    #Create Background
    image = Image.new("RGB", (disp_width, disp_height))
    draw = ImageDraw.Draw(image)
    draw.rectangle((0, 0, disp_width, disp_height), fill=(255, 85, 0))
    
    #Create inner rectangle
    draw.rectangle(
        (BORDER, BORDER, disp_width-BORDER-1, disp_height-BORDER-1), fill=(0, 0, 0)
    )
    # Load a TTF Font
    font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", FONTSIZE)
    text = "test 12 chars"
    bbox = font.getbbox(text)
    font_width = bbox[2] - bbox[0]
    font_height = bbox[3] - bbox[1]
    #disp1.image(image)
    
    #Small Font
    font2 = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", FONTSIZE//2)
    bbox2 = font.getbbox(text)
    font2_width = bbox2[2] - bbox2[0]
    font2_height = bbox2[3] - bbox2[1]
    
    #Create the menu Options ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    num_options = 3
    
    Option_box_locy1 = 22
    Option_box_locx = 40
    
    Option_box_height = font_height+40
    Option_box_width = font_width+40
    Space_height =  10 #(disp_height-(BORDER*2)-(Option_box_height*num_options))//(num_options+1)
    
    #Debug
    #print("locy1 = {}".format(Option_box_locy1))
    #print("locx = {}".format(Option_box_locx))
    #print("height = {}".format(Option_box_height))
    #print("width = {}".format(Option_box_width))
    #print("running = {}".format(sel_opt))
    
    #Exit Option ~~~~~~~~~~~~~~~~~~~~~~
    ex1 = Option_box_locx
    ey1 = Option_box_locy1
    ex2 = Option_box_locx+Option_box_width
    ey2 = Option_box_locy1+Option_box_height
    if(sel_opt == 1):
        draw.rectangle((ex1, ey1, ex2, ey2), fill=(128,43,0), outline=(255,255,255))
    else:
        draw.rectangle((ex1, ey1, ex2, ey2), fill=(128,43,0))
    Exit_text = "Exit"
    et_x = ex1+10
    et_y = ey1+(Option_box_height - font_height) // 2
    draw.text(
        (et_x, et_y),
        Exit_text,
        font=font,
        fill=(255, 255, 255)
    )
    
    #Display Data Option~~~~~~~~~~~~~~~
    dx1 = Option_box_locx
    dy1 = Option_box_locy1+(Option_box_height+Space_height)
    dx2 = Option_box_locx+Option_box_width
    dy2 = Option_box_locy1+(Option_box_height*2+Space_height)
    if(sel_opt == 2):
        draw.rectangle((dx1, dy1, dx2, dy2), fill=(128,43,0), outline=(255,255,255))
    else:
        draw.rectangle((dx1, dy1, dx2, dy2), fill=(128,43,0))
    display_text = "Display Data"
    dt_x = dx1+10
    dt_y = dy1+(Option_box_height - font_height) // 2
    draw.text(
       (dt_x, dt_y),
       display_text,
       font=font,
       fill=(255, 255, 255)
    )
    
    #Record Data Option~~~~~~~~~~~~~~~
    rx1 = Option_box_locx
    ry1 = Option_box_locy1+(Option_box_height*2+Space_height*2)
    rx2 = Option_box_locx+Option_box_width
    ry2 = Option_box_locy1+(Option_box_height*3+Space_height*2)
    if(sel_opt == 3):
        draw.rectangle((rx1, ry1, rx2, ry2), fill=(128,43,0), outline=(255,255,255))
    else:
        draw.rectangle((rx1, ry1, rx2, ry2), fill=(128,43,0))
    record_text = "Record Data"
    rt_x = rx1+10
    rt_y = ry1+(Option_box_height - font_height) // 2
    draw.text(
       (rt_x, rt_y),
       record_text,
       font=font,
       fill=(255, 255, 255)
    )
    
    #Display IP address:
    
    # host_name = sk.gethostname()
    # host_ip = sk.gethostbyname(host_name)
    # print("Hostname :  ", host_name)
    # print("IP : ", host_ip)
    
    ip_addr = sk.gethostbyname(sk.gethostname())
    ip_x = BORDER + 100
    ip_y = 220
    draw.text(
       (ip_x, ip_y),
       ip_addr,
       font=font2,
       fill=(255, 255, 255)
    )    
    
    #Refresh Screen
    disp1.image(image)
    return

def start_menu():
    global Rotary_counter, LockRotary, Switch_State
    tm.sleep(0.5)
    #This menu starts after main is called
    
    #Reset Rotary encoder and Button
    LockRotary.acquire()
    Rotary_counter = 0
    Switch_State = 0
    LockRotary.release()
    
    Button_Pressed = 0                #Denotes whether the option was selected
    Loop_exit = 0                     #Exit loop if var = 1
    Highlighted_option = 1            #Denotes which option is highlighted
    Available_options = 3             #Denotes how many avaiable options
    exit_option = 1                   #Denotes which option exits menu
    display_data_option = 2           #Denotes which option calls "display_data"
    record_data_option = 3            #Denotes which option calls "record_data"
    # -- add more options here; update "Available_options" and add elif's below --

    
    while(Loop_exit != 1):
        #Exit if desired + reset encoder and button states
        if(Button_Pressed == 1):
            print("loop entered")
            if(Highlighted_option == exit_option):
                Loop_exit = 1
                Highlighted_option = 1
                Button_Pressed = 0    
            elif(Highlighted_option == display_data_option):
                print("pressed right")
                Loop_exit = 0
                Button_Pressed = 0
                display_data()                               #Call display_data
                Highlighted_option = 1
            elif(Highlighted_option == record_data_option):
                Loop_exit = 0
                Highlighted_option = 1
                Button_Pressed = 0
                record_data()                               #Call record_data
            else:
                Loop_exit = 0
                Highlighted_option = 1
                Button_Pressed = 0                          #reset values if error
                
        #Draw Graphics & pass current selection
        draw_menu(Highlighted_option)
        tm.sleep(0.05)
        
        
        #Check for rotary encoder updates & button press ~~~~~~~~~~~~~~~~~~~~~~
        LockRotary.acquire()
        Highlighted_option += Rotary_counter
        Rotary_counter = 0
    
        #Check for bounds
        if(Highlighted_option > Available_options):
            Highlighted_option = 1
        elif(Highlighted_option < 1):
            Highlighted_option = 1
            
        #Check Button
        if(Switch_State == 1):
            print("Button_Pressed")
            Button_Pressed = 1
            Switch_State = 0
        
            
        LockRotary.release()
        #End check ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    
    return


def main():
   global Rotary_counter, LockRotary, Switch_State, disp1, disp_height, disp_width
   
   current_position = 0
   current_state = 0
   
   #Initialize Components
   init_Rotary()
   init_Display()
   
   #Call Start menu
   start_menu()
   
   
   
   exit(0)  
   
   tm.sleep(0.5)
   
main()
    




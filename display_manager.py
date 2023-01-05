from lib_pico.ST7735_GUI import *

class MorseAudioDisplay():
    def __init__(self):
        self.display = TFT_display()
        self.rx_speed_text_frame = self.display.add_frame("rx_speed_text",0,0,0,11,TFT.WHITE)
        self.rx_speed_text_frame.write_text("Est._RX_dot:")
        self.rx_speed_text_unit_frame = self.display.add_frame("rx_speed_unit_",0,17,0,20,TFT.WHITE)
        self.rx_speed_text_unit_frame.write_text("_ms_")
        self.rx_speed_display = self.display.add_frame("rx_speed_value",0,12,0,16,TFT.GREEN)
        self.decoding_panel = self.display.add_frame("decoding_panel",2,0,13,20,TFT.YELLOW)


class MorseDisplayManager():
    def __init__(self, keying_speed_controller=None):
        self.keying_speed_controller = keying_speed_controller
        self.display = TFT_display()
        #encoding section
        self.tx_speed_text_frame = self.display.add_frame("tx_speed_text",0,0,0,10,TFT.GREEN)
        self.tx_speed_text_frame.write_text("TX_Speed:__")
        self.tx_speed_text_unit_frame = self.display.add_frame("tx_speed_unit_text",0,17,0,20,TFT.GREEN)
        self.tx_speed_text_unit_frame.write_text("_wpm")
        self.tx_dot_text_frame = self.display.add_frame("tx_dot_text",1,0,1,10,TFT.GREEN)
        self.tx_dot_text_frame.write_text("Dot_time:__")
        self.tx_dot_text_unit_frame = self.display.add_frame("tx_dot_unit_text",1,17,1,20,TFT.GREEN)
        self.tx_dot_text_unit_frame.write_text("_ms_")
        self.tx_speed_display = self.display.add_frame("tx_speed_value",0,11,0,16,TFT.WHITE)
        self.tx_dot_display = self.display.add_frame("tx_dot_value",1,11,1,16,TFT.WHITE)
        self.encoding_panel = self.display.add_frame("encoding_panel",2,0,3,20,TFT.YELLOW)
        
        #decoding section
        self.rx_speed_text_frame = self.display.add_frame("rx_speed_text",5,0,5,11,TFT.ORANGE)
        self.rx_speed_text_frame.write_text("Est._RX_dot:")
        self.rx_speed_text_unit_frame = self.display.add_frame("rx_speed_unit_",5,17,5,20,TFT.ORANGE)
        self.rx_speed_text_unit_frame.write_text("_ms_")
        self.rx_speed_display = self.display.add_frame("rx_speed_value",5,12,5,16,TFT.WHITE)
        self.decoding_panel = self.display.add_frame("decoding_panel",6,0,13,20,TFT.YELLOW)
      
    def set_keying_speed_controller(self, speed_controller):
        self.keying_speed_controller = speed_controller
               
    def update_TX_speed(self):
        wpm_str = f"{self.keying_speed_controller.word_per_mn:>5d}"
        dot_str = f"{self.keying_speed_controller.dot_time:>5d}"
        self.tx_speed_display.write_text(wpm_str, reset_position=True)
        self.tx_dot_display.write_text(dot_str, reset_position=True)




    
def test():
    print("start test: 'morse_display_manager'")
    from async_morse.keying_controller import KeyingSpeedController
    import time
    #init display
    display_manager = MorseDisplayManager()
    # init keying speed manager
#     speed_up_pb_gpio = 3 # bouton K1 active LO
#     speed_down_pb_gpio = 2 # bouton K2 active LO        
#     speed_controller = KeyingSpeedController(display_manager, speed_up_pb_gpio, speed_down_pb_gpio)
#     display_manager.set_keying_speed_controller(speed_controller)
    for n in range(20):
        word_per_mn = 4+n*2
        dot_time = 800/word_per_mn
        display_manager.tx_dot_display.write_text(f"{dot_time:>5.2f}")
        display_manager.tx_speed_display.write_text(f"{word_per_mn:>3d}")
        time.sleep_ms(200)
    display_manager.encoding_panel.write_text("this is the encoding panel----"*5)
    for rx_dot in range(30,150,10):
        display_manager.rx_speed_display.write_text(f"{rx_dot:>4.1f}")
        time.sleep_ms(200)
    display_manager.decoding_panel.write_text("this is the decoding panel----".upper()*6)
    print("end test")

if __name__ == "__main__":
    test()

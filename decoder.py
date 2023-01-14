import uasyncio
import utime
from machine import Pin, Signal

from lib_pico.async_push_button import Button
from Morse_decoder.user_dialog import UserDialog
from Morse_decoder.keying_controller import KeyingToneEncoder, KeyingSpeedController
from Morse_decoder.display_manager import MorseDisplayManager
from Morse_decoder.code_translator import *


from debug_utility.pulses import Probe    
probe_gpio = 16
pb=Probe(probe_gpio)
    


class RxBuffer():
    def __init__(self):
        self.rx_buffer = []
        self.buffer_ready = uasyncio.ThreadSafeFlag()       
    def push(self, data):
        self.rx_buffer.insert(0, data)
        self.buffer_ready.set()    
    def pull(self):
        data=self.rx_buffer.pop()
        #print(f"@{utime.ticks_ms()}=\t\tRxBuffer/pull: '{data}'  {self.rx_buffer}")     
        return data    
    def size(self):
        return len(self.rx_buffer)

class DotTimeShiftRegister():
    def __init__(self):
        self.register = []      
    def push(self, data):
        self.register.insert(0, data)
        if len(self.register)>5:
            del self.register[-1]
    def get_min(self):
        data=min(self.register)    
        return data    
    def size(self):
        return len(self.register)
    

class RXTimingProcessor():
    def __init__(self, display, key_in_gpio, rx_buffer):
        self.display = display
        self.rx_buffer = rx_buffer
        self.key_in_pin = Pin(key_in_gpio, Pin.IN)
        self.key_in_signal = Signal(self.key_in_pin, invert = True)
        self.key_in = Button("key", key_in_gpio, pull=-1,
                 interrupt_service_routine=self.key_in_IRQ_handler, debounce_delay=30,
                 active_HI=False, both_edge=True )
        self.key_duration_list = []
        self.dot_time_list = DotTimeShiftRegister()
        self.dot_time = 1000
        self.timeout = 1000
       
    def update_dot_time(self, duration):
        self.dot_time_list.push(duration)
        self.dot_time = self.dot_time_list.get_min()
        self.timeout = 12 * self.dot_time
        self.display.rx_speed_display.write_text("{:>4d}".format(self.dot_time),
                                                 reset_position=True)
    
    def key_in_IRQ_handler(self, button):        
        duration = button.last_event_duration
        self.update_dot_time(duration)
        if button.is_pressed == True: #on sort d'un silence, on commence un son
            key_code = self.translate_silence(duration/self.dot_time)
            self.rx_buffer.push(key_code)
        else: 
            key_code = self.translate_tone(duration/self.dot_time)
            self.rx_buffer.push(key_code)   
       
    def translate_silence(self, t):
        if t > 0.5 and t < 1.5:   # gap inter code 
            return "+"
        elif t > 2 and t < 4: # gap inter lettres
            return "|"
        elif t >= 4 :
            return "#"          # gap inter mots

    def translate_tone(self, t):
        if t >= 0.5 and t <= 1.5:
            return "."
        elif t >= 2 and t < 4:
            return "-"
        else:
            return "?"
    
    

class MorseDecoder():
    def __init__(self, display, rx_key_processor, rx_buffer):
        self.rx_buffer = rx_buffer
        self.display = display
        self.current_code = []
        self.rx_key_processor = rx_key_processor
        self.translator = MorseTranslator()

    def convert_current_code(self):
        if len(self.current_code) !=0:
            code=""
            for e in self.current_code:
                code += e
            letter = self.translator.to_letter(code)
            if letter == None : letter = "*"
            return letter
        else:
            return " "

    def write_code(self, txt, step=1):
        self.display.decoding_panel.write_text(txt, reset_position=False)

    def decode_keying(self, key):
        if (key == ".") or (key=="-"):
            self.current_code.append(key)
        
        elif key=="|":
            letter = self.convert_current_code()
            self.write_code(letter, step=len(letter))
            self.current_code.clear()

        elif key=="#":
            letter = self.convert_current_code()
            self.write_code(f"{letter} ", step=len(letter)+1)
            self.current_code.clear()
#         else:
#             return
        
    async def process_key_stream(self):
        if __name__ == "__main__" : print(f"@{utime.ticks_ms()}------------>start 'process_key_stream'")
        while True:
            while self.rx_buffer.size() > 0:
                key_code = self.rx_buffer.pull()                  
                self.decode_keying(key_code)
            self.rx_buffer.buffer_ready.clear()
            try:
                if self.rx_key_processor.dot_time_list.size()==0: timeout=1000
                else : timeout = self.rx_key_processor.dot_time*10
                await uasyncio.wait_for_ms(self.rx_buffer.buffer_ready.wait(),timeout)
            except uasyncio.TimeoutError:
                #pb.pulses(30)  ##############################
                #print ("timeout")
                self.decode_keying("#")
                self.rx_buffer.buffer_ready.clear()
                await self.rx_buffer.buffer_ready.wait()
        if __name__ == "__main__" : print("--------------->stop 'process_key_stream'")


 
    async def simulate_keying_code(self, code, signals):
        self.display.encoding_panel.write_text(code_to_letter[code], reset_position=False)
        if (code == " "):
            # silence entre deux mots : [4]=[7]-[2]-[1]  TODO voir pourquoi c'esst 2 et pas 4 qu'il faut mettre
            await  uasyncio.sleep_ms(4*self.rx_key_processor.dot_time)
            self.rx_buffer.insert(0,"#")
            self.buffer_ready.set()
        else:            
            for code_element in code:
                # [1]silence entre deux morse_element de code_morse
                await  uasyncio.sleep_ms(self.rx_key_processor.dot_time)
                for s in signals: s.on() # keying on()                    
                if(code_element == "."):
                    await  uasyncio.sleep_ms(self.rx_key_processor.dot_time) # [1] codage d'un point
                if(code_element == "-"):
                    await  uasyncio.sleep_ms(3*self.rx_key_processor.dot_time) # [3] codage d'un tiret
                for s in signals:s.off()
                self.rx_buffer.insert(0,code_element)
                self.buffer_ready.set()
    
    async def simulate_keying_sentence(self, sentence, signals):
        words = sentence.split()
        for word in words:
            await self.simulate_keying_code(" ", signals) # simu entre mots pour eviter d'envoyer "#" à la fin de sentence       
            if word.isupper(): # word in upper case = symbole predefini e.g.SOS
                keyword = letter_to_code[word]
                for key in keyword:
                    self.rx_buffer.insert(0,keyword)
                self.rx_buffer.insert(0,"#")
                self.buffer_ready.set()
                await self.simulate_keying_code(letter_to_code[word], signals)
            else:
                for letter in word:
                # [2]=[3]-[1] silence entre deux lettres - 1 silence finissant le dernier element
                    await  uasyncio.sleep_ms(2*self.rx_key_processor.dot_time) 
                    self.rx_buffer.insert(0,"|")
                    self.buffer_ready.set()
                    await self.simulate_keying_code(letter_to_code[letter], signals)
 
#------------------------------------------------------------------------------
                    
if __name__ == "__main__":
    
    print("start test closed loop morse coder-decoder")

    # setup display
    display_manager = MorseDisplayManager()

    # setup TX speed keying manager    
    speed_up_pb_gpio = 22 # bouton K3 active LO
    speed_down_pb_gpio = 2 # bouton K2 active LO        
    tx_speed_controller = KeyingSpeedController(display_manager,
                                          speed_up_pb_gpio,
                                          speed_down_pb_gpio)   
    display_manager.set_keying_speed_controller(tx_speed_controller)
    tx_speed_controller.word_per_mn = 8
    tx_speed_controller.update_speed()
    display_manager.update_TX_speed()


    # setup encoder
    key_out_gpio = 6
    led_gpio = "LED" # on-board led active HI, gpio 25
    buzzer_on = False
    key_out = Signal(key_out_gpio, Pin.OUT,  invert=False) # active HI
    led = Signal(led_gpio, Pin.OUT)
    signals = [led, key_out]
    if buzzer_on == True:
        signals.append(buzzer)    
    encoder = KeyingToneEncoder(display_manager.encoding_panel,
                                  tx_speed_controller, signals)

    # setup Rx Buffer
    rx_buffer = RxBuffer()

    # setup decoder   
    key_in_gpio = 7
    rx_keying = RXTimingProcessor(display_manager,key_in_gpio, rx_buffer)
    decoder = MorseDecoder(display_manager,rx_keying, rx_buffer)

    # setup main dialog
    main_dialog=UserDialog()

    # setup asyncio tasks
    rx = decoder.process_key_stream()
    dialog = main_dialog.dialog_loop(encoder)
    tx = tx_speed_controller.update_speed()

    scheduler = uasyncio.get_event_loop()
    scheduler.create_task(rx)
    scheduler.create_task(dialog)
    scheduler.create_task(tx)
    scheduler.run_forever()

#     uasyncio.create_task(dialog)
#     uasyncio.run(rx)

#     uasyncio.create_task(rx)    
#     uasyncio.run(dialog)








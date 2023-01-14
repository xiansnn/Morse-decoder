from machine import Pin, Signal
import uasyncio
import utime
from Morse_decoder.code_translator import MorseTranslator
from lib_pico.async_push_button import Button

from debug_utility.pulses import Probe    
probe_gpio = 16
pb=Probe(probe_gpio)

#TODO possible de rester avec un dot-time d e60ms et de faire uniquement varier l'espace intermot #
#TODO selon la formule T# = n*dot =dot *(25-wph*16/1000) et wph = word per hour = 60 * wpm
#TODO pour le test audio, prevoir un filtre 500Hz à la sortie de micro


class KeyingSpeedController():
    """
vitesse de commande : 6<=word_per_mn<=30
derivés : word_per_hour = 60*word_per_mn
'.' code dot_time = word_per_mn*(-1.22)+ 78
'-' code dash_time = 3*dot_time
'+' inter symbol = dot_time
'|' nb dot inter letter = 450/(word_per_mn)^^2 + 2
'#' nb dot inter word =  1700/(word_per_mn)^^2 + 4.5
"""
    def __init__(self, display_manager,
                 speed_up_pb_gpio, speed_down_pb_gpio):
        self.display = display_manager
        self.word_per_mn = 10
        self.dot_time = 0
        self.nb_dot_inter_letter = 0
        self.inter_letter_time = 0
        self.nb_dot_inter_word = 0
        self.inter_word_time = 0

        self.delta = 0
        self.speed_changed = uasyncio.ThreadSafeFlag()
        
        self.speed_up_btn = Button("speed_up_btn", speed_up_pb_gpio,
                              active_HI=False, repeat=True, repeat_delay=150)
        self.speed_dn_btn = Button("speed_dn_btn", speed_down_pb_gpio,
                              active_HI=False, repeat=True, repeat_delay=150)
        
        self.speed_dn_btn.set_irq_routine(self.speed_update_IRQ_routine)
        self.speed_up_btn.set_irq_routine(self.speed_update_IRQ_routine)

    def compute_keying_times(self):
        # version simple , lineaire
#         self.dot_time = int(800/self.word_per_mn)
#         self.nb_dot_inter_letter = 3
#         self.inter_letter_time = self.nb_dot_inter_letter*self.dot_time
#         self.nb_dot_inter_word = 9
#         self.inter_word_time = self.nb_dot_inter_word*self.dot_time

        
        
        # version complexe simulant le cours de morse de F5IRO      
        self.dot_time = int(-1.3*self.word_per_mn+76)
        self.inter_letter_time = self.dot_time * 3
        self.inter_word_dot = 10 + int((67*self.word_per_mn +8238)/(self.word_per_mn*self.word_per_mn*self.word_per_mn))
        self.inter_word_time = self.inter_word_dot * self.dot_time
        if __name__ == "__main__" :   
            print(f"""\twpm:{self.word_per_mn}, dot:{self.dot_time},
    # \t"|":{self.inter_letter_time}ms\t"#":{self.inter_word_time}ms""") 

    async def update_speed(self):
        while True:
            #pb.pulses(30)
            if __name__ == "__main__" : print("KeyingSpeedController/update_speed")
            self.word_per_mn = min(max(self.word_per_mn + self.delta, 5),20)
            self.compute_keying_times()
            self.delta = 0
            self.speed_changed.clear()
            self.display.update_TX_speed()
            await self.speed_changed.wait()


    def speed_update_IRQ_routine(self, button):
        if __name__ == "__main__" : print("KeyingSpeedController/speed_update_IRQ_routine")
        if button == self.speed_up_btn:
            self.delta = +1
        elif button == self.speed_dn_btn:
            self.delta = -1
        self.speed_changed.set()

class KeyingToneEncoder():
    def __init__(self,frame, speed, signals):
        self.keying_speed = speed
        self.signals = signals
        self.coder_frame = frame
        self.translate = MorseTranslator()
    
    async def keying_code(self, code):
        if __name__=="__main__":
            print(f"keying_code:'{code}'")
        if (code == "#"):
            # silence entre deux mots : [4]=[10]-[2]-[1]
            await  uasyncio.sleep_ms(self.keying_speed.inter_word_time - self.keying_speed.inter_letter_time- self.keying_speed.dot_time)
        elif (code == "|"):
            # silence fin de lettre pour um mot-clé (HH, SOS, etc)
            await  uasyncio.sleep_ms(self.keying_speed.inter_letter_time - self.keying_speed.dot_time)           
        else:            
            for code_element in code:
                for s in self.signals: s.on() # keying on()                    
                if(code_element == "."):
                    await  uasyncio.sleep_ms(self.keying_speed.dot_time) # [1] codage d'un point
                if(code_element == "-"):
                    await  uasyncio.sleep_ms(3*self.keying_speed.dot_time) # [3] codage d'un tiret
                # [1]silence entre deux morse_element de code_morse
                for s in self.signals:s.off()
                await  uasyncio.sleep_ms(self.keying_speed.dot_time)
            # [2]=[3]-[1] silence entre deux lettres - 1 silence finissant le dernier element
            await  uasyncio.sleep_ms(self.keying_speed.inter_letter_time - self.keying_speed.dot_time)
 
    async def keying_sentence(self, sentence):
        while True:
            if __name__ == "__main__" : print(f"@{utime.ticks_ms()}--- start 'keying_sentence' : {sentence}")
            words = sentence.split()
            for word in words:
                if word.isupper():
                    await self.keying_code(self.translate.to_morse(word))               
                    self.coder_frame.write_text(word, reset_position=False)
                else:
                    for letter in word:
                        await self.keying_code(self.translate.to_morse(letter))
                        self.coder_frame.write_text(letter, reset_position=False)
                await self.keying_code(self.translate.to_morse(" ")) # fin de mot
                self.coder_frame.write_text(" ", reset_position=False)

        


if __name__ == "__main__":
    #test_audio()   
    print("start test <async_keying_controller.py>")

    # setup display
    from async_morse.display_manager import MorseDisplayManager
    display_manager = MorseDisplayManager()

    # setup TX speed keying manager
    speed_up_pb_gpio = 22 # bouton K1 active LO
    speed_down_pb_gpio = 2 # bouton K2 active LO        
    tx_speed_controller = KeyingSpeedController(display_manager,
                                          speed_up_pb_gpio,
                                          speed_down_pb_gpio)
    display_manager.set_keying_speed_controller(tx_speed_controller)
    tx_speed_controller.word_per_mn = 5
    tx_speed_controller.compute_keying_times()    
    display_manager.update_TX_speed()

    # setup encoder
    key_out_gpio = 6
    led_gpio = "LED" # on-board led active HI, gpio 25
    buzzer_on = False
    key_out = Signal(key_out_gpio, Pin.OUT,  invert=False) # active HI
    led = Signal(led_gpio, Pin.OUT)
    signals = [led, key_out]
    if buzzer_on == True:
        signals.append(Signal(4,Pin.OUT,invert=False) )   
    encoder = KeyingToneEncoder(display_manager.encoding_panel,
                                  tx_speed_controller, signals)
    
    tx=encoder.keying_sentence("HH at i e") 
    scheduler = uasyncio.get_event_loop()
    scheduler.create_task(tx_speed_controller.update_speed())
    uasyncio.run(tx)
        

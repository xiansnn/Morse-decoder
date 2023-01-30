import uasyncio
import utime


class UserDialog():
    def __init__(self):
        #self.default_sentence = "HH KA SL cq de f3tv + VA "
        #self.default_sentence = "HH e 0 HH "
        self.default_sentence = "HH at i e "
        self.sentence = self.default_sentence

    async def simulate_dialog_loop(self, decoder, signals):
        if __name__ == "__main__": print("--------------->start 'simulate_dialog_loop'")
        while True:
            self.sentence = input("enter sentence: ")
            if self.sentence == "stop":
                break 
            elif self.sentence == "":
                self.sentence =  self.default_sentence
                print(f"sentence: {self.sentence}")
            else:
                print(f"sentence: {self.sentence}")
            await decoder.simulate_keying_sentence(self.sentence, signals)
            await uasyncio.sleep(5)
        if __name__ == "__main__": print("--------------->stop 'simulate_dialog_loop'")
        
    async def dialog_loop(self, encoder):
        if __name__ == "__main__": print(f"sentence: {self.sentence}")
        self.sentence = input("enter sentence: ")
        if self.sentence == "stop":
            loop = uasyncio.get_event_loop()
            loop.stop()   
        elif self.sentence == "":
            self.sentence =  self.default_sentence
            print(f"default sentence: {self.sentence}")
        else:
            print(f"new sentence: {self.sentence}")
        while True:
            await encoder.keying_sentence(self.sentence)
            await uasyncio.sleep(5)
#
#         while True:
#             self.sentence = input("enter sentence: ")
#             if self.sentence == "stop":
#                 break   
#             elif self.sentence == "":
#                 self.sentence =  self.default_sentence
#                 print(f"default sentence: {self.sentence}")
#             else:
#                 print(f"new sentence: {self.sentence}")
#             await encoder.keying_sentence(self.sentence)
#             await uasyncio.sleep(5)
#         if __name__ == "__main__":
#             print("end of user loop")
#             loop = uasyncio.get_event_loop()
#             loop.stop()

if __name__ == "__main__":
    
    from debug_utility.pulses import Probe
    probe_gpio = 16    
    p = Probe(probe_gpio)
    
    class Encoder():
        def __init__(self):
            print ("init Encoder")

        async def keying_sentence(self, sentence):
                print (sentence)
                p.pulses(1)
                await uasyncio.sleep_ms(6)
                p.pulses(1)
                
    class Decoder():
        def __init__(self):
            print ("init Decoder")

        async def process_key_stream(self):
            print ("process key stream")
            p.pulses(5)
            await uasyncio.sleep_ms(3)
            p.pulses(5)
            print ("process done")
    
         


    # setup main dialog
    main_dialog=UserDialog()
    
    tx = Encoder()
    rx = Decoder()
    keying_process = rx.process_key_stream()
    user_loop = main_dialog.dialog_loop(tx)

    # setup asyncio tasks

    scheduler = uasyncio.get_event_loop()
    scheduler.create_task(keying_process)
    scheduler.create_task(user_loop)
    
    scheduler.run_forever()

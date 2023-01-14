import uasyncio
import utime
from machine import Pin, Signal
from micropython import const

KEY_IN_GPIO = const(7)


from Morse_decoder.decoder import MorseDecoder, RxBuffer, RXTimingProcessor
from Morse_decoder.display_manager import MorseAudioDisplay


    
print("start audio morse decoder")


display_manager = MorseAudioDisplay()
rx_buffer = RxBuffer() 

rx_keying = RXTimingProcessor(display_manager,KEY_IN_GPIO, rx_buffer)
decoder = MorseDecoder(display_manager,rx_keying, rx_buffer)

# setup asyncio tasks
rx = decoder.process_key_stream()
scheduler = uasyncio.get_event_loop()
scheduler.create_task(rx)
scheduler.run_forever()



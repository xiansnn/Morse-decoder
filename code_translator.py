#init code dictionary
_letter_dictionary = {
    "1"  : ".----",
    "2"  : "..---",
    "3"  : "...--",
    "4"  : "....-",
    "5"  : ".....",
    "6"  : "-....",
    "7"  : "--...",
    "8"  : "---..",
    "9"  : "----.",
    "0"  : "-----",
    #-----------------------------
    "a"  : ".-",
    "b"  : "-...",
    "c"  : "-.-.",
    "d"  : "-..",
    "e"  : ".",
    "é"  : "..-..",
    "f"  : "..-.",
    "g"  : "--.",
    "h"  : "....",
    "i"  : "..",
    "j"  : ".---",
    "k"  : "-.-",  #invitation à transmettre
    "l"  : ".-..",
    "m"  : "--",
    "n"  : "-.",
    "o"  : "---",
    "p"  : ".--.",
    "q"  : "--.-",
    "r"  : ".-.",
    "s"  : "...",
    "t"  : "-",
    "u"  : "..-",
    "v"  : "...-",
    "w"  : ".--",
    "x"  : "-..-",
    "y"  : "-.--",
    "z"  : "--..",
    #-----------------------------
    "."  : ".-.-.-",
    ","  : "--..--",
    ":"  : "---...",
    "?"  : "..--..",   # "pas compris, repetez"
    "'"  : ".----.",
    "-"  : "-....-",
    "/"  : "-..-.",
    "("  : "-.--.",
    ")"  : "-.--.-",
    "_"  : "..--.-",   
    "="  : "-...-",    # "stop" nouveau §


    "+"  : ".-.-.",    # "fin de msg", "invitation à transmettre"

    "!"  : "-.-.--",
    "&"  : ".-...",
    ";"  : "-.-.-.",
    "\"" : ".-..-.",
    "$"  : "...-..-",
    "@"  : ".--.-.",
    #------------------------------
    " "  : "#",        # "code clé signifiant fin de mot"
    "BK" : "-...-.-",  # "break"
    "VA" : "...-.-",   # "fin de transmisson" "silent key"
    "VE" : "...-.",    # "tout compris"
    "AS" : ".-...",    # "attente, patientez"
    "HH" : "........", # "erreur"
    "KA" : "-.-.-",    # "debut de message"
    "SL" : "....-..",  # "slow down" ralentissez
    "SOS": "...---..."
    }
_code_dictionary={
    '...---...': 'SOS',
    '-..'      : 'd',
    '-.-'      : 'k',
    '...'      : 's',
    ' '        : ' ',
    '.----.'   : "'",
    '---...'   : ':',
    '........' : 'HH',
    '-....'    : '6',
    '....-'    : '4',
    '.-..-.'   : '"',
    '.....'    : '5',
    '-...-'    : '=',
    '.-.-.'    : '+',
    '--..'     : 'z',
    '--.-'     : 'q',
    '..--..'   : '?',
    '--'       : 'm',
    '-.'       : 'n',
    '.-.'      : 'r',
    '..--.-'   : '_',
    '.--'      : 'w',
    '--...'    : '7',
    '-..-'     : 'x',
    '..-.'     : 'f',
    '-...'     : 'b',
    '---'      : 'o',
    '-.--.'    : '(',
    '.-...'    : 'AS',
    '...--'    : '3',
    '--.'      : 'g',
    '...-.'    : 'VE',
    '-....-'   : '-',
    '-.-.--'   : '!',
    '.--.'     : 'p',
    '.---'     : 'j',
    '..---'    : '2',
    '---..'    : '8',
    '...-..-'  : '$',
    '-..-.'    : '/',
    '-.-.-.'   : ';',
    '..'       : 'i',
    '.-'       : 'a',
    '.--.-'    : chr(134), #'à',
    '.--.-.'   : '@',
    '-...-.-'  : 'BK',
    '-----'    : '0',
    '....-..'  : 'SL',
    '.----'    : '1',
    '----.'    : '9',
    '--..--'   : ',',
    '...-'     : 'v',
    '-.--'     : 'y',
    '-.-.-'    : 'KA',
    '.-..'     : 'l',
    '....'     : 'h',
    '.'        : 'e',
    '..-..'    : chr(138), #'é',
    '-.-.'     : 'c',
    '-'        : 't',
    '...-.-'   : 'VA',
    '-.--.-'   : ')',
    '.-.-.-'   : '.',
    '..-'      : 'u'
    }

class MorseTranslator():
    def __init__(self):
        pass
    
    def to_morse(self, letter):
        if letter in _letter_dictionary:
            return _letter_dictionary[letter]
        else:
            return None
        
    def to_letter(self, code):
        if code in _code_dictionary:
            return _code_dictionary[code]
        else:
            return None




def test():
    print("start test: 'code_translator'")
    translate = MorseTranslator()
    for n in range(32,128):
        letter = chr(n)
        print( f" n={n}\t'{letter}'\t{translate.to_morse(letter)}")
    print("#"*20)
#     print("code->letter\n",_code_to_letter)
    for c in sorted(_code_dictionary):
        print( f"{c:<10s}\t{translate.to_letter(c)}")
    print("#"*20)

    print("end test")
    
if __name__ == "__main__":
    test()


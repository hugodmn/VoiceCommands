from fuzzywuzzy import fuzz
import time


class Commands():
    def __init__(self):
        self.commandsdic = dict()
        with open("Fuzzywuzzy/command.txt",'r') as f:
            lines = f.readlines()
            for line in lines :
                self.commandsdic[line.split("/")[0]] = line.split("/")[1]

    def comparaison(self, transcription : str):
        for command, activ in self.commandsdic.items():
            t = time.time()
            sim = fuzz.token_set_ratio(transcription, command)
            print(sim)
            if (sim > 70):
                print("activation of : ", activ)
            end = time.time()
            print("process time : ",end - t )




if __name__ == '__main__':
    GOSAIcommands = Commands()
    test = "Hello everyone"
    test2 = "triangle active"
    test3 = "sleep mod"
    test4 = "Hello everyone activation of the triangle please"
    GOSAIcommands.comparaison(test)
    GOSAIcommands.comparaison(test2)
    GOSAIcommands.comparaison(test3)
    GOSAIcommands.comparaison(test4)

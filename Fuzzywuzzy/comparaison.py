from fuzzywuzzy import fuzz
import time


class Commands():
    def __init__(self):
        self.commandsdic = dict()
        with open("command.txt",'r') as f:
            lines = f.readlines()
            for line in lines :
                self.commandsdic[line.split("/")[0]] = line.split("/")[1]
        self.modeactive = None 

    def comparaison(self, transcription : str):
        for command, activ in self.commandsdic.items():
            # t = time.time()


            activation = max(fuzz.partial_token_set_ratio(transcription, "active"),fuzz.partial_token_set_ratio(transcription, "achieve"))
  
            print("active prob : ", activation)
            if (activation > 80):
                
                
                #sim = fuzz.token_set_ratio(transcription, command)
                sim2 =     fuzz.partial_token_set_ratio(transcription, command)
                #print("token set ratio : ",sim)
                
                # print("checking for ", activ)
                # print("mode prob : ", sim2)

                if (sim2 > 85):
                    print("activation of : ", activ)
                    self.modeactive = activ 

            # end = time.time()
            # print("process time : ",end - t )
            # print("---------------------------------------------")




if __name__ == '__main__':
    GOSAIcommands = Commands()
    test = "Hello everyone"
    test2 = "triangle active"
    test3 = "activation of the triangles please GOSAI"
    test4 = "Hello everyone activation of the triangle please"
    test5 = "The life of activation of the triangle ok"
    GOSAIcommands.comparaison(test)
    GOSAIcommands.comparaison(test2)
    GOSAIcommands.comparaison(test3)
    GOSAIcommands.comparaison(test4)
    GOSAIcommands.comparaison(test5)

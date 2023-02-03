# VoiceCommands
1 - WakeUpWord 
Custom wake up word system (using a LSTM model) triggering the system when the keyword is recognized in a 2sec audio. 
The model is trained with a custom dataset to recognize the keyword : " Ok Gosai " .

2 - Speech to Text
Using the Whisper speech-to-text from OpenAI. 

3 - Fuzzywuzzy 
The string is then compared to several command strings with fuzzywuzzy. 

4 - Text to speech
Using pytts text-to-speech to give a feedback for the user. 






COMMAND.TXT : 


File composed of all commands we want the system to recognize and trigger : 

To add a new command, add in the file : 

"Word(s) to trigger the mode"/mode=NameOfTheMode/VocalFeedback

exemples : 

"sleep mode"/mode=sleep mode/"sleep mode"

-> STT : you need to say "Ok Gosai, start the sleep mode" or "Ok Gosai, stop the sleep mode"

-> TTS : the feed back will be "sleep mode started" or "sleep mode stopped"

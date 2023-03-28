import unittest
import torchaudio
from inference import LSTMInference


class TestInference(unittest.TestCase):
    
    def test_inference(self):
         #import an audio file
         device = "cpu"
         false1,sr = torchaudio.load("VoiceCommands/LSTM/test_audio/false_1.wav")
         false2,sr = torchaudio.load("VoiceCommands/LSTM/test_audio/false_2.wav")
         true1,sr = torchaudio.load("VoiceCommands/LSTM/test_audio/true_1.wav")
         true2,sr = torchaudio.load("VoiceCommands/LSTM/test_audio/true_2.wav")
         false1 = false1.squeeze(0).to(device)
         false2 = false2.squeeze(0).to(device)
         true1 = true1.squeeze(0).to(device)
         true2 = true2.squeeze(0).to(device)
         
         TestInfer = LSTMInference(device = device)
         #Compare inference of these files with the expecte result 
         pred_false1,_ = TestInfer.get_prediction(false1)
         pred_false2,_ = TestInfer.get_prediction(false2)
         pred_true1,_ = TestInfer.get_prediction(true1)
         pred_true2,_ = TestInfer.get_prediction(true2)
         
         
         self.assertEqual(pred_false1, 1)
         self.assertEqual(pred_false2, 1)
         self.assertEqual(pred_true1, 0) 
         self.assertEqual(pred_true2, 0)


if __name__ == '__main__':
    unittest.main()
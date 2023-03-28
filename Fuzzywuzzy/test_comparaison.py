import unittest 
import comparaison

class TestComparaison(unittest.TestCase):
    def test_comparaison(self):
        GOSAIcommands = comparaison.Commands()
        test = "Hello everyone"
        test2 = "start the triangles"
        test3 = "activation of the triangles please GOSAI"
        test4 = "Hello everyone please stop the triangle"
        test5 = "The life of activation of the triangle ok"

        start_triangle = "start","mode=triangles"
        stop_triangle = "stop","mode=triangles"
        self.assertEqual(GOSAIcommands.comparaison(test,debug=True), None)
        self.assertEqual(GOSAIcommands.comparaison(test2,debug=True), start_triangle)
        self.assertEqual(GOSAIcommands.comparaison(test3,debug=True), None)
        self.assertEqual(GOSAIcommands.comparaison(test4,debug=True), stop_triangle)
        self.assertEqual(GOSAIcommands.comparaison(test5,debug=True), None)

if __name__ == '__main__':
    unittest.main()
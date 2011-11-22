import unittest
import os

suite = unittest.TestSuite()
for n in filter(lambda fn: fn[-8:] == "Tests.py", os.listdir(".")):
    suite.addTest(unittest.defaultTestLoader.loadTestsFromName(n[:-3]))

runner = unittest.TextTestRunner()
runner.run(suite)

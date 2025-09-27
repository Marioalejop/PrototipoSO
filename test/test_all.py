"""
Archivo que ejecuta todas las pruebas del prototipo de sistema operativo.
Usa unittest para descubrir y ejecutar automáticamente los tests.
"""

import unittest
import os

def suite():
    loader = unittest.TestLoader()
    test_dir = os.path.dirname(__file__)
    suite = loader.discover(start_dir=test_dir, pattern="test_*.py")
    return suite

if __name__ == "__main__":
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite())

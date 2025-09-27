import unittest
from memoria import Memoria

class TestMemoria(unittest.TestCase):

    def setUp(self):
        self.memoria = Memoria(frames=4, frame_size=16)

    def test_allocate_and_free(self):
        frames = self.memoria.allocate_frames(pid=1, count=2)
        self.assertEqual(len(frames), 2)
        status = self.memoria.status()
        self.assertEqual(status["frames_used"], 2)

        self.memoria.free_frames(pid=1)
        status = self.memoria.status()
        self.assertEqual(status["frames_used"], 0)

    def test_write_and_read(self):
        frames = self.memoria.allocate_frames(pid=2, count=1)
        frame = frames[0]
        data = b"hola"
        self.assertTrue(self.memoria.write(frame, 0, data))
        self.assertEqual(self.memoria.read(frame, 0, 4), data)

if __name__ == "__main__":
    unittest.main()

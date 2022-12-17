from mfs import *
import subprocess
import toolspath
from testing.test import Failure

class SparseTest(MfsTest):
   name = "sparse"
   description = "write first and last block"
   timeout = 10

   def run(self):
      image = self.create_image()
      self.loadlib()
      self.start_server(image)

      self.mfs_init("localhost", self.port)
      self.creat(0, MFS_REGULAR_FILE, "test")
      inum = self.lookup(ROOT, "test")

      buf = gen_block(1)
      self.write(inum, buf, 0, MFS_BLOCK_SIZE)
      self.read_and_check(inum, 0, buf, MFS_BLOCK_SIZE)

      buf = gen_block(2)
      self.write(inum, buf, (MAX_FILE_BLOCKS - 1) * MFS_BLOCK_SIZE, MFS_BLOCK_SIZE)
      self.read_and_check(inum, (MAX_FILE_BLOCKS - 1) * MFS_BLOCK_SIZE, buf, MFS_BLOCK_SIZE)

      buf = gen_block(3)
      self.write(inum, buf, 0, MFS_BLOCK_SIZE)
      self.read_and_check(inum, 0, buf, MFS_BLOCK_SIZE)
      buf = gen_block(2)
      self.read_and_check(inum, (MAX_FILE_BLOCKS - 1) * MFS_BLOCK_SIZE, buf, MFS_BLOCK_SIZE)

      buf = gen_block(4)
      self.write(inum, buf, (MAX_FILE_BLOCKS - 1) * MFS_BLOCK_SIZE, MFS_BLOCK_SIZE)
      self.read_and_check(inum, (MAX_FILE_BLOCKS - 1) * MFS_BLOCK_SIZE, buf, MFS_BLOCK_SIZE)
      buf = gen_block(3)
      self.read_and_check(inum, 0, buf, MFS_BLOCK_SIZE)

      self.shutdown()
      self.server.wait()
      self.done()

class Stat2Test(MfsTest):
   name = "stat2"
   description = "stat a sparse file"
   timeout = 10

   def run(self):
      image = self.create_image()
      self.loadlib()
      self.start_server(image)

      self.mfs_init("localhost", self.port)
      self.creat(0, MFS_REGULAR_FILE, "test")
      inum = self.lookup(ROOT, "test")

      buf = gen_block(1)
      self.write(inum, buf, 0, MFS_BLOCK_SIZE)
      buf = gen_block(2)
      self.write(inum, buf, (MAX_FILE_BLOCKS - 1) * MFS_BLOCK_SIZE, MFS_BLOCK_SIZE)
      buf = gen_block(3)
      self.write(inum, buf, 0, MFS_BLOCK_SIZE)
      buf = gen_block(4)
      self.write(inum, buf, (MAX_FILE_BLOCKS - 1) * MFS_BLOCK_SIZE, MFS_BLOCK_SIZE)

      st = self.stat(inum)
      if st.type != MFS_REGULAR_FILE:
         raise Failure("Stat gave wrong type")
      if st.size != MAX_FILE_BLOCKS * MFS_BLOCK_SIZE:
         raise Failure("Stat gave wrong size")

      self.shutdown()
      self.server.wait()
      self.done()

test_list = [SparseTest, Stat2Test]

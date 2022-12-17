from ctypes import *
import os, time, random

import toolspath
from testing.test import Test, Failure
import subprocess

# root inode number
ROOT = 0

MFS_DIRECTORY = 0
MFS_REGULAR_FILE = 1
MFS_BLOCK_SIZE = 4096

MAX_INODES = 4096  # 32 from new test

MAX_FILE_BLOCKS = 30
MAX_FILES_PER_DIR = (MAX_FILE_BLOCKS * MFS_BLOCK_SIZE / 32) - 2  # 126 from new test

MAX_NAME_LEN = 27

BlockBuffer = c_char * MFS_BLOCK_SIZE
BlockBufferHello = c_char * 5 

class StatStruct(Structure):
   _fields_ = [("type", c_int), ("size", c_int)]

def bufs_equal(b1, b2):
   for i in range(0, MFS_BLOCK_SIZE):
      if b1[i] != b2[i]:
         return False
   return True

def gen_block(number):
   b = BlockBuffer()
   start = "START BLOCK " + str(number)
   end = "END BLOCK " + str(number)
   for i in range(len(start)):
      b[i] = start[i]
   for i in range(len(end)):
      b[-(i+1)] = end[-(i+1)]
   return b

class MfsTest(Test):

   library_functions = ["MFS_Init", "MFS_Lookup", "MFS_Stat", "MFS_Write",
         "MFS_Read", "MFS_Creat", "MFS_Unlink", "MFS_Shutdown"]
   server = None

   def loadlib(self):
      self.libmfs = cdll.LoadLibrary(self.project_path + "/libmfs.so")
      for func in self.library_functions:
         if not hasattr(self.libmfs, func):
            raise Failure("libmfs should export fucntion '" + func + "'")
      return self.libmfs

   def start_server(self, image = None, libs = None, port = None):
      os.system("killall server")
      if image is None:
         os.system("./mkfs -f test.img")
         image = "./test.img"
      minport = 5000
      maxport = 10000
      for i in range(5):
        if port != None:
          self.port = port
        else:
          self.port = random.randint(minport, maxport)
        self.log("Starting server on port " + str(self.port))
        self.server = self.startexe(["server", str(self.port), image], libs = libs)
        time.sleep(0.2)
        if (self.server.poll() != None):
          self.server.kill()
          self.server = None
        else:
          return
      raise Failure("Could not start server")

   def mfs_init(self, hostname, port):
      r = self.libmfs.MFS_Init(hostname, port)
      if r != 0:
         raise Failure("MFS_Init returned failure")
      return r

   def lookup(self, inum, name):
      r = self.libmfs.MFS_Lookup(inum, name)
      if r < 0:
         raise Failure("MFS_Lookup returned failure " +
               "inum=" + str(inum) + " name=" + repr(name))
      return r

   def write(self, inum, buf, block, nbyte):
      r = self.libmfs.MFS_Write(inum, byref(buf), block, nbyte)
      if r != 0:
         raise Failure("MFS_Write returned failure " +
               "inum=" + str(inum) + " block=" + str(block))

   def read(self, inum, buf, block, nbyte):
      r = self.libmfs.MFS_Read(inum, byref(buf), block, nbyte)
      if r != 0:
         raise Failure("MFS_Read returned failure " +
               "inum=" + str(inum) + " block=" + str(block))

   def read_and_check(self, inum, block, expected, nbyte):
      buf = BlockBuffer()
      self.read(inum, buf, block, nbyte)
      if not bufs_equal(buf, expected):
         raise Failure("Corrupt data returned by read")

   def creat(self, inum, type, name):
      r = self.libmfs.MFS_Creat(inum, type, name)
      if r != 0:
         raise Failure("MFS_Creat returned failure " +
               "inum=" + str(inum) + " type=" + str(type) + " name=" + repr(name))
      return r

   def stat(self, inum):
      st = StatStruct()
      r = self.libmfs.MFS_Stat(inum, byref(st))
      if r != 0:
         raise Failure("MFS_Stat returned failure inum=" + str(inum))
      return st

   def unlink(self, pinum, name):
      r = self.libmfs.MFS_Unlink(pinum, name)
      if r != 0:
         raise Failure("MFS_Unlink returned failure " +
               "pinum=" + str(pinum) + " name=" + repr(name))
      return r

   def shutdown(self):
      r = self.libmfs.MFS_Shutdown()
      if r != 0:
         raise Failure("MFS_Shutdown returned failure")
      return r


   def __getstate__(self):
      odict = self.__dict__.copy()
      if 'libmfs' in odict:
         del odict['libmfs']
      return odict

   def fail(self, reason = None):
      result = Test.fail(self, reason)
      self.terminate()
      return result

   def create_image(self):
      pwd = subprocess.check_output("pwd", shell=True);
      command = str(pwd).replace('\n', '') + "/mkfs -f test.img"
      os.system(command)
      image = str(pwd).replace('\n', '') + "/test.img"
      return image

   def create_image_max(self, num_data_blocks, num_inodes):
      pwd = subprocess.check_output("pwd", shell=True);
      command = str(pwd).replace('\n', '') + "/mkfs -f test.img -d %i -i %i" %(num_data_blocks, num_inodes)
      os.system(command)
      image = str(pwd).replace('\n', '') + "/test.img"
      return image

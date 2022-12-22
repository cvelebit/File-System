import superblock
import disk

import numpy as np

_inodes = None
_dnodes = None

def Init():
    global _inodes
    global _dnodes

    if _inodes is None:
        num = superblock.Read(3) # number of inodes
        byts = (num + 7) // 8
        #_inodes = np.array([b'\x01' for i in range(byts)], dtype = bytes)
        _inodes = bytearray(byts)


        num = superblock.Read(1) #number of data blocks
        byts = (num + 7) // 8
        #_dnodes = np.array([b'\x01' for i in range(byts)], dtype = bytes)
        _dnodes = bytearray(byts)

def Create():
    global _inodes
    global _dnodes

    _inodes = None
    Init()
    
    bytes_per_block = superblock.Read(7)
    inode_block = superblock.Read(6)
    pos = inode_block * bytes_per_block
    for i in _inodes:
        disk.WriteDisk(pos, i)
        pos += 1

    dnode_block = superblock.Read(5)
    pos = dnode_block * bytes_per_block
    for d in _dnodes:
        disk.WriteDisk(pos, d)
        pos += 1

def Load():
    global _dnodes
    global _inodes
    Init()

    bytes_per_block = superblock.Read(7)
    inode_block = superblock.Read(6)
    pos = inode_block * bytes_per_block
    for i in range(len(_inodes)):
        _inodes[i:i+1] = bytes(disk.ReadDisk(pos))
        pos += 1

    dnode_block = superblock.Read(5)
    pos = dnode_block * bytes_per_block
    for d in range(len(_dnodes)):
        _dnodes[d:d+1] = bytes(disk.ReadDisk(pos))
        pos += 1

def IsInodeValid(inode):
    global _inodes
    pos = inode // 8
    byt = bytes(_inodes[pos:pos+1])
    byt = int.from_bytes(byt, "big")
    bit = inode % 8
    bbb = 1 << bit
    r = byt & bbb
    return r != 0

def SetInodeValid(inode, value):
    global _inodes
    pos = inode // 8
    byt = bytes(_inodes[pos:pos+1])
    byt = int.from_bytes(byt, "big")
    bit = inode % 8
    bbb = 1 << bit
    if value:
        byt = byt | bbb
    else:
        byt = byt & ~bbb
    byt = byt.to_bytes(1, "big")
    _inodes[pos:pos+1] = byt

    bytes_per_block = superblock.Read(7)
    inode_block = superblock.Read(6)
    pos += inode_block * bytes_per_block
    disk.WriteDisk(pos, byt)

def GetInodeValid():
    for i in range(superblock.Read(3)):
        if not IsInodeValid(i):
            return i
    return False

def IsDnodeValid(dnode):
    global _dnodes
    pos = dnode // 8
    byt = bytes(_dnodes[pos:pos+1])
    #byt = int(byt.decode("utf-8"))
    byt = int.from_bytes(byt, "big")
    bit = dnode % 8
    bbb = 1 << bit
    r = byt & bbb
    return r != 0

def SetDnodeValid(dnode, value):
    global _dnodes
    pos = dnode // 8
    byt = bytes(_dnodes[pos:pos+1])
    #byt = int(byt.decode("utf-8"))
    byt = int.from_bytes(byt, "big")
    bit = dnode % 8
    bbb = 1 << bit
    if value:
        byt = byt | bbb
    else:
        byt = byt & ~bbb
    byt = byt.to_bytes(1, "big")
    _dnodes[pos:pos+1] = byt

    bytes_per_block = superblock.Read(7)
    dnode_block = superblock.Read(5)
    pos += dnode_block * bytes_per_block
    disk.WriteDisk(pos, byt)


def GetDnodeValid():
    for d in range(superblock.Read(1)):
        if not IsDnodeValid(d):
            return d
    return False
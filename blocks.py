#data blocks
import superblock
import disk

def _GetBlockPos(bid):
    databmp = superblock.Read(5)
    inodeStart = databmp +1
    num_inodes = superblock.Read(3) / superblock.Read(2)
    st = inodeStart + num_inodes
    st = superblock.Read(7) * (bid + st)
    return int(st)

def ReadIntBlock(bid, offset): #bid is block id, byte offset
    p = _GetBlockPos(bid) + offset
    return disk.ReadInt(p), offset + 4 #read value, and new offset for reading next int

def WriteIntBlock(bid, offset, value):
    p = _GetBlockPos(bid) + offset
    disk.WriteInt(p, value)
    return offset + 4

def ReadStringBlock(bid, offset):
    p = _GetBlockPos(bid)
    r = ""
    while True:
        c = disk.ReadDisk(p + offset)
        offset += 1
        if c == 0:
            break
        r += chr(c)
    return r, offset

def WriteStringBlock(bid, offset, value):
    p = _GetBlockPos(bid)
    o = 0
    while o < len(value):
        disk.WriteDisk(p + offset, ord(value[o]))
        offset += 1
        o+=1
    disk.WriteDisk(p + offset, 0)
    offset += 1
    return offset 
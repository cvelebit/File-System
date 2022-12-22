import disk
import superblock
import bmp

def GetInodeStart():
    databmp = superblock.Read(5)
    return databmp + 1

def _GetInodePos(inode):
    s = GetInodeStart()
    bytes_per_block = superblock.Read(7)
    s *= bytes_per_block
    inodes_per_block = superblock.Read(2)
    bytes_per_inode = bytes_per_block // inodes_per_block
    s += inode * bytes_per_inode
    return s

def _GetInode(inode):
    a = []
    s = _GetInodePos(inode)
    for i in range(8):
        v = disk.ReadInt(s)
        a.append(v)
        s+=4
    return a

def IsInodeValid(inode):
    n = _GetInode(inode)
    return n[0] != 0

def GetInodeType(inode):
    n = _GetInode(inode)
    return n[0]

def SetInodeValid(inode, value):
    p = _GetInodePos(inode)
    bmp.SetInodeValid(inode, value != 0)
    disk.WriteInt(p, value)

def ReadInodeSize(inode):
    n = _GetInode(inode)
    return n[1]

def WriteInodeSize(inode, value):
    p = _GetInodePos(inode)
    disk.WriteInt(p + 4, value)

def ReadDataNode(inode, offset, indirect=False): #if 0-4, then easy, otherwise have to get indirect node which is 0-5
    n = _GetInode(inode)
    if offset < 5:
        return n[offset+2]
    elif offset == 5 and indirect:
        return n[offset+2]
    else:
        return ReadDataNode(n[-1], offset-5, indirect=True)

def WriteDataNode(inode, offset, value, indirect=False):
    p = _GetInodePos(inode)
    if offset < 5:
        disk.WriteInt(p + ((2 + offset)*4), value)
    elif offset == 5 and indirect:
        disk.WriteInt(p + ((2 + offset)*4), value)
    else:
        n = _GetInode(inode)
        #find an invalid inode and set the current inode indirect entry to the new invalid inode
        if n[-1] != 0:
            return WriteDataNode(n[-1], offset-5, value, indirect=True)
        else:
            c = 1
            while True:
                n = _GetInode(inode+c)
                if n[0] != 0:
                    if inode+c == superblock.Read(3)-1:
                        c = -inode
                    else:
                        c+=1
                else:
                    p1 = _GetInodePos(inode)#set current inode indirect entry to new inode
                    disk.WriteInt(p1 + (7*4), inode+c)
                    p2 = _GetInodePos(inode+c)#set new inode to valid
                    disk.WriteInt(p2, 1)
                    return WriteDataNode(inode+c, offset-5, value, indirect=False)

def Create():
    inode_start_block = GetInodeStart()
    inode_block_count = superblock.Read(3)
    bytes_per_block = superblock.Read(7) #4096
    for i in range(inode_start_block, inode_start_block + inode_block_count):
        for j in range(0, bytes_per_block, 4):
            disk.WriteInt(i * bytes_per_block + j, 0)
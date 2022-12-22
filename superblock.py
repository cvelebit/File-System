import disk

# 0 - Magic Number
# 1 - Number of Blocks
# 2 - number of inodes per data block
# 3 - Number of inodes
# 4 - Directory inode
# 5 - Block nbr of Data bitmap
# 6 - Block nbr of Inode bitmap
# 7 - Block size in bytes

def Read(entry):
    return disk.ReadInt(entry * 4)

def Write(entry, value):
    disk.WriteInt(entry*4, value)

def Create():
    Write(0, 45055) # magic number - could be anything, basically id for type
    Write(1, 8) # number of data blocks
    Write(2, 16) # number of inodes per data block
    Write(3, 5*16) # number of inodes (5 inode blocks)
    Write(4, 0) # Directory inode is 0
    Write(5, 2) # Block nbr of Data bitmap
    Write(6, 1) # Block nbr of Inode bitmap
    Write(7, 4096) # Number of bytes per block

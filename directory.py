import inodes
import blocks
import bmp
#assume all inodes were intitialized
def CreateRoot():
    # root
    inode = 0
    dnode = 0
    inodes.SetInodeValid(inode, 2)
    inodes.WriteInodeSize(inode, 1)
    inodes.WriteDataNode(inode, 0, dnode)
    bmp.SetDnodeValid(dnode, True)
    size = 4 #calculates itself
    size = blocks.WriteIntBlock(dnode, size, inode)     #inode for current directory
    size = blocks.WriteStringBlock(dnode, size, "d.")    #value indicating current dir
    size = blocks.WriteIntBlock(dnode, size, 0)         #inode for previous directory
    size = blocks.WriteStringBlock(dnode, size, "d..")   #value indicating previous dir
    size = blocks.WriteIntBlock(dnode, size, 1)         #inode for etc directory
    size = blocks.WriteStringBlock(dnode, size, "detc")
    size = blocks.WriteIntBlock(dnode, size, 2)         #inode for bin directory
    size = blocks.WriteStringBlock(dnode, size, "dbin")
    blocks.WriteIntBlock(dnode, 0, size)

    # etc 
    inode = 1
    dnode = 1
    inodes.SetInodeValid(inode, 2)
    inodes.WriteInodeSize(inode, 1)
    inodes.WriteDataNode(inode, 0, dnode)
    bmp.SetDnodeValid(dnode, True)
    size = 4
    size = blocks.WriteIntBlock(dnode, size, inode)
    size = blocks.WriteStringBlock(dnode, size, "d.")
    size = blocks.WriteIntBlock(dnode, size, 0)
    size = blocks.WriteStringBlock(dnode, size, "d..")
    size = blocks.WriteIntBlock(dnode, size, 3)
    size = blocks.WriteStringBlock(dnode, size, "fdata.txt")
    blocks.WriteIntBlock(dnode, 0, size)

    # bin
    inode = 2
    dnode = 2
    inodes.SetInodeValid(inode, 2)
    inodes.WriteInodeSize(inode, 1)
    inodes.WriteDataNode(inode, 0, dnode)
    bmp.SetDnodeValid(dnode, True)
    size = 4
    size = blocks.WriteIntBlock(dnode, size, inode)
    size = blocks.WriteStringBlock(dnode, size, "d.")
    size = blocks.WriteIntBlock(dnode, size, 0)
    size = blocks.WriteStringBlock(dnode, size, "d..")
    blocks.WriteIntBlock(dnode, 0, size)

    # data.txt
    inode = 3
    dnode = 3
    bmp.SetDnodeValid(dnode, True)
    inodes.SetInodeValid(inode, 1)
    inodes.WriteInodeSize(inode, 1)
    inodes.WriteDataNode(inode, 0, dnode)
    size = 4
    size = blocks.WriteStringBlock(dnode, size, "Hello World!")
    blocks.WriteIntBlock(dnode, 0, size)



def GetFileType(inode):
    return inodes.GetInodeType(inode)

def GetFileData(inode): #assume everything we load is a string, normally have to worry about binary data
    blockCount = inodes.ReadInodeSize(inode)
    data = ""
    for i in range(blockCount):
        d = inodes.ReadDataNode(inode, i)
        s, o = blocks.ReadStringBlock(d, 4)
        data += s
    return data

def GetDirInfo(inode): #assume its a directory
    # filename: [inode, filetype]
    info = {}
    dnode = inodes.ReadDataNode(inode, 0)
    size, offset = blocks.ReadIntBlock(dnode, 0)
    while offset < size:
        inode, offset = blocks.ReadIntBlock(dnode, offset)
        filename, offset = blocks.ReadStringBlock(dnode, offset)
        if filename[0] == "d":
            filetype = 2
        else:
            filetype = 1
        info[filename[1:]] = [inode, filetype]
    return info

def GetInodeFromPath(inode, path):#new
    if len(path) <= 0:
        return None
    elif path[0] == '/':
        path = path[1:]
    dirs = path.split('/')
    for d in dirs:
        info = GetDirInfo(inode)
        if d not in info:
            return inode
        i = info[d]
        if i[1] == 1: #file
            return i[0]
        inode = i[0]
    return inode

def GetInodeFromPath1(inode, path):#old
    if len(path) <= 0:
        return None
    elif path[0] == '/':
        path = path[1:]
        inode = 0
    dirs = path.split('/')
    for d in dirs:
        info = GetDirInfo(inode)
        if d not in info:
            return None
        i = info[d]
        if i[1] == 1: #file type
            return i[0]
        inode = i[0]
    return inode

def AddDirectory(dirName, curDir):
    inode = bmp.GetInodeValid()
    dnode = bmp.GetDnodeValid()
    bmp.SetDnodeValid(dnode, True)
    inodes.SetInodeValid(inode, 2)
    inodes.WriteInodeSize(inode, 1)
    inodes.WriteDataNode(inode, 0, dnode)
    size = 4
    size = blocks.WriteIntBlock(dnode, size, inode)
    size = blocks.WriteStringBlock(dnode, size, "d.")
    size = blocks.WriteIntBlock(dnode, size, curDir)
    size = blocks.WriteStringBlock(dnode, size, "d..")
    blocks.WriteIntBlock(dnode, 0, size)
    
    #add new directory to parent directory
    c = 0
    while True:
        if inodes.ReadDataNode(curDir, c+1) == 0:
            p_dnode = inodes.ReadDataNode(curDir, c)
            break
        c+=1
    p_size, dump = blocks.ReadIntBlock(p_dnode, 0)
    p_size = blocks.WriteIntBlock(p_dnode, p_size, inode)
    p_size = blocks.WriteStringBlock(p_dnode, p_size, "d" + dirName)
    blocks.WriteIntBlock(p_dnode, 0, p_size)


def Remove(path, curDir, type):
    name = path.rsplit("/")[-1]
    p_path = "/" + path.rstrip("/" + name)
    p_inode = GetInodeFromPath(curDir, p_path)
    inode = GetInodeFromPath(curDir, path)
    if type == "directory":
        info = GetDirInfo(inode)
        if len(info) > 2:
            print("The directory is not empty.")
            return
        elif inode == curDir:
            print("Cannot remove current working directory.")
            return
    c = 0
    while True:
        if inodes.ReadDataNode(inode, c+1) == 0:
            dnode = inodes.ReadDataNode(inode, c)
            break
        c+=1
    bmp.SetInodeValid(inode, False)
    bmp.SetDnodeValid(dnode, False)
    p_dnode = inodes.ReadDataNode(p_inode, 0)
    total_dir = GetDirInfo(curDir)
    del total_dir[name]
    size = 4
    for dir in total_dir.keys():
        size = blocks.WriteIntBlock(p_dnode, size, total_dir[dir][0])
        if total_dir[dir][1] == 2:
            size = blocks.WriteStringBlock(p_dnode, size, "d" + dir)
        if total_dir[dir][1] == 1:
            size = blocks.WriteStringBlock(p_dnode, size, "f" + dir)
    blocks.WriteIntBlock(p_dnode, 0, size)

def AddFile(message, filename, curDir):
    filename = "f" + filename

    #make new file
    inode = bmp.GetInodeValid()
    dnode = bmp.GetDnodeValid()
    inodes.SetInodeValid(inode, 1)
    inodes.WriteInodeSize(inode, 1)
    inodes.WriteDataNode(inode, 0, dnode)
    bmp.SetDnodeValid(dnode, True)
    size = 4
    size = blocks.WriteStringBlock(dnode, size, message)
    blocks.WriteIntBlock(dnode, 0, size)

    #add new file to parent directory
    c = 0
    while True:
        if inodes.ReadDataNode(curDir, c+1) == 0:
            p_dnode = inodes.ReadDataNode(curDir, c)
            break
        c+=1
    p_size, dump = blocks.ReadIntBlock(p_dnode, 0)
    p_size = blocks.WriteIntBlock(p_dnode, p_size, inode)
    p_size = blocks.WriteStringBlock(p_dnode, p_size, filename)
    blocks.WriteIntBlock(p_dnode, 0, p_size)
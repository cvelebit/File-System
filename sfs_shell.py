from cmd import Cmd
import disk
import superblock
import inodes
import directory
import bmp
_CurDir = 0

class MyPrompt(Cmd):
    def do_exit(self, inp):
        disk.CloseDisk()
        print("Bye")
        return True

    # file sys
    def do_format(self, inp): #use 65536 - 64k
        if int(inp) < 1:
            return
        disk.NewDisk("filesys.bin", int(inp))
        print("Formatted: " + str(inp) + " bytes")
        disk.OpenDisk("filesys.bin")
        superblock.Create()
        bmp.Create()
        inodes.Create()
        directory.CreateRoot()


    def do_mount(self, inp):
        disk.OpenDisk("filesys.bin")
        bmp.Load()
        print("Mounted")
        
    # superblock - comment all
    
    #def do_createsb(self, inp):
        #superblock.Create()
        #print("Created Superblock")

    #def do_readsb(self, inp):
        #val =  superblock.Read(int(inp))
        #print("Value: " + str(val))

    #def do_writesb(self, inp):
        #tmp = str(inp).split(" ")
        #if len(tmp) != 2:
            #return
        #superblock.Write(int(tmp[0]), int(tmp[1]))
        #print("Wrote Superblock")
    

    #inodes - comment all

    #def do_initin(self, inp):
        #inodes.Create()
        #print("Initialized inodes")

    #def do_validin(self, inp):
        #r = inodes.IsInodeValid(int(inp))
        #print("Valid" if r else "Invalid")

    #def do_newin(self, inp):
        #inodes.SetInodeValid(int(inp), True)
        #inodes.WriteInodeSize(int(inp), 0)
        #print("New Inode Created: " + str(inp))

    #def do_clearin(self, inp):
        #inodes.SetInodeValid(int(inp), False)
        #print("Inode Deleted: " + str(inp))
        
    #def do_addindb(self, inp): #inode, db index
        #tmp = str(inp).split(' ')
        #if len(tmp) != 2:
            #return
        #tmp[0] = int(tmp[0])
        #tmp[1] = int(tmp[1])
        #size = inodes.ReadInodeSize(tmp[0])
        #inodes.WriteDataNode(tmp[0], size, tmp[1])
        #size+=1
        #inodes.WriteInodeSize(tmp[0], size)
        #print("Datablock (" + str(tmp[1]) + ") added to Inode: " + str(tmp[0]))
        #print("New Inode size: " + str(size))
        
    #def do_readindb(self, inp): #inode, db index
        #tmp = str(inp).split(" ")
        #if len(tmp) != 2:
            #return
        #tmp[0] = int(tmp[0])
        #tmp[1] = int(tmp[1])
        #r = inodes.ReadDataNode(tmp[0], tmp[1])
        #print("Inode "+ str(tmp[0]) +" Datablock Index " + str(tmp[1]) + " = " + str(r))

    #def do_setindb(self, inp):
        #tmp = str(inp).split(" ")
        #if len(tmp) != 3:
            #return
        #tmp[0] = int(tmp[0])
        #tmp[1] = int(tmp[1])
        #tmp[2] = int(tmp[2])
        #inodes.WriteDataNode(tmp[0], tmp[1], tmp[2])
        #print("Set Inode "+ str(tmp[0]) +" Datablock Index " + str(tmp[1]) + " => " + str(tmp[2]))
    
    #def do_readinsize(self, inp):
        #s = inodes.ReadInodeSize(int(inp))
        #print("Inode size: " + str(s))
    
    #directory - comment out create root
    #def do_createroot(self, inp):
        #directory.CreateRoot()
        #print("Root Directory Created")

    def do_ls(self, inp):
        info = directory.GetDirInfo(_CurDir)
        lst = list(info.keys())
        lst.sort()
        print(*lst)
    
    def do_cwd(self, inp):
        global _CurDir
        curDir = _CurDir
        dir = ""
        while True:
            prevDir = directory.GetInodeFromPath(curDir, "..")
            info = directory.GetDirInfo(prevDir)
            for k in list(info.keys())[2:]:
                if info[k][0] == curDir:
                    dir = "/" + k + dir
                    break
            if prevDir <= 0:
                print("/" + dir[1:])
                return
            else:
                curDir = prevDir

    def do_cd(self, inp): #change directory
        global _CurDir
        r = directory.GetInodeFromPath(_CurDir, inp)
        if r is not None:
            _CurDir = r
            self.do_cwd(None)

    def do_mkdir(self, inp):
        global _CurDir
        directory.AddDirectory(inp,_CurDir)
        self.do_ls(None)

    def do_cat(self, inp):
        r = directory.GetInodeFromPath(_CurDir, inp)
        if r is not None:
            t = inodes.GetInodeType(r)
            if t == 1:
                s = directory.GetFileData(r)
                print(s)

    def do_rmdir(self, inp):
        global _CurDir
        directory.Remove(inp, _CurDir, "directory")
        self.do_ls(None)

    def do_rm(self, inp):
        global _CurDir
        directory.Remove(inp, _CurDir, "file")
        self.do_ls(None)

    def do_echo(self, inp):
        global _CurDir
        if ">" in inp:
            message, filename = inp.split(" > ")
            directory.AddFile(message, filename, _CurDir)
            print(message)
        else:
            print(inp)


p = MyPrompt()
p.cmdloop()
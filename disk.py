#https://code-maven.com/interactive-shell-with-cmd-in-python
_CurrentFile = None
_CurrentFileSize = 0

def NewDisk(name, size):
    global _CurrentFile
    _CurrentFile = open(name, 'wb+')
    if _CurrentFile != None:
        # Set the file size to the max size with the first 4 bytes
        lst = [(size >> 24) & 0xFF, (size >> 16) & 0xFF, (size >> 8) & 0xFF, size & 0xFF]
        _CurrentFile.write(bytes(lst))
        for i in range(size):
            _CurrentFile.write(b'\x00')
        _CurrentFile.close()
        OpenDisk(name)

def OpenDisk(name):
    global _CurrentFile
    global _CurrentFileSize
    _CurrentFile = open(name, 'rb+')
    # Get the current file size - big endien order of bytes
    _CurrentFileSize = int.from_bytes(_CurrentFile.read(4), "big")# << 24 #changed read(1) to read(4)
    #_CurrentFileSize += int.from_bytes(_CurrentFile.read(1), "big") << 16
    #_CurrentFileSize += int.from_bytes(_CurrentFile.read(1), "big") << 8
    #_CurrentFileSize += int.from_bytes(_CurrentFile.read(1), "big")

def CloseDisk():
    global _CurrentFile
    _CurrentFile.close()

def WriteDisk(position, value):
    global _CurrentFile
    global _CurrentFileSize
    if not isinstance(value, int):
        return
    if value < 0 or value > 255: # Write only 1 byte
        return
    if not isinstance(position, int):
        return
    if position < 0 or position >= _CurrentFileSize:
        return
    _CurrentFile.seek(position+4) # all positions are +4 because the first 4 bytes is the header size
    _CurrentFile.write(bytes([value]))
    _CurrentFile.flush()

def ReadDisk(position):
    global _CurrentFile
    global _CurrentFileSize
    if not isinstance(position, int):
        return
    if position < 0 or position >= _CurrentFileSize:
        return
    _CurrentFile.seek(position+4) # all positions are +4 because the first 4 bytes is the header size
    value = int.from_bytes(_CurrentFile.read(1), "big")
    return value

def ReadInt(position):
    global _CurrentFile
    global _CurrentFileSize
    if not isinstance(position, int):
        return
    if position < 0 or position >= _CurrentFileSize:
        return
    _CurrentFile.seek(position+4) # all positions are +4 because the first 4 bytes is the header size
    value = int.from_bytes(_CurrentFile.read(4), "big")
    return value

def WriteInt(position, value):
    global _CurrentFile
    global _CurrentFileSize
    if not isinstance(value, int):
        return
    if value < 0 or value > 255*255*255*255: # Write only 4 byte
        return
    if not isinstance(position, int):
        return
    if position < 0 or position >= _CurrentFileSize - 3:
        return
    _CurrentFile.seek(position+4) # all positions are +4 because the first 4 bytes is the header size
    _CurrentFile.write(int.to_bytes(value, 4, "big", signed=False))
    _CurrentFile.flush()

##Test Code
#NewDisk("test.bin", 16)
#WriteDisk(0, 100)
#print(str(ReadDisk(0)))
#CloseDisk()





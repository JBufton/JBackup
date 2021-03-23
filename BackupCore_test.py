from tempfile import TemporaryDirectory
from os.path import join, isfile
from os import listdir
from random import randint, choice
from string import ascii_letters
from BackupCore import JBackup_Core
from pprint import pprint

def setupFiles(_numberOfFiles, _location):
    for i in range( _numberOfFiles ):
        tempFile = open( join(_location, f"{i}.txt"), "w" )
        lines = randint(1,30)
        for line in range(lines):
            length = randint(1,50)
            tempFile.write( ''.join(choice(ascii_letters) for i in range(length)) + "\n" )

def changeFiles( _location, _addFileLength ):
    for testFile in [i for i in listdir(_location) if isfile(i)]:
        testFileObject = open( join(_location, testFile), "r" )
        testFileContents = testFileObject.readlines()
        testFileObject.close()
        index = 0
        while index <= len(testFileContents):
            if randint(0,1):
                # Delete the line
                del testFileContents[index]
                index -= 1
            elif randint(0,1):
                # insert a new line
                testFileContents.insert( index, ''.join(choice(ascii_letters) for i in range(_addFileLength)) + "\n" )
        testFileObject = open( join(_location, testFile), "w" )
        testFileObject.write(''.join(testFileContents))



class TestBackupCore:

    def test_10ChangeRoundtrip(self):
        with TemporaryDirectory() as tempFiles:
            with TemporaryDirectory() as tempBackups:
                with TemporaryDirectory() as tempRestore:
                    setupFiles(10, tempFiles)
                    JBackup = JBackup_Core()
                    JBackup.m_backupPath = tempBackups
                    JBackup.UpdateBackup(_newPaths=[tempFiles])
                    assert len(listdir(tempBackups)) == 1
                    changeFiles(tempFiles, 30)
                    JBackup.UpdateBackup()
                    assert len(listdir(tempBackups)) == 2
                    changeFiles(tempFiles, 30)
                    JBackup.UpdateBackup()
                    assert len(listdir(tempBackups)) == 3
                    JBackup.RebuildFiles(tempRestore)
                    # Now test recreated files match
                    for tempFile_Original in [join(tempFiles, i) for i in listdir(tempFiles)]:
                        with open(tempFile_Original, "r") as originalFile:
                            originalFileContents = originalFile.readlines()
                            with open(join(tempRestore, tempFile_Original.replace(":", "")), "r") as recreatedFile:
                                recreatedFileContents = recreatedFile.readlines()
                                assert originalFileContents == recreatedFileContents
                                pprint(originalFileContents)
                                pprint(recreatedFileContents)
                                print( f"{tempFile_Original} == {join(tempRestore, tempFile_Original.replace(':', ''))}")


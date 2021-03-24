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

    # I want this test to do the following:
    # Generate 10 files with random content
    # Use JBackup to back these files up
    # Edit the files contents twice and backing up after each change
    # Make sure after each backup that there has been a new backup file saved
    # Use JBackup to restore the files
    # Compare the current actual files with their restored counterparts
    def test_10ChangeRoundtrip(self):
        # Create all the temporary directories we need
        with TemporaryDirectory() as tempFiles:
            with TemporaryDirectory() as tempBackups:
                with TemporaryDirectory() as tempRestore:
                    # Create the files
                    setupFiles(10, tempFiles)
                    # Setup JBackup and create initial backup
                    JBackup = JBackup_Core()
                    JBackup.m_backupPath = tempBackups
                    JBackup.UpdateBackup(_newPaths=[tempFiles])
                    # Check a backup has been made
                    assert len(listdir(tempBackups)) == 1
                    # Change and backup the files twice making sure that backup files have been made each time
                    changeFiles(tempFiles, 30)
                    JBackup.UpdateBackup()
                    assert len(listdir(tempBackups)) == 2
                    changeFiles(tempFiles, 30)
                    JBackup.UpdateBackup()
                    assert len(listdir(tempBackups)) == 3
                    JBackup.RebuildFiles(tempRestore)
                    # Now test recreated files match the originals
                    for tempFile_Original in [join(tempFiles, i) for i in listdir(tempFiles)]:
                        # Get the original files contents
                        with open(tempFile_Original, "r") as originalFile:
                            originalFileContents = originalFile.readlines()
                            # Get the restored files contents
                            with open(join(tempRestore, tempFile_Original.replace(":", "")), "r") as recreatedFile:
                                recreatedFileContents = recreatedFile.readlines()
                                # Compare
                                assert originalFileContents == recreatedFileContents
                                pprint(originalFileContents)
                                pprint(recreatedFileContents)
                                print( f"{tempFile_Original} == {join(tempRestore, tempFile_Original.replace(':', ''))}")


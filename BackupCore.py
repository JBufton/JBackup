from os.path import isdir, getmtime, join
from os import walk, listdir
from datetime import datetime
import pickle

class JBackup_Core:

    def __init__(self):
        # List of paths of all of the files and folders wanted for backup
        self.m_paths = []
        # Location of where to store backup
        self.m_backupPath = ""
        # The list of files in the backup and their current states aswell as other information about the current backup
        self.m_currentBackupState = {}

    # Function to set m_currentBackupState to a specific date or latest if _date set to default
    def GetBackupState(self, _date=None):
        if _date == None:
            self.m_currentBackupState["latest"] = True
            _date = datetime.now()
        else:
            self.m_currentBackupState["latest"] = False
        # First get the list of backup files in order
        files = sorted([f for f in listdir(self.m_backupPath) if ".pkl" in f])
        # Go through all the files in order
        for i in range(0, len(files) ):
            updateDict = pickle.load( open(join(self.m_backupPath, files[i]), "rb") )
            # Check to see if we need to add these changes
            if updateDict["ctime"] <= _date:
                self.m_currentBackupState["ctime"] = updateDict["ctime"]
                for updateFile in updateDict["files"].keys():
                    # Check if the current update file is in the current backup state
                    if updateFile in self.m_currentBackupState["files"].keys():
                        self.m_currentBackupState["files"][updateFile]["mtime"] = updateDict["files"][updateFile]["mtime"]
                        self.m_currentBackupState["files"][updatefile]["changes"].append( updateDict["files"][updateFile]["changes"] )
                    else:
                        self.m_currentBackupState["files"][updateFile] = {}
                        self.m_currentBackupState["files"][updateFile]["mtime"] = updateDict["files"][updateFile]["mtime"]
                        self.m_currentBackupState["files"][updatefile]["changes"] = [ updateDict["files"][updateFile]["changes"] ]
            else:
                # We don't want to apply this update because it is after the date we want to sync to
                return self.m_currentBackupState

    # Function to back if a file is updated vs the latest file
    def isFileUpdated(self, _path ):
        # First check if the current backup state is the latest
        if not self.m_currentBackupState["latest"]:
            self.GetBackupState()
        if _path in self.m_currentBackupState["files"].keys():
            # The file already exists in the backup
            if getmtime( _path ) > self.m_currentBackupState["files"][_path]["mtime"]:
                return True
            else:
                return False
        else:
            # The file is new and so is updated by default
            return True

    # Function that given a file path gets the contents of the latest backed up version of that file as a list of lines
    def GetCurrentVersionOfFile(self, _path):
        if _path in self.m_currentBackupState["files"].keys():
            fileContents = ""
            # Cycle through changes saved
            for change in self.m_currentBackupState["files"][_path]["changes"]:
                # Change is replacing the whole file, normally only made if the file doesn't exist previously
                if change["type"] == "wholeFile":
                    fileContents = change["content"]
                # Change is deleting a line at a specific index
                elif change["type"] == "deleteLine":
                    splitFileContents = fileContents.split("\n")
                    del splitFileContents[ change['lineNumber'] ]
                    fileContents = splitFileContents.join("\n")
                # Change is adding in a line at a specific index
                elif change["type"] == "addLine":
                    splitFileContents = fileContents.split("\n")
                    splitFileContents.insert( change["lineNumber"], change["content"] )
                    fileContents = splitFileContents.join("\n")
            return fileContents.splitlines("\n")
        else:
            return None


    # Function to find the differences between two files and return a list detailing those changes
    def GetFileChanges( self, _newFile ):
        newfileObject = open( _newFile, "r" )
        newFileContents = newfileObject.readlines()
        oldFileContents = self.GetCurrentVersionOfFile( _newFile )
        changes = {}
        # First check if there is no old file. Add the whole file if it didn't exist previously
        if oldFileContents == None:
            changes = {
                "type": "wholeFile",
                "content": _newFile
            }
            return changes
        
        # Cycle through the old file and compare it to the new one
        for line in oldFileContents:
            continue
        return changes


    # Function that returns a dictionary for the changes to a file vs the files currently backed up state
    def BackupFile( self, _path ):
        fileUpdate = {
            "mtime": getmtime( _path ),
            "changes": self.GetFileChanges( _path )
        }

        return fileUpdate

    # Function to recursively find all of the files changed in m_paths
    def UpdateBackup(self):
        updateChanges = {
            "ctime": datetime.now(),
            "files": {}
        }

        for path in self.m_paths:
            if isdir(path):
                # Walk the directory tree
                for root, dirs, files in os.walk( path ):
                    for filePath in [join(root, f) for f in files]:
                        if self.isFileUpdated( filePath ):
                            updateChanges["files"][filePath] = self.BackupFile( _path )
            else:
                if self.isFileUpdated( path ):
                    updateChanges["files"][path] = self.BackupFile( path )

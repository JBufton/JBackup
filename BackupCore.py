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
                        self.m_currentBackupState["files"][updatefile]["changes"].append( updateDict["files"][updateFile]["change"] )
                    else:
                        self.m_currentBackupState["files"][updateFile] = {}
                        self.m_currentBackupState["files"][updateFile]["mtime"] = updateDict["files"][updateFile]["mtime"]
                        self.m_currentBackupState["files"][updatefile]["changes"] = [ updateDict["files"][updateFile]["change"] ]
            else:
                # We don't want to apply this update because it is after the date we want to sync to
                return self.m_currentBackupState

    # Function to back if a file is updated vs the latest file
    def isFileUpdated(self, _path ):
        if _path in self.m_currentBackupState["files"].keys():
            # The file already exists in the backup
            if getmtime( _path ) > self.m_currentBackupState["files"][_path]["mtime"]:
                return True
            else:
                return False
        else:
            # The file is new and so is updated by default
            return True

    # Function to recursively find all of the files changed in m_paths
    def UpdateBackup(self):
        for path in self.m_paths:
            if isdir(path):
                # Walk the directory tree
                for root, dirs, files in os.walk( path ):
                    for filePath in [join(root, f) for f in files]:
                        if self.isFileUpdated( filePath ):
                            # TODO self.BackupFile( filePath )
            else:
                if self.isFileUpdated( path ):
                    # TODO self.BackupFile( path )

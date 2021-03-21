from os.path import isdir, getmtime, join
from os import walk

class JBackup_Core:

    def __init__(self):
        # List of paths of all of the files and folders wanted for backup
        self.m_paths = []
        # Location of where to store backup
        self.m_backupPath = ""
        # The list of files in the backup and their current states
        self.m_currentBackupState = {}

    def isFileUpdated( _path ):
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
        changedFiles = []
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

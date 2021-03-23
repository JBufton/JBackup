from os.path import isdir, getmtime, join, exists, dirname, expanduser
from os import walk, listdir, makedirs
from datetime import datetime
from Differ import JDiffer
from platform import system
import pickle
import argparse

class JBackup_Core:

    def __init__(self):
        # Location of where to store backup
        self.m_backupPath = ""
        # The list of files in the backup and their current states aswell as other information about the current backup
        self.m_currentBackupState = {
            "latest": False,
            "ctime": None,
            "backupPaths": [],
            "files":{}
        }

    # Function to set m_currentBackupState to a specific date or latest if _date set to default
    def GetBackupState( self, _date=None ):
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
                self.m_currentBackupState["backupPaths"] += updateDict["backupPaths"]
                for updateFile in updateDict["files"].keys():
                    # Check if the current update file is in the current backup state
                    if updateFile in self.m_currentBackupState["files"].keys():
                        self.m_currentBackupState["files"][updateFile]["mtime"] = updateDict["files"][updateFile]["mtime"]
                        self.m_currentBackupState["files"][updateFile]["changes"].extend(updateDict["files"][updateFile]["changes"])
                    else:
                        self.m_currentBackupState["files"][updateFile] = {}
                        self.m_currentBackupState["files"][updateFile]["mtime"] = updateDict["files"][updateFile]["mtime"]
                        self.m_currentBackupState["files"][updateFile]["changes"] = updateDict["files"][updateFile]["changes"]
            else:
                # We don't want to apply this update because it is after the date we want to sync to
                return self.m_currentBackupState

    # Function to back if a file is updated vs the latest file
    def isFileUpdated( self, _path ):
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
    def ReBuildFileFromBackup( self, _path):
        if _path in self.m_currentBackupState["files"].keys():
            fileContents = []
            # Cycle through changes saved
            for change in self.m_currentBackupState["files"][_path]["changes"]:
                print(change)
                print(type(fileContents))
                # Change is replacing the whole file, normally only made if the file doesn't exist previously
                if change["type"] == "wholeFile":
                    fileContents = change["content"]
                # Change is deleting a line at a specific index
                elif change["type"] == "deleteLine":
                    del fileContents[ change['lineNumber'] ]
                # Change is adding in a line at a specific index
                elif change["type"] == "addLine":
                    fileContents.insert( change["lineNumber"], change["content"] )
                elif change["type"] == "appendLine":
                    fileContents.append( change["content"] )
            return fileContents
        else:
            return None


    # Function to generate all of the files that are backed up to the desired location
    def RebuildFiles( self, _outputDir ):
        print("Rebuilding Files")
        if not exists( _outputDir ):
            makedirs( _outputDir )
        for rebuildFile in self.m_currentBackupState["files"].keys():
            rebuildFilePath = rebuildFile
            if system() == "Windows":
                # We need to remove the : from the path
                rebuildFilePath = rebuildFile.replace(":","")
            pathToOutputFile = join( _outputDir, rebuildFilePath )
            print(f"Rebuilding: {pathToOutputFile}")
            if not exists( dirname( pathToOutputFile ) ):
                makedirs( dirname( pathToOutputFile ) )
            fileContents = self.ReBuildFileFromBackup( rebuildFile )
            print(fileContents)
            with open( pathToOutputFile, "w" ) as outputRebuildFile:
                outputRebuildFile.write( "".join(fileContents) )



    # Function to find the differences between two files and return a list detailing those changes
    def DiffFiles( self, _oldFile, _newFile ):
        # First we need to read the content of the file
        newfileObject = open( _newFile, "r" )
        newFileContents = newfileObject.readlines()
        changes = []
        # First check if there is no old file. Add the whole file if it didn't exist previously
        if _oldFile == None:
            changes.append({
                "type": "wholeFile",
                "content": newFileContents
            })
            return changes
        else:
            Differ = JDiffer( "custom" )
            changes = Differ.Diff( _oldFile, newFileContents )
        return changes


    # Function that returns a dictionary for the changes to a file vs the files currently backed up state
    def BackupFile( self, _path ):
        fileUpdate = {
            "mtime": getmtime( _path ),
            "changes": self.DiffFiles( self.ReBuildFileFromBackup( _path ), _path )
        }

        return fileUpdate

    # Function to recursively find all of the files changed in m_paths
    def UpdateBackup( self, _newPaths=[] ):
        # This will only work on the latest files so we need to update the backup state to latest
        self.GetBackupState()
        updateChanges = {
            "ctime": datetime.now(),
            "files": {},
            "backupPaths": _newPaths
        }

        backupPaths = self.m_currentBackupState['backupPaths'] + updateChanges["backupPaths"]

        for path in backupPaths:
            if isdir(path):
                # Walk the directory tree
                for root, dirs, files in walk( path ):
                    for filePath in [join(root, f) for f in files]:
                        if self.isFileUpdated( filePath ):
                            updateChanges["files"][filePath] = self.BackupFile( path )
            else:
                if self.isFileUpdated( path ):
                    updateChanges["files"][path] = self.BackupFile( path )
        
        updateVersionNumber = str(len( [i for i in listdir( self.m_backupPath ) if ".pkl" in i] ) + 1)
        pickleFileName = f"{updateVersionNumber}.pkl"
        # Write out the new update
        pickle.dump( updateChanges, open( join( self.m_backupPath, pickleFileName ), "wb" ) )
        # Now we have written the update lets get the latest backup state to load those changes into the current backup state
        self.GetBackupState()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--makeBackup", default=False ,action="store_true", help="Use this flag to make JBackup generate a backup")
    parser.add_argument("--backupsLocation", nargs="?", default="Default", type=str, help="Use this flag to determine where you want the backup to be made")
    parser.add_argument("--addBackupPaths", nargs="*", default=[], help="Use this flag to add files or folders to a new backup")
    parser.add_argument("--restore", default=False, action="store_true", help="Use this flag to restore the backups")
    parser.add_argument("--restoreDate", nargs="?", default="Latest", type=str, help="Use this flag in conjunction with --restore to choose the date to which to restore the files")
    parser.add_argument("--restoreLocation", nargs="?", default="Default", help="Use this flag to determine the location of the restored files when used in conjunction with --restore")
    args = parser.parse_args()

    restoreLocation = args.restoreLocation
    if args.restoreLocation == "Default":
        restoreLocation = join( expanduser("~"), "JBackup", "Restore" )
        if not exists(restoreLocation):
            makedirs(restoreLocation)

    backupsLocation = args.backupsLocation
    if args.backupsLocation == "Default":
        backupsLocation = join( expanduser("~"), "JBackup", "Backups" )
        if not exists(backupsLocation):
            makedirs(backupsLocation)
    
    JBackup = JBackup_Core()
    JBackup.m_backupPath = backupsLocation

    if args.makeBackup:
        JBackup.UpdateBackup(_newPaths=args.addBackupPaths)
    elif args.restore:
        if args.restoreDate == "Latest":
            JBackup.GetBackupState()
        else:
            # TODO somehow need to convert users input date to datetime date
            JBackup.GetBackupState()
        JBackup.RebuildFiles(_outputDir=restoreLocation)
from os.path import isdir, getmtime, join, exists, dirname, expanduser
from os import walk, listdir, makedirs
from datetime import datetime
from Differ import JDiffer
from platform import system
import pickle
import argparse

class JBackup_Core:

    def __init__(self, _backupPath="", _restoreLocation=""):
        self.m_defaultsLocation = join(dirname(__file__), "defaults.pkl")
        defaults = self.GetDefaults()
        if defaults:
            self.m_backupPath = defaults["backupPath"]
            self.m_restorePath = defaults["restorePath"]
        else:
            self.m_backupPath = join( expanduser("~"), "JBackup", "Backups" )
            self.m_restorePath = join( expanduser("~"), "JBackup", "Restore" )
        if _backupPath:
            self.m_backupPath = _backupPath
        if _restoreLocation:
            self.m_restorePath = _restoreLocation
        # The list of files in the backup and their current states aswell as other information about the current backup
        self.m_currentBackupState = {
            "latest": False,
            "ctime": None,
            "backupPaths": set(),
            "files":{}
        }

    '''Function to check if a defaults file exists and load it'''
    def GetDefaults( self ):
        if exists(self.m_defaultsLocation):
            defaults = pickle.load(open(self.m_defaultsLocation, "rb"))
            return defaults
        else:
            return None
    
    def SaveDefaults( self ):
        defaults = {
            "backupPath": self.m_backupPath,
            "restorePath": self.m_restorePath
        }

        pickle.dump( defaults, open(self.m_defaultsLocation, "wb")  )

    '''Function to return a list of backups and their date/times'''
    def GetListOfBackups( self ):
        files = sorted([f for f in listdir(self.m_backupPath) if ".pkl" in f])
        backupFiles = []
        for updateFile in files:
            backupDict = pickle.load( open(join(self.m_backupPath, updateFile), "rb") )
            backupFiles.append(
                {
                    "date": backupDict["ctime_date"],
                    "time": backupDict["ctime_time"],
                    # A combined datetime number to sort by
                    "datetime": int(backupDict["ctime_date"] + backupDict["ctime_time"]),
                    "files": backupDict["files"].keys()
                }
            )
        return sorted(backupFiles, key=lambda k: k['datetime'])

    '''Function to set m_currentBackupState to a specific date or latest if _date set to default'''
    def GetBackupState( self, _date=None, _time=None ):
        if _date == None and _time == None:
            self.m_currentBackupState["latest"] = True
            _date = datetime.now().date().strftime("%d/%m/%Y")
            _time = datetime.now().time().strftime("%H/%M/%S")
        else:
            self.m_currentBackupState["latest"] = False
        # We need to formate the date and time into YMD and HMS
        formattedDate = datetime.strptime(_date, "%d/%m/%Y").strftime("%Y%m%d")
        formattedTime = datetime.strptime(_time, "%H/%M/%S").strftime("%H%M%S")
        
        # First get the list of backup files in order
        files = sorted([f for f in listdir(self.m_backupPath) if ".pkl" in f])
        # Go through all the files in order
        for i in range(0, len(files) ):
            updateDict = pickle.load( open(join(self.m_backupPath, files[i]), "rb") )
            # Check to see if we need to add these changes
            if updateDict["ctime_date"] <= formattedDate:
                if updateDict["ctime_time"] <= formattedTime:
                    self.m_currentBackupState["ctime_date"] = updateDict["ctime_date"]
                    self.m_currentBackupState["ctime_time"] = updateDict["ctime_time"]
                    self.m_currentBackupState["backupPaths"].update( updateDict["backupPaths"] )
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

    '''Function to check if a file is different vs the latest file'''
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

    '''Function that given a file path gets the contents of the latest backed up version of that file as a list of lines'''
    def ReBuildFileFromBackup( self, _path):
        if _path in self.m_currentBackupState["files"].keys():
            # We're working forward through time so first change will always be a whileFile change
            fileContents = []
            # Cycle through changes saved
            for change in self.m_currentBackupState["files"][_path]["changes"]:
                # Change is replacing the whole file, normally only made if the file doesn't exist previously
                if change["type"] == "wholeFile":
                    fileContents = change["content"]
                # Change is deleting a line at a specific index
                elif change["type"] == "deleteLine":
                    del fileContents[ change['lineNumber'] ]
                # Change is adding in a line at a specific index
                elif change["type"] == "addLine":
                    fileContents.insert( change["lineNumber"], change["content"] )
                # Change is appending a line to the end of the file
                elif change["type"] == "appendLine":
                    fileContents.append( change["content"] )
            return fileContents
        else:
            return None


    '''Function to generate all of the files that are backed up to the desired location
    pretty much recursively use RebuildFileFromBackup()'''
    def RebuildFiles( self, _outputDir=None ):
        if not _outputDir:
            _outputDir = self.m_restorePath
        print("Rebuilding Files")
        # Make sure the output location exists
        if not exists( _outputDir ):
            makedirs( _outputDir )
        # We don't necessarily want to restore to the last version to use the backup state we already have
        for rebuildFile in self.m_currentBackupState["files"].keys():
            # Make a copy of the path incase we need to edit it for windows 
            rebuildFilePath = rebuildFile
            if system() == "Windows":
                # We need to remove the : from the drive part of the path
                rebuildFilePath = rebuildFile.replace(":","")
            pathToOutputFile = join( _outputDir, rebuildFilePath )
            print(f"Rebuilding: {pathToOutputFile}")
            # Make sure the folder structure is already in place where we are putting the restored file
            if not exists( dirname( pathToOutputFile ) ):
                makedirs( dirname( pathToOutputFile ) )
            # Get the file contents and write it out
            fileContents = self.ReBuildFileFromBackup( rebuildFile )
            with open( pathToOutputFile, "w" ) as outputRebuildFile:
                outputRebuildFile.write( "".join(fileContents) )



    '''Function to find the differences between two files and return a list detailing those changes'''
    def DiffFiles( self, _oldFile, _newFile ):
        changes = []
        # First check if there is no old file. Add the whole file if it didn't exist previously, no need to diff
        if _oldFile == None:
            changes.append({
                "type": "wholeFile",
                "content": _newFile
            })
            return changes
        else:
            # Choose a differ and get the changes
            Differ = JDiffer( "difflib" )
            changes = Differ.Diff( _oldFile, _newFile )
        return changes


    '''Function that returns a dictionary for the changes to a file vs the files currently backed up state'''
    def BackupFile( self, _path ):
        # First we need to read the content of the file
        fileObject = open( _path, "r" )
        fileContents = fileObject.readlines()
        # This will be the contents describing the changes from the previous file state to the current
        fileUpdate = {
            "mtime": getmtime( _path ),
            # Rebuild the currently backed up version of the file and then diff it against what is already there
            "changes": self.DiffFiles( self.ReBuildFileFromBackup( _path ), fileContents )
        }

        return fileUpdate

    '''Function to recursively find all of the files changed in m_paths'''
    def UpdateBackup( self, _newPaths=[] ):
        # This will only work on the latest files so we need to update the backup state to latest
        self.GetBackupState()
        # Default change dict
        updateChanges = {
            "ctime_date": datetime.now().date().strftime("%Y%m%d"),
            "ctime_time": datetime.now().time().strftime("%H%M%S"),
            "files": {},
            "backupPaths": set(_newPaths)
        }
        # We've already added the new backup paths (if any) to the updateChanges dict but
        # we want to go through all new and existing backup paths
        backupPaths = self.m_currentBackupState['backupPaths'].union(updateChanges["backupPaths"])
        for path in backupPaths:
            # If the path is a file we back that up, if it is a folder we recursively go through and back up all files
            if isdir(path):
                # Walk the directory tree
                for root, dirs, files in walk( path ):
                    for filePath in [join(root, f) for f in files]:
                        # Check if the file needs backing up
                        if self.isFileUpdated( filePath ):
                            updateChanges["files"][filePath] = self.BackupFile( filePath )
            else:
                # Check if the file needs backing up
                if self.isFileUpdated( path ):
                    updateChanges["files"][path] = self.BackupFile( path )
        
        updateVersionNumber = str(len( [i for i in listdir( self.m_backupPath ) if ".pkl" in i] ) + 1)
        pickleFileName = f"{updateVersionNumber}.pkl"
        # Write out the new update
        pickle.dump( updateChanges, open( join( self.m_backupPath, pickleFileName ), "wb" ) )
        # Now we have written the update lets get the latest backup state to load those changes into the current backup state
        self.GetBackupState()

'''Function to print a list of backups nicely'''
def PrintBackupList( _backupList ):
    spacesBetweenItems = 30
    for backup in _backupList:
        print( f"{backup['date'][6:]}-{backup['date'][4:6]}-{backup['date'][:4]}".ljust(spacesBetweenItems), end='' )
        print( f"{backup['time'][:2]}-{backup['time'][2:4]}-{backup['time'][4:]}".ljust(spacesBetweenItems) )

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--makeBackup", default=False ,action="store_true", help="Use this flag to make JBackup generate a backup")
    parser.add_argument("--backupsLocation", nargs="?", default="", type=str, help="Use this flag to determine where you want backups to be made or where they currently exist")
    parser.add_argument("--addBackupPaths", nargs="*", default=[], help="Use this flag to add files or folders to a new backup")
    parser.add_argument("--restore", default=False, action="store_true", help="Use this flag to restore the backups")
    parser.add_argument("--restoreDate", nargs="?", default=None, type=str, help="Use this flag in conjunction with --restore to choose the date to which to restore the files, needs to be in format DD/MM/YYYY")
    parser.add_argument("--restoreTime", nargs="?", default=None, type=str, help="Use this flag in conjunction with --restore to choose the date to which to restore the files, needs to be in format HH/MM/SS")
    parser.add_argument("--restoreLocation", nargs="?", default="", help="Use this flag to determine the location of the restored files when used in conjunction with --restore")
    parser.add_argument("--listBackups", default=False, action="store_true", help="Use this flag to get a list of backups and when they were in the backup location")
    parser.add_argument("--saveDefaults", default=False, action="store_true", help="Use this option to save your backups location and your restore location as default")
    args = parser.parse_args()
    
    JBackup = JBackup_Core(_backupPath=args.backupsLocation, _restoreLocation=args.restoreLocation)
    if args.listBackups:
        PrintBackupList( JBackup.GetListOfBackups() )

    if args.makeBackup:
        JBackup.UpdateBackup(_newPaths=args.addBackupPaths)
    elif args.restore:
        JBackup.GetBackupState(_date=args.restoreDate, _time=args.restoreTime)
        JBackup.RebuildFiles()
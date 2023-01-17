

class JDiffer:

    def __init__(self, _diffTool):
        self.m_diffTool = _diffTool

    '''Function to use difflib to diff two files contents'''
    def difflib_diff(self, _file1, _file2):
        import difflib
        Differ = difflib.Differ()
        out = list( Differ.compare( _file1, _file2 ))
        # Now we have our diff we need to produce a list of changes from this to be able to linearly go from one file to another
        changes = []
        index = 0
        for i in range( len(out) ):
            if out[i][:1] == "?":
                continue
            elif out[i][:1] == "-":
                changes.append({
                    "type": "deleteLine",
                    "lineNumber": index,
                    "content": out[i][2:]
                })
                index -= 1
            elif out[i][:1] == "+":
                if index + 1 == len(_file1):
                    changes.append({
                    "type": "appendLine",
                    "content": out[i][2:]
                    })
                else:
                    changes.append({
                        "type": "addLine",
                        "lineNumber": index,
                        "content": out[i][2:]
                    })
            index += 1
        return changes

    '''General diff function that will let you diff using different libraries and functions'''
    def Diff(self, _file1, _file2):
        if self.m_diffTool == "difflib":
            return self.difflib_diff( _file1, _file2 )
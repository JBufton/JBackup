

class JDiffer:

    def __init__(self, _diffTool):
        self.m_diffTool = _diffTool

    def difflib_diff(self, _file1, _file2):
        import difflib
        Differ = difflib.Differ()
        out = list( Differ.compare( _file1, _file2 ))
        # Now we have our diff we need to produce a list of changes from this
        changes = []
        for i in range( len(out) ):
            if out[i][:2] == "? ":
                continue
            elif out[i][:2] == "- ":
                changes.append({
                    "type": "deleteLine",
                    "lineNumber": i
                })
            elif out[i][:2] == "+ ":
                changes.append({
                    "type": "addLine",
                    "lineNumber": i
                })
        return changes

    def Diff(self, _file1, _file2):
        if self.m_diffTool == "difflib":
            return self.difflib_diff( _file1, _file2 )
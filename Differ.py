

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
            if out[i][:2] == "? ":
                continue
            elif out[i][:2] == "- ":
                changes.append({
                    "type": "deleteLine",
                    "lineNumber": index,
                    "content": out[i][2:]
                })
                index -= 1
            elif out[i][:2] == "+ ":
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

    '''WIP: a custom differ, doesn't work yet and is bad generally'''
    def customDiff_diff(self, _file1, _file2 ):
        temp_file1 = _file1
        temp_file2 = _file2
        changes = []
        index = 0
        while temp_file1 != temp_file2:
            print(f"index: {index}")
            print(f"oldfileLength: {len(temp_file1)}")
            print(f"newfileLength: {len(temp_file2)}")
            print(f"OldFile: {''.join(temp_file1)}")
            print(f"NewFile: {''.join(temp_file2)}")
            if index > len(temp_file1)-1 and index <= len(temp_file2)-1:
                # We've reached the end of file1 so we need to append the rest of the contents of file2 to file1
                for i in range(index, len(temp_file2)-1):
                    temp_file1.append(temp_file2[index + i])
                    changes.append({
                            "type": "appendLine",
                            "content": temp_file2[index + i]
                        })
                index += 1
                continue
            if index > len(temp_file2)-1 and index <= len(temp_file1)-1:
                # We've reached the end of file2 but there is still content in file1, this should be removed
                for i in range(index, len(temp_file1)-1):
                    del temp_file1[index]
                    changes.append({
                        "type": "deleteLine",
                        "lineNumber": index
                    })
                index += 1
                continue

            print(f"oldFileContent: {temp_file1[index]}")
            print(f"newFileContent: {temp_file2[index]}")
            if temp_file1[index] == temp_file2[index]:
                index += 1
                continue
            else:
                if temp_file1[index] in temp_file2[index:]:

                    while temp_file1[index] != temp_file2[index]:
                        temp_file1.insert(index, temp_file2[index])
                        changes.append({
                            "type": "addLine",
                            "lineNumber": index,
                            "content": temp_file2[index]

                        })
                else:
                    del temp_file1[index]
                    changes.append({
                        "type": "deleteLine",
                        "lineNumber": index
                    })
                    changes.append({
                        "type": "addLine",
                        "lineNumber": index,
                        "content": temp_file2[index]
                    })
            print(changes)
            index += 1
        print(temp_file1)
        print(temp_file2)
        return changes

    '''General diff function that will let you diff using different libraries and functions'''
    def Diff(self, _file1, _file2):
        if self.m_diffTool == "difflib":
            return self.difflib_diff( _file1, _file2 )
        if self.m_diffTool == "custom":
            return self.customDiff_diff( _file1, _file2)
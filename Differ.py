

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
                    "lineNumber": i,
                    "content": out[i][2:]
                })
        return changes

    def customDiff_diff(self, _file1, _file2 ):
        temp_file1 = _file1
        temp_file2 = _file2
        changes = []
        index = 0
        finished = False
        while not finished:
            print(f"index: {index}")
            print(f"oldfileLength: {len(temp_file1)}")
            print(f"newfileLength: {len(temp_file2)}")
            if index > len(temp_file1)-1 and index > len(temp_file2)-1:
                print( "Should be finishing")
                finished = True
                continue
            if index > len(temp_file1)-1 and index <= len(temp_file2)-1:
                # We've reached the end of file1 so we need to append the rest of the contents of file2 to file1
                temp_file1.append(temp_file2[index])
                changes.append({
                        "type": "appendLine",
                        "content": temp_file2[index]
                    })
                index += 1
                continue
            if index > len(temp_file2)-1 and index <= len(temp_file1)-1:
                # We've reached the end of file2 but there is still content in file1, this should be removed
                for i in range(index, len(temp_file1)):
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
                print(temp_file2[index:])
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
        return changes


    def Diff(self, _file1, _file2):
        if self.m_diffTool == "difflib":
            return self.difflib_diff( _file1, _file2 )
        if self.m_diffTool == "custom":
            return self.customDiff_diff( _file1, _file2)
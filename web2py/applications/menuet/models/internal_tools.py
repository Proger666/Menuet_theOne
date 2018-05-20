def checkIfExist(*args):
    '''Test if arguments are exists via len, etc None'''
    for arg in args:
        arg = str(arg.encode('utf-8'))
        if arg is None  or len(arg) == 0 or arg == '' or arg == " ":
            return False
        else:
            return True




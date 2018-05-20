def checkIfExist(*args):
    '''Test if arguments are exists via len, etc None'''
    for arg in args:
        if arg is None  or len(str(arg)) == 0 or arg == '' or arg == " ":
            return False
        else:
            return True




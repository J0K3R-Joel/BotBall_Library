class FileR:
    def __init__(self):
        print()

    def reader(self, file_name: str) -> str:
        try:
            with open(file_name, 'r') as f:
                return f.read()
        except Exception as e:
            print('File reader error: ', str(e))

    def writer(self, file_name: str, mode: str, msg: str) -> None:
        """Writing a message into the bias.txt file CCCCHHHHHAAAAAANNNNNGEEEEEEEEEEEEEE
            (The only purpose is to write the average bias into the file and getting it so you need not to calibrate it every time)

        Args:
            msg (str): writing the message into the bias.txt file

        Returns:
            None
        """
        try:
            with open(file_name, mode) as f:
                f.write(str(msg))
        except Exception as e:
            print('File writer error: ', str(e))

    def cleaner(self, file_name: str) -> None:
        try:
            open(file_name, 'w').close()
        except Exception as e:
            print('File cleaner error: ', str(e))

